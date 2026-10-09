import React from "react";

export default function About() {
  return (
    <article className="wrap prose">
      <h1>About Metadata Extractor</h1>
      <p className="lede">
        Library catalogues, citation managers and archives all need clean metadata, and typing it in from the first
        page of every paper is slow. This tool reads it for you and keeps you in charge of what gets saved.
      </p>

      <h2>How extraction works</h2>
      <p>
        The server sends your PDF to GROBID, an open-source machine-learning parser for scholarly documents. GROBID
        returns the paper as structured XML, with each author connected to their affiliation and email. Pattern
        matching on the body text recovers the abstract, keywords or title when GROBID leaves them blank.
      </p>
      <p>
        If GROBID is unavailable, or the PDF has no text layer, the server falls back to the original pipeline: a
        DocLayout-YOLO model finds the title, author and abstract regions on the first page, Tesseract reads each
        region, and a rule-based parser sorts the text into fields.
      </p>

      <h2>How accurate it is</h2>
      <p>
        On 100 sample papers, checked against OpenAlex and Crossref records, GROBID with pattern matching got the
        title exactly right for 94% of papers and scored an author F1 of 0.95. The original OCR pipeline scored 0.61
        on authors. Scanned PDFs have not been measured.
      </p>

      <h2>Why you still review it</h2>
      <p>
        About one author list in five came out incomplete or wrong in testing. The review screen shows the paper
        beside the extracted fields so you can catch those quickly, and you confirm each field before exporting.
      </p>
    </article>
  );
}
