import { jsPDF } from "jspdf";

function stem(name) {
  return (name || "metadata").replace(/\.pdf$/i, "").replace(/[^\w.-]+/g, "_").slice(0, 60) || "metadata";
}

function save(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function exportJson(record, sourceName) {
  const body = JSON.stringify(
    {
      TITLE: record.title,
      ABSTRACT: record.abstract,
      METADATA: {
        AUTHORS: record.authors,
        AFFILIATIONS: record.affiliations,
        EMAILS: record.emails,
        KEYWORDS: record.keywords,
      },
    },
    null,
    2
  );
  save(new Blob([body], { type: "application/json" }), `${stem(sourceName)}.metadata.json`);
}

export function exportPdf(record, sourceName) {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const margin = 18;
  const width = doc.internal.pageSize.getWidth() - margin * 2;
  const bottom = doc.internal.pageSize.getHeight() - margin;
  let y = margin;

  const write = (text, { size = 11, bold = false, gap = 1.5 } = {}) => {
    doc.setFont("helvetica", bold ? "bold" : "normal");
    doc.setFontSize(size);
    const lineHeight = size * 0.5;
    doc.splitTextToSize(text, width).forEach((line) => {
      if (y + lineHeight > bottom) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += lineHeight;
    });
    y += gap;
  };

  write(record.title || "Untitled", { size: 16, bold: true, gap: 6 });

  const section = (label, value) => {
    write(label, { size: 10, bold: true, gap: 0.5 });
    write(value || "Not provided", { gap: 5 });
  };

  section("Authors", record.authors.join(", "));
  section("Affiliations", record.affiliations.join("\n"));
  section("Emails", record.emails.join(", "));
  section("Keywords", record.keywords.join(", "));
  section("Abstract", record.abstract);

  doc.save(`${stem(sourceName)}.metadata.pdf`);
}
