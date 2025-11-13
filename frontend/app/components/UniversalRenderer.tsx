"use client";

import React, { JSX } from "react";


export function UniversalRenderer({ data }: { data: any }) {
  return (
    <div dir="rtl" className="text-right">
      {renderAny(data)}
    </div>
  );
}

function renderAny(data: any): JSX.Element {
  if (data === null || data === undefined) {
    return <span className="italic text-slate-400">ריק</span>;
  }

  if (typeof data === "string") {
    return (
      <span className="text-slate-800 whitespace-pre-wrap leading-relaxed">
        {data}
      </span>
    );
  }

  if (typeof data === "number" || typeof data === "boolean") {
    return (
      <span className="font-semibold text-blue-700">
        {String(data)}
      </span>
    );
  }

  if (Array.isArray(data)) {
    return (
      <ul className="list-disc pr-6 space-y-2">
        {data.map((item, i) => (
          <li key={i} className="text-slate-700">
            {renderAny(item)}
          </li>
        ))}
      </ul>
    );
  }

  if (typeof data === "object") {
    return (
      <div className="space-y-4">
        {Object.entries(data).map(([key, value], index) => (
          <div
            key={index}
            className="border border-slate-200 bg-white rounded-xl p-4 shadow-sm"
          >
            <h3 className="text-lg font-bold text-indigo-800 mb-2">
              {formatKey(key)}
            </h3>

            <div className="pl-2">
              {renderAny(value)}
            </div>
          </div>
        ))}
      </div>
    );
  }


  return <span className="text-red-600">Unsupported Type</span>;
}

function formatKey(key: string) {
  return key.replace(/_/g, " ");
}
