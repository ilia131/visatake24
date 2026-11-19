from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import BytesIO
from threading import Barrier
from unittest.mock import patch
from urllib.parse import urlsplit

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.utils import timezone
from PIL import Image
from pypdf import PdfWriter
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.appointments.models import Appointment, ConsultantAvailability
from apps.appointments.services.notifications import appointment_event
from apps.consultants.models import Consultant

ROOT = "/api/v1/appointments/"
pytestmark = pytest.mark.django_db


@pytest.fixture
def scenario(django_user_model, settings, tmp_path):
    settings.APPOINTMENT_RECEIPT_ROOT = tmp_path / "private"
    settings.APPOINTMENT_PAYMENT_CARD = "0000000000000000"
    owner, stranger, consultant, other_consultant, admin = [
        django_user_model.objects.create_user(
            phone_number=f"+98910000000{index}", is_staff=(index == 4),
            first_name=f"User {index}",
        )
        for index in range(5)
    ]
    profile, _ = [
        Consultant.objects.create(
            user=user, full_name=f"Consultant {index}", slug=f"consultant-{index}",
            is_verified=True, consultation_fee=750000,
        )
        for index, user in enumerate([consultant, other_consultant])
    ]
    slot = ConsultantAvailability.objects.create(
        consultant=profile, start_at=timezone.now() + timedelta(days=2),
        end_at=timezone.now() + timedelta(days=2, hours=1),
    )
    return owner, stranger, consultant, other_consultant, admin, slot


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def book(user, slot, **data):
    return client_for(user).post(ROOT, {"availability_id": slot.pk, **data}, format="json")


def path(pk, action="", prefix=""):
    return f"{ROOT}{prefix}{pk}/{action}"


def png():
    output = BytesIO()
    Image.new("RGB", (3, 3)).save(output, format="PNG")
    return output.getvalue()


def receipt(client, pk, data=None, name="receipt.png"):
    data = png() if data is None else data
    return client.post(path(pk, "payment-receipt/"), {
        "payment_receipt": SimpleUploadedFile(name, data),
    }, format="multipart")


@pytest.fixture
def approved(scenario):
    owner, _, consultant, _, _, slot = scenario
    pk = book(owner, slot).data["id"]
    response = client_for(consultant).post(path(pk, "approve/", "consultant/"))
    assert response.status_code == 200
    return pk


def test_fee_snapshot_and_ignored_user_fields(scenario, settings):
    owner, stranger, consultant, other_consultant, _, slot = scenario
    profile = client_for(owner).get(f"/api/v1/consultants/{slot.consultant.slug}/")
    assert profile.data["consultation_fee"] == "750000"
    result = book(owner, slot, consultation_fee="1", status="confirmed", user_note="سلام")
    assert result.status_code == 201
    pk = result.data["id"]
    assert result.data["status"] == "pending"
    assert result.data["consultation_fee"] == "750000"
    assert settings.APPOINTMENT_PAYMENT_CARD not in result.content.decode()
    slot.consultant.consultation_fee = 5
    slot.consultant.save()
    assert client_for(owner).get(path(pk)).data["consultation_fee"] == "750000"
    assert client_for(owner).patch(path(pk), {"status": "confirmed"}).status_code == 405
    assert client_for(stranger).get(ROOT).data == []
    assert client_for(stranger).get(path(pk)).status_code == 404
    assert client_for(consultant).get(ROOT + "consultant/?status=pending").data["count"] == 1
    assert client_for(other_consultant).get(ROOT + "consultant/").data["count"] == 0
    assert client_for(other_consultant).get(path(pk, prefix="consultant/")).status_code == 404
    assert client_for(other_consultant).post(path(pk, "approve/", "consultant/")).status_code == 404
    assert receipt(client_for(owner), pk).status_code == 400


def test_consultant_reject_and_slot_release(scenario):
    owner, stranger, consultant, _, _, slot = scenario
    pk = book(owner, slot).data["id"]
    client = client_for(consultant)
    assert client.post(path(pk, "reject/", "consultant/"), {}).status_code == 400
    response = client.post(path(pk, "reject/", "consultant/"), {"rejection_reason": "در دسترس نیستم"})
    assert response.data["status"] == "rejected"
    assert response.data["rejection_reason"] == "در دسترس نیستم"
    assert client.post(path(pk, "approve/", "consultant/")).status_code == 400
    assert book(stranger, slot).status_code == 201


def test_full_workflow_and_private_download(scenario, approved, settings, django_capture_on_commit_callbacks):
    owner, stranger, consultant, _, admin, slot = scenario
    client = client_for(owner)
    reviewer = client_for(admin)
    assert client.get(path(approved)).data["status"] == "awaiting_payment"
    assert client.get(path(approved)).data["payment_card"] == settings.APPOINTMENT_PAYMENT_CARD
    assert client_for(consultant).get(path(approved, prefix="consultant/")).data["payment_card"] is None
    assert book(stranger, slot).status_code == 400
    assert receipt(client_for(stranger), approved).status_code == 404
    response = receipt(client, approved)
    assert response.status_code == 200
    assert response.data["status"] == "payment_submitted"
    assert response.data["payment_card"] == settings.APPOINTMENT_PAYMENT_CARD
    assert reviewer.get(ROOT + "admin/payments/").data["count"] == 1
    detail = reviewer.get(path(approved, prefix="admin/payments/")).data
    assert detail["applicant_name"] == owner.get_full_name()
    assert detail["payment_submitted_at"]
    download = urlsplit(detail["payment_receipt_url"]).path
    stored = Appointment.objects.get(pk=approved).payment_receipt
    assert stored.name not in response.content.decode()
    with pytest.raises(ValueError):
        _ = stored.url
    assert APIClient().get(download).status_code == 401
    assert client_for(stranger).get(download).status_code == 404
    for allowed in [client, reviewer, client_for(consultant)]:
        file_response = allowed.get(download)
        assert file_response.status_code == 200
        assert b"".join(file_response.streaming_content) == png()
    approve_url = path(approved, "approve/", "admin/payments/")
    assert client_for(owner).post(approve_url).status_code == 403
    assert client_for(consultant).post(approve_url).status_code == 403
    with patch.object(appointment_event, "send_robust") as notify:
        with django_capture_on_commit_callbacks(execute=True):
            response = reviewer.post(approve_url)
        notify.assert_called_once()
        assert notify.call_args.kwargs["event"] == "confirmed"
    assert response.data["status"] == "confirmed"
    assert response.data["confirmed_at"]
    assert response.data["payment_reviewed_by"] == admin.pk
    assert reviewer.post(approve_url).status_code == 400
    assert reviewer.get(ROOT + "admin/payments/").data["count"] == 0
    assert book(stranger, slot).status_code == 400
    complete_url = path(approved, "complete/", "consultant/")
    assert client_for(consultant).post(complete_url).status_code == 400
    ConsultantAvailability.objects.filter(pk=slot.pk).update(
        start_at=timezone.now() - timedelta(hours=2), end_at=timezone.now() - timedelta(hours=1),
    )
    assert client_for(consultant).post(complete_url).data["status"] == "completed"
    assert list(Appointment.objects.get(pk=approved).history.values_list("new_status", flat=True)) == [
        "pending", "awaiting_payment", "payment_submitted", "confirmed", "completed",
    ]


@pytest.mark.parametrize(("name", "content"), [
    ("invalid.png", b"<html>"),
    ("invalid.pdf", b"%PDF-1.7\n%%EOF"),
    ("invalid.svg", b"<svg/>"),
    ("oversized.png", b"x" * (5 * 1024 * 1024 + 1)),
])
def test_invalid_receipts(scenario, approved, name, content):
    response = receipt(client_for(scenario[0]), approved, content, name)
    assert response.status_code == 400
    assert Appointment.objects.get(pk=approved).status == "awaiting_payment"


def test_payment_rejection_and_safe_replacement(scenario, approved, django_capture_on_commit_callbacks):
    owner, _, _, _, admin, _ = scenario
    client = client_for(owner)
    assert receipt(client, approved).status_code == 200
    old_file = Appointment.objects.get(pk=approved).payment_receipt
    result = client_for(admin).post(path(approved, "reject/", "admin/payments/"), {"payment_note": "مبلغ اشتباه است"})
    assert result.data["status"] == "payment_rejected"
    assert result.data["payment_note"] == "مبلغ اشتباه است"
    assert client.get(ROOT + "availability/").data
    output = BytesIO()
    pdf = PdfWriter()
    pdf.add_blank_page(width=100, height=100)
    pdf.write(output)
    with django_capture_on_commit_callbacks(execute=True):
        replacement = receipt(client, approved, output.getvalue(), "replacement.pdf")
    assert replacement.status_code == 200
    assert replacement.data["payment_note"] == ""
    assert replacement.data["payment_reviewed_at"] is None
    assert not old_file.storage.exists(old_file.name)


def test_rebook_after_rejection_prevents_old_receipt_submission(scenario, approved):
    owner, stranger, _, _, admin, slot = scenario
    assert receipt(client_for(owner), approved).status_code == 200
    client_for(admin).post(path(approved, "reject/", "admin/payments/"), {"payment_note": "رد شد"})
    assert book(stranger, slot).status_code == 201
    assert receipt(client_for(owner), approved).status_code == 400
    assert Appointment.objects.get(pk=approved).status == "payment_rejected"


def test_cancellation_releases_slot(scenario):
    owner, stranger, _, _, _, slot = scenario
    pk = book(owner, slot).data["id"]
    assert book(stranger, slot).status_code == 400
    assert client_for(stranger).post(path(pk, "cancel/")).status_code == 404
    assert client_for(owner).post(path(pk, "cancel/")).data["status"] == "cancelled"
    assert Appointment.objects.get(pk=pk).history.last().new_status == "cancelled"
    assert book(stranger, slot).status_code == 201


def test_slot_in_past_cannot_be_approved(scenario):
    owner, _, consultant, _, _, slot = scenario
    pk = book(owner, slot).data["id"]
    ConsultantAvailability.objects.filter(pk=slot.pk).update(start_at=timezone.now() - timedelta(minutes=1))
    assert client_for(consultant).post(path(pk, "approve/", "consultant/")).status_code == 400


def test_jwt_cookie_requires_csrf(scenario, settings):
    owner, _, _, _, _, slot = scenario
    client = APIClient(enforce_csrf_checks=True)
    client.cookies[settings.JWT_ACCESS_COOKIE] = str(AccessToken.for_user(owner))
    assert client.get(ROOT).status_code == 200
    assert client.post(ROOT, {"availability_id": slot.pk}).status_code == 403
    from django.middleware.csrf import _get_new_csrf_string

    csrf = _get_new_csrf_string()
    client.cookies[settings.CSRF_COOKIE_NAME] = csrf
    assert client.post(ROOT, {"availability_id": slot.pk}, HTTP_X_CSRFTOKEN=csrf).status_code == 201


@pytest.mark.django_db(transaction=True)
def test_postgresql_concurrent_booking(scenario):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL is required to exercise row-level locks.")
    owner, stranger, _, _, _, slot = scenario
    barrier = Barrier(2, timeout=5)

    def attempt(user):
        close_old_connections()
        try:
            barrier.wait()
            return book(user, slot).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(attempt, [owner, stranger])) == [201, 400]
    assert Appointment.objects.filter(availability=slot).count() == 1

@pytest.mark.parametrize("occupying_status", [
    Appointment.Status.PENDING,
    Appointment.Status.AWAITING_PAYMENT,
    Appointment.Status.PAYMENT_SUBMITTED,
    Appointment.Status.CONFIRMED,
])
def test_database_constraint_covers_each_occupying_status(scenario, occupying_status):
    owner, stranger, _, _, _, slot = scenario
    Appointment.objects.create(user=owner, availability=slot, status=occupying_status)
    with pytest.raises(IntegrityError), transaction.atomic():
        Appointment.objects.create(user=stranger, availability=slot)


def test_failed_receipt_history_rolls_back_file_and_status(scenario, approved, settings):
    owner = scenario[0]
    with patch("apps.appointments.services.booking._record_change", side_effect=RuntimeError):
        with pytest.raises(RuntimeError):
            receipt(client_for(owner), approved)
    appointment = Appointment.objects.get(pk=approved)
    assert appointment.status == Appointment.Status.AWAITING_PAYMENT
    assert not appointment.payment_receipt
    assert not list(settings.APPOINTMENT_RECEIPT_ROOT.iterdir())
