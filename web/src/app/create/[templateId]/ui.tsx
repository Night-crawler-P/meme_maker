"use client";

import { useMemo, useState } from "react";
import type { MemeTemplate } from "../../../lib/types";

function apiBase() {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
}

export default function CreateClient({ template }: { template: MemeTemplate }) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);

  const canGo = !!file && !busy;

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  async function onGenerate() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setResultUrl(null);

    try {
      const form = new FormData();
      form.append("template_id", template.id);
      form.append("photo", file);

      const res = await fetch(`${apiBase()}/render`, { method: "POST", body: form });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `Render failed (${res.status})`);
      }

      const blob = await res.blob();
      setResultUrl(URL.createObjectURL(blob));
    } catch (e: any) {
      setError(e?.message || "Failed")
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="twoCol">
      <section>
        <h2>1) Upload face photo</h2>
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />

        {previewUrl && (
          <div className="panel">
            <div className="muted">Preview</div>
            <img className="preview" src={previewUrl} alt="upload preview" />
          </div>
        )}

        <h2>2) Generate</h2>
        <button disabled={!canGo} onClick={onGenerate}>
          {busy ? "Generating…" : "Generate meme"}
        </button>
        {error && <div className="error">{error}</div>}
      </section>

      <section>
        <h2>Template</h2>
        <img className="preview" src={template.image} alt={template.name} />

        <h2>Result</h2>
        {resultUrl ? (
          <div className="panel">
            <img className="preview" src={resultUrl} alt="result" />
            <div className="row">
              <a className="btn" href={resultUrl} download={`${template.id}.png`}>Download</a>
              <a className="btn" href={resultUrl} target="_blank" rel="noreferrer">Open</a>
            </div>
          </div>
        ) : (
          <div className="muted">Generate to see output.</div>
        )}
      </section>
    </div>
  );
}
