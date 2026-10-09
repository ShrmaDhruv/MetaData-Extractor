// Field definitions shared by the review screen and the exporters.
// `kind` decides how a field is edited and shown once confirmed.
export const FIELDS = [
  { key: "title", label: "Title", kind: "text", hint: "" },
  { key: "authors", label: "Authors", kind: "chips", hint: "Separate names with commas." },
  { key: "affiliations", label: "Affiliations", kind: "lines", hint: "One affiliation per line." },
  { key: "emails", label: "Emails", kind: "chips", hint: "Separate addresses with commas." },
  { key: "keywords", label: "Keywords", kind: "chips", hint: "Separate keywords with commas." },
  { key: "abstract", label: "Abstract", kind: "long", hint: "" },
];

const splitList = (text, sep) =>
  text
    .split(sep)
    .map((x) => x.trim())
    .filter(Boolean);

// record value -> editable string
export function toDraft(field, value) {
  if (field.kind === "chips") return (value || []).join(", ");
  if (field.kind === "lines") return (value || []).join("\n");
  return value || "";
}

// editable string -> record value
export function fromDraft(field, text) {
  if (field.kind === "chips") return splitList(text, /,|\n/);
  if (field.kind === "lines") return splitList(text, /\n/);
  return text.trim();
}

export function draftsToRecord(drafts) {
  const out = {};
  FIELDS.forEach((f) => {
    out[f.key] = fromDraft(f, drafts[f.key] || "");
  });
  return out;
}
