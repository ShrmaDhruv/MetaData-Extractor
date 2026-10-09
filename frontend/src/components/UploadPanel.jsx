import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import { apiUrl } from "../api";
import { useSession } from "../state";

async function readJson(res) {
  try {
    return await res.json();
  } catch {
    return {};
  }
}

export default function UploadPanel() {
  const navigate = useNavigate();
  const { startSession } = useSession();
  const [stage, setStage] = useState("idle"); // idle | uploading | extracting | error
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");

  const run = useCallback(
    async (file) => {
      setFileName(file.name);
      setError("");
      setStage("uploading");
      try {
        const body = new FormData();
        body.append("file", file);
        const up = await fetch(apiUrl("/upload/"), { method: "POST", body });
        const upData = await readJson(up);
        if (!up.ok) throw new Error(upData.detail || `The upload failed (status ${up.status}).`);

        setStage("extracting");
        const res = await fetch(apiUrl(`/process/?filename=${encodeURIComponent(upData.filename)}`));
        const data = await readJson(res);
        if (!res.ok || data.error) {
          throw new Error(data.detail || data.error || `Extraction failed (status ${res.status}).`);
        }

        startSession(data, { name: file.name, url: URL.createObjectURL(file) });
        navigate("/review");
      } catch (err) {
        setError(
          err instanceof TypeError
            ? "Could not reach the server. Check that the backend is running, then try again."
            : err.message
        );
        setStage("error");
      }
    },
    [navigate, startSession]
  );

  const onDrop = useCallback(
    (accepted, rejected) => {
      if (rejected.length) {
        setError("That file is not a PDF. Choose a .pdf file.");
        setStage("error");
        return;
      }
      if (accepted[0]) run(accepted[0]);
    },
    [run]
  );

  const busy = stage === "uploading" || stage === "extracting";
  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
    noClick: true,
    disabled: busy,
    onDrop,
  });

  return (
    <div className="upload">
      <div
        {...getRootProps({
          className: `dropzone${isDragActive ? " is-active" : ""}`,
        })}
      >
        <input {...getInputProps()} />
        {busy ? (
          <div role="status" aria-live="polite" className="dropzone__busy">
            <span className="spinner" aria-hidden="true" />
            <p className="dropzone__main">
              {stage === "uploading" ? "Uploading" : "Reading"} {fileName}
            </p>
            <p className="dropzone__sub">
              {stage === "uploading"
                ? "Sending the file to the server."
                : "Looking for the title, authors, affiliations and abstract. This usually takes a few seconds."}
            </p>
          </div>
        ) : (
          <>
            <svg className="dropzone__icon" viewBox="0 0 48 48" aria-hidden="true">
              <path d="M12 4h17l9 9v31H12z" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
              <path d="M29 4v9h9" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
              <path d="M18 24h12M18 30h12M18 36h7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
            <p className="dropzone__main">
              {isDragActive ? "Drop the PDF to start" : "Drop a research paper here"}
            </p>
            <p className="dropzone__sub">PDF files only. Metadata comes from the first page.</p>
            <button type="button" className="btn btn--primary" onClick={open}>
              Choose a PDF
            </button>
          </>
        )}
      </div>

      {stage === "error" && (
        <p role="alert" className="notice notice--error">
          {error}
        </p>
      )}
    </div>
  );
}
