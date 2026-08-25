import React from "react";
import { render, screen } from "@testing-library/react";
import HomePage from "../page";
import { it, expect, describe, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

describe("Root HomePage", () => {
  it("renders heading", () => {
    render(<HomePage />);
    expect(screen.getByText("DeepResearch")).toBeDefined();
  });
});
