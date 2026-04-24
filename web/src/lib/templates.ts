import templates from "../templates/index.json";
import type { MemeTemplate } from "./types";

export function getTemplates(): MemeTemplate[] {
  return (templates as any).templates as MemeTemplate[];
}

export function getTemplate(id: string): MemeTemplate | undefined {
  return getTemplates().find((t) => t.id === id);
}
