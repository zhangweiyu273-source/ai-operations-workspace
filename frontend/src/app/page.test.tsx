import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "./page";

describe("Home", () => {
  it("renders the workbench foundation state", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: "运营首页" })).toBeInTheDocument();
    expect(screen.getByText("数据底座已就绪")).toBeInTheDocument();
  });
});
