import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

// Small fade animation
const fadeIn = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function Process() {
  const location = useLocation();
  const navigate = useNavigate();
  const content = location.state?.content || {};

  // Parse JSON from backend if needed
  let parsed = content;
  if (typeof content === "string") {
    try {
      parsed = JSON.parse(content.replace(/'/g, '"'));
      if (typeof parsed !== "object") parsed = {};
    } catch {
      parsed = {};
    }
  }

  const [data, setData] = useState(parsed);

  // Author & Email editors
  const [authorInput, setAuthorInput] = useState("");
  const [emailInput, setEmailInput] = useState("");
  const [authorSaved, setAuthorSaved] = useState(false);
  const [emailSaved, setEmailSaved] = useState(false);

  // Identify backend keys for author/email
  const normalizeList = (value) => {
    if (!value) return [];
    if (Array.isArray(value)) return value.map((v) => v.trim()).filter(Boolean);
    if (typeof value === "string")
      return value.split(/,|\n/).map((v) => v.trim()).filter(Boolean);
    if (typeof value === "object")
      return Object.values(value).flat().map((v) => v.trim()).filter(Boolean);
    return [];
  };

  const authorKey = Object.keys(data).find((k) =>
    k.toLowerCase().includes("author")
  );
  const emailKey = Object.keys(data).find((k) =>
    k.toLowerCase().includes("email")
  );

  // Initialize editors for detected keys
  useEffect(() => {
    if (authorKey) {
      setAuthorInput(normalizeList(data[authorKey]).join(", "));
      setAuthorSaved(false);
    }
    if (emailKey) {
      setEmailInput(normalizeList(data[emailKey]).join(", "));
      setEmailSaved(false);
    }
  }, [authorKey, emailKey]);

  // Remove individual email chip
  const removeFromEmailList = (i) => {
    const updated = normalizeList(data[emailKey]).filter((_, idx) => idx !== i);
    setData((prev) => ({ ...prev, [emailKey]: updated }));
    setEmailInput(updated.join(", "));
  };

  // Save & Join (normalize)
  const saveAuthors = () => {
    const cleaned = normalizeList(authorInput).join(", ");
    setData((prev) => ({ ...prev, [authorKey]: cleaned }));
    setAuthorSaved(true);
  };

  const saveEmails = () => {
    const cleaned = normalizeList(emailInput).join(", ");
    setData((prev) => ({ ...prev, [emailKey]: cleaned }));
    setEmailSaved(true);
  };

  // Filter content fields
  const visibleEntries = Object.entries(data).filter(([k, v]) => {
    if (!v) return false;
    if (typeof v === "string" && v.trim() === "") return false;
    if (Array.isArray(v) && v.length === 0) return false;
    return true;
  });

  return (
    <div className="min-h-screen w-full bg-slate-100 flex">

      {/* LEFT SIDEBAR */}
      <aside className="hidden lg:block sticky top-6 h-screen px-6 py-8 w-80">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white border border-gray-200 shadow-lg rounded-2xl p-6 h-full overflow-auto"
        >
          <h3 className="text-base font-medium text-gray-600 mb-6">Metadata</h3>

          {/* Title preview */}
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500 tracking-wide">Title</h4>
            <p className="text-sm text-gray-800">
              {
                visibleEntries.find(([k]) =>
                  k.toLowerCase().includes("title")
                )?.[1] || "—"
              }
            </p>
          </div>

          {/* Authors preview */}
          <div className="mb-6">
            <h4 className="text-xs uppercase text-gray-500 tracking-wide">Authors</h4>
            <p className="text-sm text-gray-800">
              {authorKey ? normalizeList(data[authorKey]).join(", ") : "—"}
            </p>
          </div>

          {/* Emails preview */}
          <div>
            <h4 className="text-xs uppercase text-gray-500 tracking-wide">Emails</h4>
            <p className="text-sm text-gray-800">
              {emailKey ? normalizeList(data[emailKey]).join(", ") : "—"}
            </p>
          </div>
        </motion.div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 px-6 py-10 max-w-4xl mx-auto">

        {visibleEntries.map(([key, value], idx) => {
          const isAuthor = key === authorKey;
          const isEmail = key === emailKey;

          return (
            <section key={key} className="mb-12">
              <motion.div variants={fadeIn} initial="hidden" animate="show">

                {/* TITLE */}
                {key.toLowerCase().includes("title") && (
                  <h1 className="text-4xl font-serif font-bold text-gray-900 mb-6">
                    {value}
                  </h1>
                )}

                {/* AUTHOR FIELD */}
                {isAuthor && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      Authors
                    </h3>

                    {!authorSaved ? (
                      <>
                        <input
                          value={authorInput}
                          onChange={(e) => setAuthorInput(e.target.value)}
                          className="w-full p-3 border rounded-lg bg-white text-gray-900"
                        />
                        <button
                          onClick={saveAuthors}
                          className="mt-3 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          Save & Join
                        </button>
                      </>
                    ) : (
                      <p className="text-gray-800">{value}</p>
                    )}
                  </div>
                )}

                {/* EMAIL FIELD */}
                {isEmail && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      Emails
                    </h3>

                    {!emailSaved ? (
                      <>
                        <div className="flex flex-wrap gap-3">
                          {normalizeList(value).map((item, i) => (
                            <motion.div
                              key={i}
                              whileHover={{ scale: 1.05 }}
                              className="px-4 py-1 bg-blue-100 rounded-full text-blue-900 flex items-center gap-2"
                            >
                              {item}
                              <button
                                onClick={() => removeFromEmailList(i)}
                                className="text-red-500 hover:text-red-700"
                              >
                                ✕
                              </button>
                            </motion.div>
                          ))}
                        </div>

                        <button
                          onClick={saveEmails}
                          className="mt-3 px-5 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          Save & Join
                        </button>
                      </>
                    ) : (
                      <p className="text-gray-800">{value}</p>
                    )}
                  </div>
                )}

                {/* CONTENT FIELD */}
                {key.toLowerCase().includes("content") &&
                  !isAuthor &&
                  !isEmail && (
                    <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
                      {value}
                    </p>
                  )}

              </motion.div>
            </section>
          );
        })}

        <button
          onClick={() => navigate("/")}
          className="mt-10 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700"
        >
          ⬅ Back to Upload
        </button>
      </main>
    </div>
  );
}
