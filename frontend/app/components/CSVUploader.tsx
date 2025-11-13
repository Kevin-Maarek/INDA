"use client";

import React, { useState } from "react";

export default function CSVUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [progress, setProgress] = useState<number>(0);
  const [result, setResult] = useState<any>(null);

  function reset() {
    setStatus("");
    setProgress(0);
    setResult(null);
  }

  async function handleUpload() {
    if (!file) {
      setStatus("⚠️ יש לבחור קובץ CSV קודם");
      return;
    }

    reset();
    setStatus("📤 מעלה את הקובץ...");
    setProgress(10);

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("⚙️ הקובץ נשלח, מתבצע אינדוקס ל-Qdrant...");
      setProgress(40);

      const res = await fetch("http://localhost:8001/ingest_csv", {
        method: "POST",
        body: formData,
      });

      setProgress(70);

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const data = await res.json();

      setStatus("✅ הסתיים בהצלחה!");
      setProgress(100);
      setResult(data);
    } catch (err: any) {
      setStatus("❌ שגיאה: " + err.message);
      console.error(err);
      setProgress(0);
    }
  }

  return (
    <div className="w-full max-w-xl p-4 border rounded-xl shadow bg-white">
      <h2 className="text-xl font-bold mb-3">📁 העלאת קובץ CSV לאינדוקס</h2>

      {/* File Picker */}
      <input
        type="file"
        accept=".csv"
        className="block mb-3"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      {/* Upload button */}
      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        🚀 התחל אינדוקס
      </button>

      {/* Status */}
      {status && <p className="mt-4 font-medium">{status}</p>}

      {/* Progress bar */}
      {progress > 0 && (
        <div className="w-full bg-gray-200 rounded-full h-3 mt-2">
          <div
            className="bg-green-500 h-3 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {/* Result */}
      {result && (
        <pre className="mt-4 p-3 bg-gray-100 rounded text-sm overflow-x-auto">
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
