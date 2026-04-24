"use client";

import { useMemo, useState } from "react";
import type { MemeTemplate } from "../../lib/types";
import templatesData from "../../templates/index.json";

type TemplatesIndex = { templates: MemeTemplate[] };

function downloadJson(obj: any, filename: string) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function TemplateAnchorEditorPage() {
  const [index, setIndex] = useState<TemplatesIndex>(templatesData as any);
  const [selectedId, setSelectedId] = useState(index.templates[0]?.id ?? "");

  const selected = useMemo(
    () => index.templates.find((t) => t.id === selectedId),
    [index, selectedId]
  );

  const [step, setStep] = useState<"left" | "right">("left");

  function onClickImage(e: React.MouseEvent<HTMLImageElement>) {
    if (!selected) return;

    const rect = (e.target as HTMLImageElement).getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) * (selectedImageNatural.w / rect.width));
    const y = Math.round((e.clientY - rect.top) * (selectedImageNatural.h / rect.height));

    const nextIndex = structuredClone(index) as TemplatesIndex;
    const t = nextIndex.templates.find((t) => t.id === selected.id)!;

    if (step === "left") {
      t.target.left_eye = { x, y };
      setStep("right");
    } else {
      t.target.right_eye = { x, y };
      setStep("left");
    }

    setIndex(nextIndex);
  }

  // track natural size for coordinate mapping
  const [selectedImageNatural, setSelectedImageNatural] = useState({ w: 1, h: 1 });

  return (
    <main>
      <h1>Template anchor editor</h1>
      <p className="muted">
        Click the template image to set <b>{step === "left" ? "LEFT" : "RIGHT"}</b> eye anchor.
        Then download the updated JSON and replace <code>web/src/templates/index.json</code>.
      </p>

      <div className="twoCol">
        <section>
          <label>
            Template:
            <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
              {index.templates.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </label>

          <div className="panel">
            <div className="muted">Current anchors</div>
            <pre className="pre">{JSON.stringify(selected?.target, null, 2)}</pre>
          </div>

          <button
            onClick={() => downloadJson(index, "index.json")}
            className="btn"
          >
            Download index.json
          </button>
        </section>

        <section>
          {selected ? (
            <div className="panel">
              <img
                className="preview"
                src={selected.image}
                alt={selected.name}
                onLoad={(e) => {
                  const img = e.currentTarget;
                  setSelectedImageNatural({ w: img.naturalWidth, h: img.naturalHeight });
                }}
                onClick={onClickImage}
              />
              <div className="muted">Image click sets anchors in original pixel coords.</div>
            </div>
          ) : (
            <div className="muted">No template selected.</div>
          )}
        </section>
      </div>
    </main>
  );
}
