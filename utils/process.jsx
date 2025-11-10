import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function Process() {
  console.log("THIS IS PROCESS COMPONENT VERSION 999");

  const location = useLocation();
  const navigate = useNavigate();
  const content = location.state?.content || {};

  console.log("CONTENT RECEIVED:", content);

  let parsed = content;
  if (typeof content === "string") {
    try {
      parsed = JSON.parse(content.replace(/'/g, '"'));
      if (typeof parsed !== "object") parsed = {};
    } catch (e) {
      console.log("JSON parse error", e);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8">
      <div className="w-full max-w-4xl bg-white shadow-xl rounded-2xl p-8 md:p-10">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Processed Document Content
        </h2>

        <div className="border border-gray-200 rounded-lg p-6 max-h-[70vh] overflow-y-auto bg-gray-50">
          {Object.entries(parsed).map(([key, value]) => (
            <div key={key} className="mb-4">
              <p className="text-gray-900 font-semibold">{key} :</p>
              <p className="text-gray-700 whitespace-pre-wrap">
                {JSON.stringify(value, null, 2)}
              </p>
            </div>
          ))}
        </div>

        <div className="flex justify-center mt-8">
          <button
            onClick={() => navigate("/")}
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            ⬅ Back to Upload
          </button>
        </div>
      </div>
    </div>
  );
}
