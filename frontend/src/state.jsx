import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from "react";

const SessionContext = createContext(null);
const STORAGE_KEY = "metadataResult";

// The backend returns { TITLE, ABSTRACT, METADATA: { AUTHORS, EMAILS, AFFILIATIONS, KEYWORDS } }.
const list = (v) => {
  if (!v) return [];
  if (Array.isArray(v)) return v.map((x) => String(x).trim()).filter(Boolean);
  return String(v).split(/,|\n/).map((x) => x.trim()).filter(Boolean);
};

export function toRecord(raw) {
  const meta = (raw && raw.METADATA) || {};
  return {
    title: (raw && raw.TITLE) || "",
    authors: list(meta.AUTHORS),
    affiliations: list(meta.AFFILIATIONS),
    emails: list(meta.EMAILS),
    keywords: list(meta.KEYWORDS),
    abstract: (raw && raw.ABSTRACT) || "",
  };
}

function loadStored() {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    return stored ? toRecord(JSON.parse(stored)) : null;
  } catch {
    return null;
  }
}

export function SessionProvider({ children }) {
  const [record, setRecord] = useState(loadStored);
  const [file, setFile] = useState(null); // { name, url } - only lives until the page is reloaded
  const [version, setVersion] = useState(0); // bumps on every new extraction so the review form resets
  const fileRef = useRef(null);

  const startSession = useCallback((raw, nextFile) => {
    if (fileRef.current) URL.revokeObjectURL(fileRef.current.url);
    fileRef.current = nextFile;
    setFile(nextFile);
    setRecord(toRecord(raw));
    setVersion((v) => v + 1);
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(raw));
    } catch {
      /* storage unavailable: the record still lives in memory */
    }
  }, []);

  useEffect(() => () => fileRef.current && URL.revokeObjectURL(fileRef.current.url), []);

  return (
    <SessionContext.Provider value={{ record, file, version, startSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export const useSession = () => useContext(SessionContext);
