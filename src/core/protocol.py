import frontmatter
import re
from typing import Dict, List, Any


class AgentMessage:
    """Represents a parsed agent message"""

    def __init__(self, raw_markdown: str):
        # If output starts cleanly with ---, use as-is.
        # If Claude added preamble text before the --- block, strip it.
        if raw_markdown.startswith('---\n'):
            normalized = raw_markdown
        else:
            # Find first occurrence of \n---\n which marks start of frontmatter after preamble
            fm_start = raw_markdown.find('\n---\n')
            if fm_start >= 0:
                normalized = raw_markdown[fm_start + 1:]
            else:
                normalized = raw_markdown

        # Parse frontmatter and content
        post = frontmatter.loads(normalized)

        self.metadata = dict(post.metadata)
        self.content = post.content
        self.raw = raw_markdown

        # Parse sections (## Heading)
        self.sections = self._parse_sections(post.content)

    def _parse_sections(self, content: str) -> Dict[str, str]:
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def extract_code_changes(self) -> List[Dict[str, str]]:
        """Extract Aider-style SEARCH/REPLACE blocks"""
        changes = []
        text = self.sections.get("Changes", "")

        # Pattern: <<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE
        # Search the full content (not just Changes section) to catch inline blocks
        full_text = self.content if self.content else text
        pattern = r'<<<<<<< SEARCH\n(.*?)\n?=======\n(.*?)\n>>>>>>> REPLACE'
        matches = re.findall(pattern, full_text, re.DOTALL)

        for search, replace in matches:
            changes.append({
                "search": search.strip(),
                "replace": replace.strip()
            })

        return changes

    def __str__(self):
        return f"AgentMessage(metadata={self.metadata}, sections={list(self.sections.keys())})"

    def __repr__(self):
        return self.__str__()
