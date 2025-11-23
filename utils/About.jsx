import React from "react";
import { motion } from "framer-motion";

export default function About() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9 }}
        className="max-w-4xl bg-white shadow-2xl rounded-2xl p-10"
      >
        <h2 className="text-4xl font-extrabold text-blue-700 mb-8 text-center tracking-wide">
          About MetaData Extractor
        </h2>

        <p className="text-gray-700 text-lg leading-relaxed mb-6">
          <span className="font-semibold">MetaData Extractor</span> is an intelligent deep-learning based system
          designed to automatically extract structured metadata from the{" "}
          <span className="font-semibold">first page of academic research papers.</span>
          Research documents often contain complex formatting styles—multiple columns, dense text blocks, figures, and inconsistent layouts.
          This makes traditional OCR pipelines inaccurate and unreliable.
        </p>

        <p className="text-gray-700 text-lg leading-relaxed mb-6">
          To solve this challenge, the system uses the powerful{" "}
          <span className="font-semibold">YOLO DocSynth-300K</span> model, trained on large-scale
          document layout datasets, to accurately detect key regions on the first page—such as{" "}
          <span className="font-semibold">title, authors, emails, abstract, and main content blocks.</span>
          Instead of performing OCR on the entire page, the model extracts only the relevant regions, giving cleaner, more accurate results.
        </p>

        <p className="text-gray-700 text-lg leading-relaxed mb-6">
          After region detection, a dedicated{" "}
          <span className="font-semibold">Tesseract OCR pipeline</span> is applied to each extracted block.
          This targeted OCR method avoids noise from irrelevant page areas and produces highly accurate text
          output—even when papers have two-column layouts, unusual fonts, or tightly packed information.
        </p>

        <p className="text-gray-700 text-lg leading-relaxed mb-6">
          Once extracted, the metadata is presented to the user in a clean, organized format.
          Fields like <span className="font-semibold">authors, affiliations, keywords and emails</span> are made fully{" "}
          <span className="font-semibold">editable</span>, allowing users to correct OCR errors,
          remove duplicates, or update details before finalizing. This ensures that the resulting metadata
          is not only machine-extracted but also <span className="font-semibold">human-verified and polished.</span>
        </p>

        <p className="text-gray-700 text-lg leading-relaxed">
          By combining{" "}
          <span className="font-semibold">AI-powered layout detection</span> with
          <span className="font-semibold"> high-precision OCR</span>,
          MetaData Extractor provides a robust and scalable solution for{" "}
          <span className="font-semibold">
            metadata extraction, academic indexing, automated research processing, citation management, and digital archiving.
          </span>{" "}
          It significantly reduces manual effort while improving accuracy, efficiency, and usability for students, researchers, and organizations.
        </p>
      </motion.div>
    </div>
  );
}
