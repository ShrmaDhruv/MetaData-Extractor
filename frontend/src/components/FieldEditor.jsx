import React from "react";
import { fromDraft } from "../lib/fields";

// One field of the record: editable until confirmed, then shown as plain text.
export default function FieldEditor({ field, draft, confirmed, onChange, onConfirm, onEdit }) {
  const id = `field-${field.key}`;
  const value = fromDraft(field, draft);
  const empty = field.kind === "chips" || field.kind === "lines" ? value.length === 0 : value === "";

  const rows = field.kind === "long" ? 9 : field.kind === "lines" ? 4 : field.kind === "chips" ? 3 : 2;
  const multiline = true;

  return (
    <section className={`field${confirmed ? " is-confirmed" : ""}${empty && !confirmed ? " is-empty" : ""}`} aria-labelledby={`${id}-label`}>
      <header className="field__head">
        <h3 id={`${id}-label`}>
          <label htmlFor={confirmed ? undefined : id}>{field.label}</label>
        </h3>
        {confirmed ? (
          <span className="status status--ok">
            <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            Confirmed
          </span>
        ) : empty ? (
          <span className="status status--warn">Not found</span>
        ) : (
          <span className="status">To check</span>
        )}
      </header>

      {confirmed ? (
        <div className="field__value">
          {empty ? (
            <p className="muted">Confirmed as empty.</p>
          ) : field.kind === "chips" ? (
            <ul className="chips">
              {value.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
          ) : field.kind === "lines" ? (
            <ul className="lines">
              {value.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
          ) : (
            <p className={field.kind === "text" ? "field__title" : "field__abstract"}>{value}</p>
          )}
          <button type="button" className="btn btn--quiet" onClick={onEdit}>
            Edit {field.label.toLowerCase()}
          </button>
        </div>
      ) : (
        <div className="field__edit">
          {multiline ? (
            <textarea
              id={id}
              rows={rows}
              value={draft}
              onChange={(e) => onChange(e.target.value)}
              aria-describedby={field.hint ? `${id}-hint` : undefined}
            />
          ) : (
            <input
              id={id}
              type="text"
              value={draft}
              onChange={(e) => onChange(e.target.value)}
              aria-describedby={field.hint ? `${id}-hint` : undefined}
            />
          )}
          {field.hint && (
            <p id={`${id}-hint`} className="hint">
              {field.hint}
            </p>
          )}
          {empty && <p className="hint hint--warn">Nothing was found for this field. Add it from the paper, or confirm it as empty.</p>}
          <button type="button" className="btn btn--primary" onClick={onConfirm}>
            Confirm {field.label.toLowerCase()}
          </button>
        </div>
      )}
    </section>
  );
}
