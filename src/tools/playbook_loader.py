import yaml
from pathlib import Path
from typing import Dict, List, Optional
import re


class PlaybookLoader:
    """
    Load and match playbooks for hybrid AI + playbook code generation.

    Based on Google's hierarchical playbook approach:
    Level 1: General Instruction (file ops, git, etc.)
    Level 2: Style (language/framework standards)
    Level 3: Task-Specific (CRUD, tests, etc.)
    Level 4: Project-Specific (client patterns)

    Reference: arXiv:2603.27296
    """

    def __init__(self, playbooks_dir: str = "playbooks"):
        self.playbooks_dir = Path(playbooks_dir)
        self._playbooks_cache = {}
        self._hierarchy_dirs = {
            "general": self.playbooks_dir / "general",
            "style": self.playbooks_dir / "style",
            "tasks": self.playbooks_dir / "tasks",
            "projects": self.playbooks_dir / "projects"
        }

    def find_matching_playbook(self, task_description: str) -> Optional[Dict]:
        """
        Find a playbook that matches the task description.

        Args:
            task_description: Natural language task description

        Returns:
            Playbook dict if match found, None otherwise
        """
        task_lower = task_description.lower()

        # Load all playbooks
        playbooks = self._load_all_playbooks()

        best_match = None
        best_score = 0

        for playbook in playbooks:
            score = self._calculate_match_score(task_lower, playbook)
            if score > best_score:
                best_score = score
                best_match = playbook

        # Threshold: require at least 30% match
        if best_score >= 0.3:
            return best_match

        return None

    def _load_all_playbooks(self) -> List[Dict]:
        """Load all playbook YAML files"""
        if self._playbooks_cache:
            return list(self._playbooks_cache.values())

        playbooks = []
        for yaml_file in self.playbooks_dir.glob("*.yaml"):
            if yaml_file.name == "playbook_template.yaml":
                continue

            try:
                with open(yaml_file) as f:
                    playbook = yaml.safe_load(f)
                    playbook["_file"] = yaml_file.name
                    playbooks.append(playbook)
                    self._playbooks_cache[yaml_file.name] = playbook
            except Exception as e:
                print(f"Warning: Failed to load playbook {yaml_file}: {e}")

        return playbooks

    def _calculate_match_score(self, task_description: str, playbook: Dict) -> float:
        """Calculate how well a playbook matches the task"""
        score = 0.0
        total_weight = 0.0

        # Check keyword matches
        pattern = playbook.get("pattern", {})
        keywords = pattern.get("keywords", [])

        if keywords:
            weight = 0.6
            total_weight += weight
            matched = sum(1 for kw in keywords if kw.lower() in task_description)
            score += (matched / len(keywords)) * weight

        # Check category relevance
        category = playbook.get("category", "")
        if category:
            weight = 0.2
            total_weight += weight
            if category.lower() in task_description:
                score += weight

        # Check description relevance
        description = playbook.get("description", "")
        if description:
            weight = 0.2
            total_weight += weight
            desc_words = set(description.lower().split())
            task_words = set(task_description.split())
            overlap = len(desc_words & task_words)
            if desc_words:
                score += (overlap / len(desc_words)) * weight

        return score / total_weight if total_weight > 0 else 0.0

    def get_playbook(self, playbook_name: str) -> Optional[Dict]:
        """Load a specific playbook by name"""
        if playbook_name in self._playbooks_cache:
            return self._playbooks_cache[playbook_name]

        playbook_path = self.playbooks_dir / playbook_name
        if not playbook_path.exists():
            return None

        try:
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)
                playbook["_file"] = playbook_name
                self._playbooks_cache[playbook_name] = playbook
                return playbook
        except Exception as e:
            print(f"Error loading playbook {playbook_name}: {e}")
            return None

    def format_playbook_for_agent(self, playbook: Dict) -> str:
        """Format playbook as Markdown for agent consumption"""
        output = []

        output.append(f"# Playbook: {playbook.get('name', 'Unknown')}")
        output.append(f"\n**Description**: {playbook.get('description', '')}")
        output.append(f"\n**Category**: {playbook.get('category', '')}")
        output.append(f"\n**Reduces Hallucination**: {playbook.get('reduces_hallucination', False)}")

        # Steps
        output.append("\n## Deterministic Steps\n")
        steps = playbook.get("steps", [])
        for step in steps:
            step_num = step.get("step", "?")
            action = step.get("action", "")
            output.append(f"{step_num}. {action}")

            if step.get("deterministic"):
                output.append("   *(deterministic)*")

            if "options" in step:
                output.append(f"   Options: {', '.join(step['options'])}")

            if "template" in step:
                output.append(f"   Template: `{step['template']}`")

        # Templates
        templates = playbook.get("templates", {})
        if templates:
            output.append("\n## Code Templates\n")
            for template_name, framework_templates in templates.items():
                output.append(f"### {template_name}\n")
                for framework, code in framework_templates.items():
                    output.append(f"**{framework}**:")
                    output.append(f"```\n{code}\n```\n")

        # Validation
        validation = playbook.get("validation", [])
        if validation:
            output.append("\n## Validation Checklist\n")
            for item in validation:
                output.append(f"- [ ] {item}")

        # Example
        example = playbook.get("example", {})
        if example:
            output.append("\n## Example\n")
            for key, value in example.items():
                output.append(f"**{key}**: {value}")

        return "\n".join(output)

    def list_available_playbooks(self) -> List[str]:
        """List all available playbook names"""
        playbooks = self._load_all_playbooks()
        return [p.get("name", p["_file"]) for p in playbooks]

    def select_playbooks_for_task(
        self,
        task: Dict,
        project_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Select all applicable playbooks for a task (hierarchical).

        Based on Google's approach: combine multiple playbook levels.

        Args:
            task: Task dict with description, language, framework
            project_name: Optional project name for project-specific playbooks

        Returns:
            List of playbooks ordered by level (general → style → task → project)
        """
        selected = []

        # Level 1: General (always include file operations)
        general_playbook = self._load_from_level("general", "file_operations.yaml")
        if general_playbook:
            selected.append(general_playbook)

        # Level 2: Style (based on language/framework)
        language = task.get("language", "python")
        framework = task.get("framework", "")

        style_playbook = self._find_style_playbook(language, framework)
        if style_playbook:
            selected.append(style_playbook)

        # Level 3: Task-Specific (match task description)
        task_playbook = self.find_matching_playbook(task.get("description", ""))
        if task_playbook:
            selected.append(task_playbook)

        # Level 4: Project-Specific (if project name provided)
        if project_name:
            project_playbook = self._find_project_playbook(project_name, task)
            if project_playbook:
                selected.append(project_playbook)

        return selected

    def _load_from_level(self, level: str, filename: str) -> Optional[Dict]:
        """Load playbook from specific level directory"""
        level_dir = self._hierarchy_dirs.get(level)
        if not level_dir:
            return None

        playbook_path = level_dir / filename
        if not playbook_path.exists():
            return None

        try:
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)
                playbook["_file"] = filename
                playbook["_level"] = level
                return playbook
        except Exception as e:
            print(f"Error loading {playbook_path}: {e}")
            return None

    def _find_style_playbook(
        self,
        language: str,
        framework: str
    ) -> Optional[Dict]:
        """Find appropriate style playbook for language/framework"""
        style_dir = self._hierarchy_dirs.get("style")
        if not style_dir or not style_dir.exists():
            return None

        # Try framework-specific first
        if framework:
            style_file = f"{language}_{framework}.yaml"
            playbook = self._load_from_level("style", style_file)
            if playbook:
                return playbook

        # Fall back to language-only
        style_file = f"{language}.yaml"
        return self._load_from_level("style", style_file)

    def _find_project_playbook(
        self,
        project_name: str,
        task: Dict
    ) -> Optional[Dict]:
        """Find project-specific playbook"""
        project_dir = self._hierarchy_dirs.get("projects") / project_name
        if not project_dir.exists():
            return None

        # Try to match task to project playbooks
        for playbook_file in project_dir.glob("*.yaml"):
            playbook = self._load_from_level(f"projects/{project_name}", playbook_file.name)
            if playbook and self._matches_task(playbook, task):
                return playbook

        return None

    def _matches_task(self, playbook: Dict, task: Dict) -> bool:
        """Check if playbook matches task"""
        pattern = playbook.get("pattern", {})
        keywords = pattern.get("keywords", [])
        task_desc = task.get("description", "").lower()

        if not keywords:
            return False

        # Check if any keyword matches
        return any(kw.lower() in task_desc for kw in keywords)
