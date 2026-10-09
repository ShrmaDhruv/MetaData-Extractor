import React from "react";
import UploadPanel from "../components/UploadPanel";
import Specimen from "../components/Specimen";

const STEPS = [
  { title: "Upload the PDF", text: "Drop in a paper. There is nothing to configure." },
  { title: "Check each field", text: "The paper sits next to the extracted record. Fix anything that is wrong and confirm it." },
  { title: "Export", text: "Once every field is confirmed, download the record as a PDF or JSON." },
];

export default function Home() {
  return (
    <>
      <section className="hero wrap">
        <div className="hero__copy">
          <h1>Check a paper's metadata against the paper itself.</h1>
          <p className="lede">
            Upload a research PDF. We read out the title, authors, affiliations, emails, keywords and abstract.
            You review each one beside the original and confirm it.
          </p>
          <UploadPanel />
        </div>
        <div className="hero__aside">
          <Specimen />
        </div>
      </section>

      <section className="band">
        <div className="wrap steps">
          <h2>How a paper moves through</h2>
          <ol>
            {STEPS.map((s, i) => (
              <li key={s.title}>
                <span className="steps__n" aria-hidden="true">{i + 1}</span>
                <div>
                  <h3>{s.title}</h3>
                  <p>{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="wrap engine">
        <h2>What does the reading</h2>
        <div className="engine__cols">
          <p>
            Papers are parsed by GROBID, a trained model for scholarly PDFs. It keeps authors linked to their
            affiliations and copes with two-column layouts. When it leaves the title, abstract or keywords empty,
            pattern matching on the paper's text fills the gap.
          </p>
          <p>
            If a file has no readable text, such as a scan, the first page is split into layout regions and read with
            OCR instead. Either way, nothing is final until you confirm it.
          </p>
        </div>
      </section>
    </>
  );
}
