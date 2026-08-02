import { render, screen } from "@testing-library/react";
import HomePage from "../page";
import {
  it,
  expect,
  describe,
} from "vitest";
import "@testing-library/jest-dom"; // for toBeInTheDocument

describe("Root HomePage", () => {
  it("renders the heading successfully", () => {
    render(<HomePage />);
    expect(screen.getByText("DeepResearch")).toBeDefined();
  });
  it("renders the dashboard link", () => {
    render(<HomePage />);
    expect(screen.getByText("Go to Dashboard")).toBeDefined();
  });
});
