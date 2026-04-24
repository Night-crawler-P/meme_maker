import { getTemplate } from "../../../lib/templates";
import CreateClient from "./ui";

export default function CreatePage({ params }: { params: { templateId: string } }) {
  const template = getTemplate(params.templateId);
  if (!template) return <main><h1>Unknown template</h1></main>;

  return (
    <main>
      <h1>Create: {template.name}</h1>
      <CreateClient template={template} />
    </main>
  );
}
