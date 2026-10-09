import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useSession } from "../state";
import { FIELDS, toDraft, draftsToRecord } from "../lib/fields";
import { exportJson, exportPdf } from "../lib/export";
import FieldEditor from "../components/FieldEditor";

function Empty() {
  return (
    <div className="wrap prose">
      <h1>Nothing to review yet</h1>
      <p className="lede">Upload a PDF first. The extracted fields will appear here next to the paper.</p>
      <Link to="/" className="btn btn--primary">
        Upload a paper
      </Link>
    </div>
  );
}

function Workbench({ record, file }) {
  const [drafts, setDrafts] = useState(() =>
    Object.fromEntries(FIELDS.map((f) => [f.key, toDraft(f, record[f.key])]))
  );
  const [confirmed, setConfirmed] = useState({});
  const [showSource, setShowSource] = useState(true);

  const total = FIELDS.length;
  const done = FIELDS.filter((f) => confirmed[f.key]).length;
  const allDone = done === total;
  const current = draftsToRecord(drafts);
  const hasSource = Boolean(file);

  const setConfirm = (key, value) => setConfirmed((c) => ({ ...c, [key]: value }));
  const confirmAll = () => setConfirmed(Object.fromEntries(FIELDS.map((f) => [f.key, true])));

  return (
    <div className={`bench wrap${hasSource && showSource ? " bench--split" : ""}`}>
      {hasSource && showSource && (
        <aside className="source" aria-label="Source paper">
          <div className="source__bar">
            <p title={file.name}>{file.name}</p>
            <a href={file.url} target="_blank" rel="noopener noreferrer">
              Open in new tab
            </a>
          </div>
          <iframe title={`Source PDF: ${file.name}`} src={`${file.url}#page=1&view=FitH`} />
        </aside>
      )}

      <div className="record">
        <div className="record__bar">
          <div className="progress" role="status" aria-live="polite">
            <p>
              <strong>{done}</strong> of {total} fields confirmed
            </p>
            <div className="progress__track" aria-hidden="true">
              <div className="progress__fill" style={{ width: `${(done / total) * 100}%` }} />
            </div>
          </div>
          <div className="record__actions">
            {hasSource && (
              <button type="button" className="btn btn--quiet" onClick={() => setShowSource((s) => !s)}>
                {showSource ? "Hide paper" : "Show paper"}
              </button>
            )}
            {!allDone && (
              <button type="button" className="btn" onClick={confirmAll}>
                Confirm all
              </button>
            )}
          </div>
        </div>

        {!hasSource && (
          <p className="notice">
            The paper preview is only available right after an upload. Reloading the page clears it, but your
            extracted fields are kept.
          </p>
        )}

        <h1 className="sr-only">Review extracted metadata</h1>

        {FIELDS.map((f) => (
          <FieldEditor
            key={f.key}
            field={f}
            draft={drafts[f.key]}
            confirmed={Boolean(confirmed[f.key])}
            onChange={(v) => setDrafts((d) => ({ ...d, [f.key]: v }))}
            onConfirm={() => setConfirm(f.key, true)}
            onEdit={() => setConfirm(f.key, false)}
          />
        ))}

        <section className="export" aria-labelledby="export-h">
          <h2 id="export-h">Export</h2>
          <p className="muted">
            {allDone
              ? "Every field is confirmed. Download the record in the format you need."
              : `Confirm the remaining ${total - done} ${total - done === 1 ? "field" : "fields"} to enable export.`}
          </p>
          <div className="export__row">
            <button type="button" className="btn btn--primary" disabled={!allDone} onClick={() => exportPdf(current, file && file.name)}>
              Download PDF
            </button>
            <button type="button" className="btn" disabled={!allDone} onClick={() => exportJson(current, file && file.name)}>
              Download JSON
            </button>
            <Link to="/" className="btn btn--quiet">
              Extract another paper
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

export default function Review() {
  const { record, file, version } = useSession();
  if (!record) return <Empty />;
  // key resets all draft/confirmed state whenever a new paper is extracted
  return <Workbench key={version} record={record} file={file} />;
}
