"""
Skills Matcher — finds the relevant skill playbook for a task description.
Handles both Flutter skills (.agents/skills/) and React playbooks (playbooks/react/).
"""
from pathlib import Path
from typing import Optional

FLUTTER_SKILLS_DIR = Path(".agents/skills")
REACT_PLAYBOOKS_DIR = Path("playbooks/react")

FLUTTER_SKILL_KEYWORDS = {
    "flutter-implement-json-serialization": ["json", "fromjson", "tojson", "serializ", "model", "parse", "dart:convert"],
    "flutter-build-responsive-layout":      ["responsive", "layout", "breakpoint", "mediaquery", "layoutbuilder", "tablet", "mobile", "desktop", "adaptive"],
    "flutter-fix-layout-issues":            ["overflow", "unbounded", "renderflex", "constraint", "layout error", "fix layout"],
    "flutter-add-widget-test":              ["widget test", "widgettester", "unit test", "test widget"],
    "flutter-add-integration-test":         ["integration test", "e2e", "flutter driver", "user flow"],
    "flutter-use-http-package":             ["http", "get request", "post request", "rest api", "fetch", "dio", "api call"],
    "flutter-setup-declarative-routing":    ["routing", "navigation", "go_router", "deep link", "url", "route"],
    "flutter-apply-architecture-best-practices": ["architecture", "layered", "clean", "repository pattern", "service layer"],
    "flutter-add-widget-preview":           ["preview", "widget preview", "ui component", "design"],
    "flutter-setup-localization":           ["localization", "l10n", "internalization", "i18n", "locale"],
}

REACT_SKILL_KEYWORDS = {
    "react-dashboard-component":  ["card", "panel", "kpi", "dashboard", "widget", "component", "badge", "shadcn"],
    "react-query-service":        ["api", "fetch", "axios", "react query", "usequery", "service", "endpoint", "http"],
    "react-tanstack-table":       ["table", "tanstack", "react-table", "sortable", "filterable", "jobs snapshot", "data grid"],
    "react-recharts-chart":       ["chart", "recharts", "line chart", "area chart", "revenue", "trend", "graph"],
}


def _is_react_task(task_description: str, file_path: str = "") -> bool:
    """Detect if task is React (TSX/JSX) vs Flutter (Dart)."""
    desc_lower = task_description.lower()
    react_signals = ["react", "tsx", "jsx", "tailwind", "shadcn", "vite", "recharts", "tanstack", ".tsx", ".jsx"]
    flutter_signals = ["flutter", "dart", "widget", "statefulwidget", ".dart", "dio"]
    if file_path.endswith((".tsx", ".jsx", ".ts", ".js")):
        return True
    if file_path.endswith(".dart"):
        return False
    react_score = sum(1 for s in react_signals if s in desc_lower or s in file_path.lower())
    flutter_score = sum(1 for s in flutter_signals if s in desc_lower or s in file_path.lower())
    return react_score > flutter_score


def find_skill(task_description: str, file_path: str = "") -> Optional[str]:
    """Return skill content if a matching skill is found."""
    desc_lower = task_description.lower()

    if _is_react_task(task_description, file_path):
        # React skill lookup
        best_skill = None
        best_score = 0
        for skill_name, keywords in REACT_SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            if score > best_score:
                best_score = score
                best_skill = skill_name

        if best_score > 0 and best_skill:
            skill_path = REACT_PLAYBOOKS_DIR / f"{best_skill}.md"
            if skill_path.exists():
                return skill_path.read_text()
    else:
        # Flutter skill lookup
        best_skill = None
        best_score = 0
        for skill_name, keywords in FLUTTER_SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            if score > best_score:
                best_score = score
                best_skill = skill_name

        if best_score > 0 and best_skill:
            skill_path = FLUTTER_SKILLS_DIR / best_skill / "SKILL.md"
            if skill_path.exists():
                return skill_path.read_text()

    return None


def find_skill_name(task_description: str, file_path: str = "") -> Optional[str]:
    """Return just the skill name."""
    desc_lower = task_description.lower()

    if _is_react_task(task_description, file_path):
        best_skill, best_score = None, 0
        for skill_name, keywords in REACT_SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            if score > best_score:
                best_score, best_skill = score, skill_name
        return best_skill if best_score > 0 else None
    else:
        best_skill, best_score = None, 0
        for skill_name, keywords in FLUTTER_SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            if score > best_score:
                best_score, best_skill = score, skill_name
        return best_skill if best_score > 0 else None
