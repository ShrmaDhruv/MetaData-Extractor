import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { jsPDF } from 'jspdf';
const fadeIn = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function Process() {
  const location = useLocation();
  const navigate = useNavigate();
  const raw = location.state?.content || {};

  // --- 1. Data Parsing ---
  let parsed = raw;
  if (typeof raw === "string") {
    try {
      parsed = JSON.parse(raw.replace(/'/g, '"'));
    } catch {
      parsed = {};
    }
  }

  // --- 2. Helper to Normalize Lists ---
  const normalize = (v) => {
    if (!v) return [];
    if (Array.isArray(v)) return v.map((x) => x.trim()).filter(Boolean);
    if (typeof v === "string")
      return v
        .split(/,|\n/)
        .map((x) => x.trim())
        .filter(Boolean);
    return [];
  };

  // --- 3. Initial State Setup ---
  const [data, setData] = useState(parsed);
  const meta = data.METADATA || {};

  // Input States
  const [authorInput, setAuthorInput] = useState(normalize(meta.AUTHORS).join(", "));
  const [emailInput, setEmailInput] = useState(normalize(meta.EMAILS).join(", "));
  const [affInput, setAffInput] = useState(normalize(meta.AFFILIATIONS).join("\n"));
  const [keyInput, setKeyInput] = useState(normalize(meta.KEYWORDS).join(", "));

  // Locking State
  const [locked, setLocked] = useState({
    authors: false,
    emails: false,
    affiliations: false,
    keywords: false,
  });

  // --- 4. Save & Lock Functions ---
  const saveAuthors = () => {
    setData((p) => ({
      ...p,
      METADATA: { ...p.METADATA, AUTHORS: normalize(authorInput) },
    }));
    setLocked((prev) => ({ ...prev, authors: true }));
  };

  const saveEmails = () => {
    setData((p) => ({
      ...p,
      METADATA: { ...p.METADATA, EMAILS: normalize(emailInput) },
    }));
    setLocked((prev) => ({ ...prev, emails: true }));
  };

  const saveAffs = () => {
    setData((p) => ({
      ...p,
      METADATA: { ...p.METADATA, AFFILIATIONS: normalize(affInput) },
    }));
    setLocked((prev) => ({ ...prev, affiliations: true }));
  };

  const saveKeys = () => {
    setData((p) => ({
      ...p,
      METADATA: { ...p.METADATA, KEYWORDS: normalize(keyInput) },
    }));
    setLocked((prev) => ({ ...prev, keywords: true }));
  };

  // Sidebar Preview Helpers
  const previewAuthors = normalize(data.METADATA?.AUTHORS);
  const previewEmails = normalize(data.METADATA?.EMAILS);
  const previewAffiliations = normalize(data.METADATA?.AFFILIATIONS);
  const previewKeywords = normalize(data.METADATA?.KEYWORDS);

  // Styles
  const buttonClass =
    "mt-3 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm";

  // Style for the final P tag (looks like read-only text)
  const pTagClass = "w-full p-3 bg-gray-50 border border-transparent rounded-lg text-gray-700";
  const downloadMetadata = () => {
    const doc = new jsPDF();

    const title = data.TITLE || "";
    const authors = (data.METADATA?.AUTHORS || []).join(", ");
    const emails = (data.METADATA?.EMAILS || []).join(", ");
    const affs = (data.METADATA?.AFFILIATIONS || []).join("\n");
    const keys = (data.METADATA?.KEYWORDS || []).join(", ");
    const abstract = data.ABSTRACT || "";

    let y = 10; // vertical cursor

    doc.setFontSize(18);
    const pageWidth = doc.internal.pageSize.getWidth();
    doc.text("Extracted Metadata", pageWidth / 2, y, { align: "center" });

    y += 10;

    doc.setFontSize(11);

    doc.text(`Title:`, 10, y);
    doc.text(title, 40, y);
    y += 8;

    doc.text(`Authors:`, 10, y);
    doc.text(authors || "—", 40, y);
    y += 8;

    doc.text(`Emails:`, 10, y);
    doc.text(emails || "—", 40, y);
    y += 8;

    doc.text(`Affiliations:`, 10, y);
    doc.text(affs || "—", 40, y);
    y += 20;

    doc.text(`Keywords:`, 10, y);
    doc.text(keys || "—", 40, y);
    y += 15;

    doc.text("Abstract:", 10, y);
    y += 8;

    // Auto-split long abstract text
    const abstractLines = doc.splitTextToSize(abstract, 180);
    doc.text(abstractLines, 10, y);

    doc.save("metadata.pdf");
  };

  const allLocked =
    locked.authors &&
    locked.emails &&
    locked.affiliations &&
    locked.keywords;

  return (
    <div className="min-h-screen w-full bg-slate-100 flex">
      {/* LEFT SIDEBAR */}
      <aside className="hidden lg:block sticky top-6 h-screen px-6 py-8 w-80">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white border border-gray-200 shadow-lg rounded-2xl p-6 h-full overflow-auto"
        >
          <h3 className="text-base font-medium text-gray-600 mb-6">
            Metadata Preview
          </h3>
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500">Title</h4>
            <p className="text-sm text-gray-800">{data.TITLE || "—"}</p>
          </div>
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500">Authors</h4>
            <p className="text-sm text-gray-800">{previewAuthors.join(", ") || "—"}</p>
          </div>
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500">Emails</h4>
            <p className="text-sm text-gray-800">{previewEmails.join(", ") || "—"}</p>
          </div>
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500">Affiliations</h4>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">
              {previewAffiliations.join("\n") || "—"}
            </p>
          </div>
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500">Keywords</h4>
            <p className="text-sm text-gray-800">{previewKeywords.join(", ") || "—"}</p>
          </div>
        </motion.div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 px-6 py-10 max-w-4xl mx-auto">
        {data.TITLE && (
          <h1 className="text-4xl font-serif font-bold text-gray-900 mb-10">
            {data.TITLE}
          </h1>
        )}

        <motion.section
          variants={fadeIn}
          initial="hidden"
          animate="show"
          className="mb-14 p-6 bg-white rounded-xl shadow"
        >
          <h2 className="text-xl font-bold text-gray-800 mb-6">Metadata</h2>

          {/* AUTHORS */}
          <div className="mb-10">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-lg font-semibold text-gray-800">
                Authors
              </label>
              {locked.authors && (
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-md uppercase tracking-wide">
                  Confirmed ✓
                </span>
              )}
            </div>

            {/* CONDITIONAL RENDERING: If locked, show P tag. If not, show Input + Button */}
            {locked.authors ? (
              <p className={pTagClass}>{authorInput}</p>
            ) : (
              <>
                <input
                  value={authorInput}
                  onChange={(e) => setAuthorInput(e.target.value)}
                  className="w-full p-3 border rounded-lg bg-white focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="Separate by commas"
                />
                <button onClick={saveAuthors} className={buttonClass}>
                  Save Authors
                </button>
              </>
            )}
          </div>

          {/* EMAILS */}
          <div className="mb-10">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-lg font-semibold text-gray-800">
                Emails
              </label>
              {locked.emails && (
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-md uppercase tracking-wide">
                  Confirmed ✓
                </span>
              )}
            </div>

            {locked.emails ? (
              <p className={pTagClass}>{emailInput}</p>
            ) : (
              <>
                <input
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  className="w-full p-3 border rounded-lg bg-white focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="Separate by commas"
                />
                <button onClick={saveEmails} className={buttonClass}>
                  Save Emails
                </button>
              </>
            )}
          </div>

          {/* AFFILIATIONS */}
          <div className="mb-10">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-lg font-semibold text-gray-800">
                Affiliations
              </label>
              {locked.affiliations && (
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-md uppercase tracking-wide">
                  Confirmed ✓
                </span>
              )}
            </div>

            {locked.affiliations ? (
              <p className={`${pTagClass} whitespace-pre-wrap`}>{affInput}</p>
            ) : (
              <>
                <textarea
                  value={affInput}
                  onChange={(e) => setAffInput(e.target.value)}
                  rows={4}
                  className="w-full p-3 border rounded-lg bg-white focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="One per line"
                />
                <button onClick={saveAffs} className={buttonClass}>
                  Save Affiliations
                </button>
              </>
            )}
          </div>

          {/* KEYWORDS */}
          <div className="mb-10">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-lg font-semibold text-gray-800">
                Keywords
              </label>
              {locked.keywords && (
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-md uppercase tracking-wide">
                  Confirmed ✓
                </span>
              )}
            </div>

            {locked.keywords ? (
              <p className={pTagClass}>{keyInput}</p>
            ) : (
              <>
                <input
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  className="w-full p-3 border rounded-lg bg-white focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="Separate by commas"
                />
                <button onClick={saveKeys} className={buttonClass}>
                  Save Keywords
                </button>
              </>
            )}
          </div>
        </motion.section>

        <motion.section
          variants={fadeIn}
          initial="hidden"
          animate="show"
          className="mb-14 p-6 bg-white rounded-xl shadow"
        >
          <h3 className="text-xl font-semibold text-gray-800 mb-3">Abstract</h3>
          <p className="text-gray-800 text-lg whitespace-pre-wrap leading-relaxed">
            {data.ABSTRACT || "—"}
          </p>
        </motion.section>

        <div className="flex gap-4 mt-10">
          <button
            onClick={() => navigate("/")}
            className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700"
          >
            ⬅ Back to Upload
          </button>

          {allLocked && (
            <button
              onClick={downloadMetadata}
              className="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700"
            >
              Download Metadata
            </button>
          )}
        </div>

      </main>
    </div>
  );
}