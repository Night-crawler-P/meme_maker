import { getTemplates } from "../lib/templates";

export default function HomePage() {
  const templates = getTemplates();

  return (
    <main>
      <h1>Pick a meme template</h1>
      <p className="muted">Upload a face photo, we’ll detect the face and blend it into the meme.</p>

      <div className="grid">
        {templates.map((t) => (
          <a key={t.id} className="card" href={`/create/${t.id}`}>
            <img className="thumb" src={t.image} alt={t.name} />
            <div className="cardTitle">{t.name}</div>
          </a>
        ))}
      </div>
    </main>
  );
}
