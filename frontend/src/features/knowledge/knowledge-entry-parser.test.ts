import { describe, expect, it } from "vitest";
import { extractKnowledgeEntries, findMatchingKnowledgeEntries } from "./knowledge-entry-parser";

const glossary = "### XSC\n**含义：** 小升初（小学升初中）的拼音首字母。\n\n### MK\n**含义：** 密考，家长圈对非公开测试的称呼。\n\n### HD\n**含义：** 活动，家长圈对体验或交流活动的称呼。";

describe("knowledge entry parser", () => {
  it.each(["XSC", "MK", "HD"])("finds the %s term and explanation", (term) => {
    const entry = findMatchingKnowledgeEntries(glossary, term)[0];
    expect(entry.term).toBe(term);
    expect(entry.explanation.length).toBeGreaterThan(0);
  });

  it("extracts every glossary entry for the detail page", () => {
    expect(extractKnowledgeEntries(glossary).map((entry) => entry.term)).toEqual(["XSC", "MK", "HD"]);
  });
});
