export type TemplateTarget = {
  left_eye: { x: number; y: number };
  right_eye: { x: number; y: number };
  scale?: number;
  rotation_deg?: number;
};

export type MemeTemplate = {
  id: string;
  name: string;
  image: string; // public path
  target: TemplateTarget;
  blend?: { mode?: "feather" | "seamlessClone"; feather_px?: number };
};
