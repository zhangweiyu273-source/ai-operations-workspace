import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Sidebar, navigation } from "./sidebar";

const usePathname = vi.fn();
vi.mock("next/navigation", () => ({ usePathname: () => usePathname() }));

describe("Sidebar", () => {
  beforeEach(() => usePathname.mockReturnValue("/keywords"));

  it("renders only the enabled stage-B navigation items", () => {
    render(<Sidebar />);
    expect(screen.getAllByRole("link")).toHaveLength(navigation.length);
    expect(screen.queryByText("私域运营中心")).not.toBeInTheDocument();
    expect(screen.queryByText("用户洞察中心")).not.toBeInTheDocument();
  });

  it("marks the current route as active", () => {
    render(<Sidebar />);
    expect(screen.getByRole("link", { name: /关键词库/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
