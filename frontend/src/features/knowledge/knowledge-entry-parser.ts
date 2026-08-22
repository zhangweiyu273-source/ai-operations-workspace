export type KnowledgeEntry = { term: string; explanation: string; body: string };

function plainText(value: string) {
  return value
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^>\s?/gm, "")
    .replace(/\[(.*?)\]\([^)]*\)/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

export function extractKnowledgeEntries(content: string): KnowledgeEntry[] {
  const sections = content.split(/^###\s+/m).slice(1);
  const entries = sections.map((section) => {
    const [heading = "", ...bodyLines] = section.split("\n");
    const body = bodyLines.join("\n").trim();
    const meaning = body.match(/\*\*含义：\*\*\s*([^\n]+)/)?.[1];
    return { term: plainText(heading), explanation: plainText(meaning || body).slice(0, 240), body: plainText(body) };
  }).filter((entry) => entry.term && entry.explanation);
  return entries.length ? entries : [{ term: "文档正文", explanation: plainText(content).slice(0, 240), body: plainText(content) }];
}

export function findMatchingKnowledgeEntries(content: string, search: string) {
  const keyword = search.trim().toLocaleLowerCase();
  if (!keyword) return [];
  return extractKnowledgeEntries(content).filter((entry) => `${entry.term} ${entry.explanation} ${entry.body}`.toLocaleLowerCase().includes(keyword));
}
