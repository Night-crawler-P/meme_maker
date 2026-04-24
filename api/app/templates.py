from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import os


@dataclass
class TemplateAnchor:
    left_eye: Dict[str, float]
    right_eye: Dict[str, float]
    scale: float = 1.0
    rotation_deg: float = 0.0
    blend_mode: str = "feather"
    feather_px: int = 14


@dataclass
class MemeTemplate:
    id: str
    name: str
    template_path: str
    target: TemplateAnchor


def load_template(template_id: str) -> Optional[MemeTemplate]:
    """Loads template definitions from a JSON file colocated with the API.

    For MVP we keep API-side template metadata minimal and mirror web template ids.
    """
    here = os.path.dirname(__file__)
    index_path = os.path.join(here, "templates.json")
    if not os.path.exists(index_path):
        return None

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    t = next((x for x in data.get("templates", []) if x.get("id") == template_id), None)
    if not t:
        return None

    target = t.get("target", {})
    anchor = TemplateAnchor(
        left_eye=target.get("left_eye"),
        right_eye=target.get("right_eye"),
        scale=float(target.get("scale", 1.0)),
        rotation_deg=float(target.get("rotation_deg", 0.0)),
        blend_mode=str(t.get("blend", {}).get("mode", "feather")),
        feather_px=int(t.get("blend", {}).get("feather_px", 14)),
    )

    return MemeTemplate(
        id=t.get("id"),
        name=t.get("name"),
        template_path=os.path.join(here, "assets", t.get("asset")),
        target=anchor,
    )
