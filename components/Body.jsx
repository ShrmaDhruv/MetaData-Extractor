import React, { useState } from "react";
import MyDropzone from "../utils/Dropzone";

export default function Body() {
  const [uploadStatus, setUploadStatus] = useState("");
  const [loading, setLoading] = useState(false);

  // Function that will be called from Dropzone when file is selected
  const handleFileUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    setUploadStatus("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/upload/", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setUploadStatus(`File uploaded successfully ${data.info}`);
      } else {
        setUploadStatus("Upload failed. Please try again.");
      }
    } catch (err) {
      console.error(err);
      setUploadStatus("Error connecting to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-6 md:p-12">
      <div className="w-full max-w-3xl bg-white shadow-xl rounded-2xl p-8 md:p-10 transition-transform transform hover:scale-[1.01] hover:shadow-2xl">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-6 text-center">
          Upload Your Document
        </h2>
        <p className="text-gray-500 text-center mb-6">
          Drag & drop your PDF here or click to browse from your computer.
        </p>

        <MyDropzone onFileUpload={handleFileUpload} />

        {/* Status Message */}
        {loading && (
          <p className="mt-6 text-blue-600 text-center font-medium animate-pulse">
            ⏳ Uploading...
          </p>
        )}
        {uploadStatus && (
          <p
            className={`mt-6 text-center font-medium ${
              uploadStatus.startsWith("File uploaded successfully")
                ? "text-green-600"
                : "text-red-600"
            }`}
          >
            {uploadStatus}
          </p>
        )}
      </div>
    </div>
  );
}
