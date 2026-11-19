
from django.core.management.base import BaseCommand
from apps.visas.models import Country


COUNTRIES = [
    {
        "name": "آلمان",
        "name_en": "Germany",
        "slug": "germany",
        "flag": "🇩🇪",
        "description": "درخواست ویزای آلمان",
    },
    {
        "name": "کانادا",
        "name_en": "Canada",
        "slug": "canada",
        "flag": "🇨🇦",
        "description": "درخواست ویزای کانادا",
    },
    {
        "name": "آمریکا",
        "name_en": "United States",
        "slug": "united-states",
        "flag": "🇺🇸",
        "description": "درخواست ویزای آمریکا",
    },
    {
        "name": "انگلیس",
        "name_en": "United Kingdom",
        "slug": "united-kingdom",
        "flag": "🇬🇧",
        "description": "درخواست ویزای انگلیس",
    },
    {
        "name": "فرانسه",
        "name_en": "France",
        "slug": "france",
        "flag": "🇫🇷",
        "description": "درخواست ویزای فرانسه",
    },
    {
        "name": "ترکیه",
        "name_en": "Turkey",
        "slug": "turkey",
        "flag": "🇹🇷",
        "description": "اطلاعات سفر و ویزای ترکیه",
    },
    {
        "name": "ایتالیا",
        "name_en": "Italy",
        "slug": "italy",
        "flag": "🇮🇹",
        "description": "درخواست ویزای ایتالیا",
    },
    {
        "name": "اسپانیا",
        "name_en": "Spain",
        "slug": "spain",
        "flag": "🇪🇸",
        "description": "درخواست ویزای اسپانیا",
    },
    {
        "name": "هلند",
        "name_en": "Netherlands",
        "slug": "netherlands",
        "flag": "🇳🇱",
        "description": "درخواست ویزای هلند",
    },
    {
        "name": "امارات",
        "name_en": "United Arab Emirates",
        "slug": "united-arab-emirates",
        "flag": "🇦🇪",
        "description": "درخواست ویزای امارات",
    },
]


class Command(BaseCommand):
    help = "Create or update initial visa destination countries"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for country_data in COUNTRIES:
            _, created = Country.objects.update_or_create(
                slug=country_data["slug"],
                defaults={
                    **country_data,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Countries seeded successfully. "
                f"Created: {created_count}, Updated: {updated_count}"
            )
        )
