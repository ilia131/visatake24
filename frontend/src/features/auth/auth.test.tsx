// @vitest-environment jsdom

import { QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { post, queryClient } from "../../lib/api";
import { Login, Register } from "./auth";

vi.mock("../../lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/api")>();
  return { ...actual, post: vi.fn(), code: () => 401 };
});

const mockPost = vi.mocked(post);
afterEach(() => {
  cleanup();
  queryClient.clear();
  mockPost.mockReset();
});

function openForm(path: string) {
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/dashboard" element={<h1>داشبورد آزمایشی</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return userEvent.setup();
}

test("country search and selection, national input, validation, password visibility and login", async () => {
  const user = openForm("/auth/login");
  await user.click(screen.getByRole("button", { name: /ایران/ }));
  const search = screen.getByRole("searchbox");
  await user.type(search, "Canada");
  await user.clear(search);
  await user.type(search, "+1");
  expect(screen.getByRole("button", { name: /کانادا/ })).toBeTruthy();
  await user.clear(search);
  await user.type(search, "کانادا");
  await user.click(screen.getByRole("button", { name: /کانادا/ }));
  const phone = screen.getByRole("textbox", { name: /شماره تلفن/ }) as HTMLInputElement;
  expect(phone.parentElement?.textContent).toContain("+1");
  await user.type(phone, "x۱۲۳");
  expect(phone.value).toBe("123");
  const password = screen.getByLabelText("رمز عبور") as HTMLInputElement;
  await user.type(password, "test-password");
  await user.click(screen.getByRole("button", { name: "نمایش رمز عبور" }));
  expect(password.type).toBe("text");
  await user.click(screen.getByRole("button", { name: "مخفی کردن رمز عبور" }));
  expect(password.type).toBe("password");
  await user.click(screen.getByRole("button", { name: "ورود" }));
  expect(screen.getByRole("alert").textContent).toContain("معتبر نیست");
  expect(mockPost).not.toHaveBeenCalled();

  await user.clear(phone);
  await user.type(phone, "4165550123");
  mockPost.mockRejectedValueOnce(new Error("Unauthorized"))
    .mockResolvedValueOnce({ user: { id: 1, role: "customer" } });
  await user.click(screen.getByRole("button", { name: "ورود" }));
  expect((await screen.findByRole("alert")).textContent).toContain("نادرست است");
  await user.click(screen.getByRole("button", { name: "ورود" }));
  expect(await screen.findByText("داشبورد آزمایشی")).toBeTruthy();
  expect(mockPost).toHaveBeenLastCalledWith("/api/v1/auth/login/", {
    country_code: "CA", phone_number: "4165550123", password: "test-password",
  });
});

test("registration validates confirmation and posts names and credentials", async () => {
  const user = openForm("/auth/login");
  await user.click(screen.getByRole("link", { name: "ایجاد حساب" }));
  await user.type(screen.getByLabelText("نام", { exact: true }), "نیلوفر");
  await user.type(screen.getByLabelText("نام خانوادگی"), "کاوه");
  await user.type(screen.getByRole("textbox", { name: /شماره تلفن/ }), "09123456789");
  await user.type(screen.getByLabelText("رمز عبور", { exact: true }), "test-password");
  const confirmation = screen.getByLabelText("تکرار رمز عبور");
  await user.type(confirmation, "different");
  await user.click(screen.getByRole("button", { name: "ثبت‌نام" }));
  expect(screen.getByRole("alert").textContent).toContain("یکسان نیستند");
  expect(mockPost).not.toHaveBeenCalled();

  await user.clear(confirmation);
  await user.type(confirmation, "test-password");
  mockPost.mockResolvedValueOnce({ user: { id: 2, role: "customer" } });
  await user.click(screen.getByRole("button", { name: "ثبت‌نام" }));
  expect(await screen.findByText("داشبورد آزمایشی")).toBeTruthy();
  expect(mockPost).toHaveBeenCalledWith("/api/v1/auth/register/", {
    first_name: "نیلوفر", last_name: "کاوه", country_code: "IR", phone_number: "09123456789",
    password: "test-password", password_confirmation: "test-password",
  });
});
