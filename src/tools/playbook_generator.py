"""
AI-Powered Playbook Generator

Based on Google's approach: AI generates playbooks from successful code examples,
then humans supervise and approve.

Reference: "A Multi-agent AI System for Deep Learning Model Migration"
arXiv:2603.27296, March 2026
"""

from pathlib import Path
from typing import List, Dict, Optional
import yaml
from datetime import datetime


class PlaybookGenerator:
    """Generate playbooks from successful code examples using LLM"""

    def __init__(self, agent_runner=None):
        self.agent_runner = agent_runner
        self.playbooks_dir = Path("playbooks")

    def generate_from_examples(
        self,
        task_description: str,
        successful_examples: List[Dict],
        level: str = "task",  # general, style, task, project
        language: str = "any",
        framework: str = "any"
    ) -> Dict:
        """
        Generate a playbook from successful code examples.

        Args:
            task_description: What task this playbook solves
            successful_examples: List of dicts with 'input', 'output', 'success'
            level: Playbook level (general, style, task, project)
            language: Programming language
            framework: Framework (if applicable)

        Returns:
            Generated playbook dict (requires human approval)
        """

        if len(successful_examples) < 2:
            raise ValueError("Need at least 2 successful examples to generate playbook")

        # Build prompt for LLM
        prompt = self._build_generation_prompt(
            task_description,
            successful_examples,
            level,
            language,
            framework
        )

        # Use agent to generate playbook
        if self.agent_runner:
            result = self.agent_runner.run("playbook_generator", prompt)
            playbook_content = result.raw
        else:
            # Fallback: return template
            playbook_content = self._generate_template(
                task_description, level, language, framework
            )

        # Parse generated playbook
        playbook = yaml.safe_load(playbook_content)

        # Add metadata
        playbook["metadata"] = {
            "level": level,
            "version": "1.0.0",
            "created_by": "ai",
            "supervised_by": "pending",
            "approval_status": "pending",
            "generated_date": datetime.now().isoformat(),
            "training_examples_count": len(successful_examples)
        }

        return playbook

    def _build_generation_prompt(
        self,
        task_description: str,
        examples: List[Dict],
        level: str,
        language: str,
        framework: str
    ) -> str:
        """Build prompt for LLM to generate playbook"""

        prompt = f"""# Generate Playbook from Examples

You are an expert at analyzing code patterns and creating reusable playbooks.

## Task
Create a playbook for: "{task_description}"

## Level: {level}
## Language: {language}
## Framework: {framework}

## Successful Examples

"""

        for i, example in enumerate(examples, 1):
            prompt += f"""### Example {i}
**Task**: {example.get('input', 'N/A')}

**Generated Code**:
```
{example.get('output', 'N/A')}
```

**Notes**: {example.get('notes', 'N/A')}

---

"""

        prompt += """## Your Task

Analyze these examples and create a playbook that captures:

1. **Common Patterns**: What patterns are consistent across examples?
2. **Deterministic Steps**: What steps can be followed mechanically?
3. **Variable Parts**: What needs to be customized per task?
4. **Code Templates**: Extract reusable templates with placeholders
5. **Validation Checks**: What should be validated?

## Output Format

Return a YAML playbook with this structure:

```yaml
name: descriptive_name
description: "Clear description"
category: api|database|testing|security|other
language: python|javascript|java|any
framework: specific_framework|any

pattern:
  keywords: ["keyword1", "keyword2"]
  entities_required: ["entity1", "entity2"]

steps:
  - step: 1
    action: "What to do"
    deterministic: true|false
    ai_guidance: "How LLM should approach"
    template: "template_name"
    validation: ["check1", "check2"]

  - step: 2
    ...

templates:
  template_name:
    {language}: |
      # Template code with {{placeholders}}

validation:
  - "Validation check 1"
  - "Validation check 2"

examples:
  - input: "Example input"
    output: "Expected output"
    success: true

best_practices:
  - "Best practice 1"
  - "Best practice 2"
```

**Important**:
- Focus on reusable patterns, not one-off solutions
- Make steps as deterministic as possible
- Include clear validation criteria
- Use placeholders like {{model_name}}, {{field_name}} in templates
- Be specific and actionable

Generate the playbook now:
"""

        return prompt

    def _generate_template(
        self,
        task_description: str,
        level: str,
        language: str,
        framework: str
    ) -> str:
        """Generate basic template if no LLM available"""

        template = f"""name: {task_description.lower().replace(' ', '_')}
description: "{task_description}"
category: general
language: {language}
framework: {framework}

pattern:
  keywords: []
  entities_required: []

steps:
  - step: 1
    action: "Analyze requirements"
    deterministic: false
    ai_guidance: "Understand what needs to be done"

  - step: 2
    action: "Implement solution"
    deterministic: false
    ai_guidance: "Follow best practices for {language}"

templates: {{}}

validation:
  - "Code compiles/runs"
  - "Follows coding standards"

examples: []
"""
        return template

    def save_for_review(self, playbook: Dict, filename: str) -> Path:
        """Save generated playbook for human review"""

        # Determine directory based on level
        level = playbook.get("metadata", {}).get("level", "task")
        output_dir = self.playbooks_dir / level

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save to file
        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False, sort_keys=False)

        return output_path

    def approve_playbook(
        self,
        playbook_path: Path,
        supervisor_name: str,
        changes: Optional[Dict] = None
    ) -> bool:
        """
        Human supervisor approves and optionally modifies playbook.

        Args:
            playbook_path: Path to playbook file
            supervisor_name: Name of approving engineer
            changes: Optional dict of changes to apply

        Returns:
            True if approved
        """

        # Load playbook
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Apply changes if provided
        if changes:
            playbook.update(changes)

        # Update metadata
        playbook["metadata"]["supervised_by"] = supervisor_name
        playbook["metadata"]["approved_date"] = datetime.now().isoformat()
        playbook["metadata"]["approval_status"] = "approved"
        playbook["metadata"]["version"] = "1.0.0"

        # Save approved version
        with open(playbook_path, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False, sort_keys=False)

        return True

    def learn_from_execution(
        self,
        playbook_name: str,
        execution_result: Dict,
        update_playbook: bool = False
    ):
        """
        Learn from playbook execution to improve it.

        Based on Google's approach: update playbooks based on executions.

        Args:
            playbook_name: Name of playbook used
            execution_result: Dict with success, code, notes
            update_playbook: Whether to automatically update (project-level only)
        """

        # Load existing playbook
        playbook_path = self._find_playbook(playbook_name)
        if not playbook_path:
            return

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Add to examples
        if "examples" not in playbook:
            playbook["examples"] = []

        playbook["examples"].append({
            "input": execution_result.get("input", ""),
            "output": execution_result.get("output", ""),
            "success": execution_result.get("success", False),
            "notes": execution_result.get("notes", ""),
            "timestamp": datetime.now().isoformat()
        })

        # For project-level playbooks, auto-update
        level = playbook.get("metadata", {}).get("level", "task")
        if update_playbook and level == "project":
            # Increment version
            current_version = playbook["metadata"].get("version", "1.0.0")
            major, minor, patch = current_version.split(".")
            playbook["metadata"]["version"] = f"{major}.{minor}.{int(patch) + 1}"
            playbook["metadata"]["last_updated"] = datetime.now().isoformat()

            # Save
            with open(playbook_path, 'w') as f:
                yaml.dump(playbook, f, default_flow_style=False, sort_keys=False)

    def _find_playbook(self, playbook_name: str) -> Optional[Path]:
        """Find playbook file by name"""
        for level_dir in ["general", "style", "tasks", "projects"]:
            path = self.playbooks_dir / level_dir / f"{playbook_name}.yaml"
            if path.exists():
                return path
        return None

    def generate_production_readiness_playbook(
        self,
        tech_stack: Dict[str, str]
    ) -> Dict:
        """
        Generate production readiness checklist playbook.

        Args:
            tech_stack: Dict with 'language', 'framework', 'database', etc.

        Returns:
            Production readiness playbook
        """

        language = tech_stack.get("language", "python")
        framework = tech_stack.get("framework", "")
        database = tech_stack.get("database", "")

        playbook = {
            "name": "production_readiness_checklist",
            "description": f"Production readiness for {language} {framework}",
            "category": "deployment",
            "language": language,
            "framework": framework,
            "metadata": {
                "level": "task",
                "version": "1.0.0",
                "created_by": "ai",
                "requires_human_review": True
            }
        }

        # Build checklist based on tech stack
        checks = []

        # Common checks
        checks.extend([
            {
                "check": "Environment Configuration",
                "items": [
                    "All secrets in environment variables",
                    "No hardcoded credentials",
                    "Environment-specific configs separated"
                ]
            },
            {
                "check": "Error Handling",
                "items": [
                    "All exceptions caught and logged",
                    "User-friendly error messages",
                    "No sensitive data in errors"
                ]
            },
            {
                "check": "Logging",
                "items": [
                    "Structured logging implemented",
                    "Appropriate log levels used",
                    "No sensitive data logged"
                ]
            },
            {
                "check": "Security",
                "items": [
                    "Input validation on all endpoints",
                    "SQL injection prevention",
                    "XSS prevention",
                    "CSRF protection",
                    "Rate limiting implemented"
                ]
            }
        ])

        # Language-specific checks
        if language == "python":
            checks.append({
                "check": "Python Specific",
                "items": [
                    "requirements.txt with pinned versions",
                    "Virtual environment documented",
                    "Python version specified"
                ]
            })

        # Framework-specific checks
        if framework == "fastapi":
            checks.append({
                "check": "FastAPI Specific",
                "items": [
                    "CORS configured properly",
                    "API documentation enabled",
                    "Health check endpoint exists",
                    "Pydantic validation on all inputs"
                ]
            })

        # Database checks
        if database:
            checks.append({
                "check": "Database",
                "items": [
                    "Connection pooling configured",
                    "Database migrations tracked",
                    "Backup strategy documented",
                    "Connection timeouts set"
                ]
            })

        playbook["checks"] = checks

        return playbook
