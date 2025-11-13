"use client";

import { useState } from "react";
import { UniversalRenderer } from "./components/UniversalRenderer";

const API_BASE =
  process.env.NEXT_PUBLIC_QUERY_SERVICE_URL ?? "http://localhost:8004";

const INDEX_API = "http://localhost:8010/ingest_csv";

export default function DSLChatPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<any | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  // מצב להעלאת CSV
  const [csvStatus, setCsvStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  // ====== שאילתת DSL ======
  const askQuestion = async () => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setPlan(null);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!response.ok) throw new Error(`שגיאת שרת (${response.status})`);

      const data = await response.json();
      setPlan(data.dsl);
      setResult(data.result);
    } catch (err: any) {
      setError(err.message ?? "שגיאה במהלך הבקשה");
    } finally {
      setLoading(false);
    }
  };

  // ====== העלאת קובץ CSV ======
  const uploadCSV = async (file: File) => {
    setUploading(true);
    setCsvStatus("מעלה קובץ...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(INDEX_API, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`שגיאת שרת (${res.status})`);

      const data = await res.json();
      setCsvStatus("✔ הקובץ נשלח ואינדקס הושלם בהצלחה!");
    } catch (err: any) {
      setCsvStatus("❌ שגיאה: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  // ====== רינדור ==========
  const renderResult = (data: any) => {
    if (!data) return null;

    if (typeof data === "object" && data.type === "table") {
      if (!Array.isArray(data.data) || data.data.length === 0) {
        return <div className="text-slate-500">אין נתונים להצגה</div>;
      }
      const cols = Object.keys(data.data[0] ?? {});
      return (
        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full text-sm border-collapse border border-slate-300">
            <thead className="bg-slate-100 sticky top-0">
              <tr>
                {cols.map((col) => (
                  <th key={col} className="border border-slate-300 p-2 text-right">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.data.map((row: any, i: number) => (
                <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                  {cols.map((col) => (
                    <td key={col} className="border border-slate-300 p-2">
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (typeof data === "object" && data.type === "text") {
      return (
        <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
          <p className="text-lg font-semibold text-green-800 whitespace-pre-wrap">
            {data.content}
          </p>
        </div>
      );
    }

    return <UniversalRenderer data={data} />;
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-start bg-gradient-to-br from-sky-50 to-indigo-100 px-6 py-10">
      <div className="w-full max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">

        <h1 className="text-2xl font-bold text-indigo-700 mb-6 text-center">
          מערכת ניתוח משובים + העלאת CSV
        </h1>

        {/* כפתור העלאת CSV */}
        <div className="mb-6 p-4 border rounded-xl bg-slate-50">
          <h2 className="text-lg font-semibold mb-2">📤 העלאת קובץ CSV</h2>

          <input
            type="file"
            accept=".csv"
            disabled={uploading}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                uploadCSV(e.target.files[0]);
              }
            }}
            className="mb-3"
          />

          {csvStatus && (
            <div className="mt-2 text-sm p-2 rounded bg-gray-100 border">
              {csvStatus}
            </div>
          )}
        </div>

        {/* שדה שאלה */}
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder="לדוגמה: תן לי ביקורות על חידוש ויזה"
          className="w-full resize-none rounded-xl border border-slate-300 p-4 text-lg shadow-inner focus:outline-none focus:ring-2 focus:ring-sky-400"
        />

        <button
          onClick={askQuestion}
          disabled={loading || !question.trim()}
          className="mt-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-5 py-3 text-sm font-semibold text-white shadow hover:from-sky-600 hover:to-indigo-600 disabled:opacity-60"
        >
          {loading ? "מריץ..." : "שלח"}
        </button>

        {/* תוצאה */}
        {result && (
          <div className="mt-6 rounded-xl bg-slate-50 p-4 border border-slate-200">
            <h2 className="text-slate-700 font-semibold mb-2">📊 תוצאה:</h2>
            {renderResult(result)}
          </div>
        )}
      </div>
    </main>
  );
}
