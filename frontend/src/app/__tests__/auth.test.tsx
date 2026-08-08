import React from "react";
import { render, screen } from "@testing-library/react";
import LoginPage from "../(auth)/login/page";
import RegisterPage from "../(auth)/register/page";
import {
  it,
  expect,
  describe,
  vi,
} from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("Auth Pages", () => {
  it("renders login focused", () => {
    render(<LoginPage />);
    expect(screen.getByText("Welcome Back")).toBeDefined();
  });

  it("renders register focused", () => {
    render(<RegisterPage />);
    expect(screen.getByText("Create an Account")).toBeDefined();
  });
});
