import React from "react";
import { render, screen } from "@testing-library/react";
import HomePage from "../page";
import {
  it,
  expect,
  describe,
} from "vitest";

describe("Root HomePage", () => {
  it("renders heading", () => {
    render(<HomePage />);
    expect(screen.getByText("DeepResearch")).toBeDefined();
  });
});
