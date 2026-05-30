from difflib import SequenceMatcher
import re
from pathlib import Path


class EditFailedException(Exception):
    """Raised when edit cannot be applied"""
    pass


class DiffEditor:
    """Aider-style diff-based editing with fuzzy matching"""

    def __init__(self, fuzzy_threshold: float = 0.8):
        self.fuzzy_threshold = fuzzy_threshold

    def apply_edit(
        self,
        file_path: str,
        search: str,
        replace: str
    ) -> bool:
        """Apply SEARCH/REPLACE edit with fallback strategies"""

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            original = f.read()

        # Strategy 1: Exact match
        if search in original:
            new_content = original.replace(search, replace, 1)
            self._write_file(file_path, new_content)
            return True

        # Strategy 2: Normalized whitespace
        normalized_match = self._try_normalized_match(original, search, replace)
        if normalized_match:
            self._write_file(file_path, normalized_match)
            return True

        # Strategy 3: Fuzzy match (0.8 threshold)
        fuzzy_match = self._try_fuzzy_match(original, search, replace)
        if fuzzy_match:
            self._write_file(file_path, fuzzy_match)
            return True

        raise EditFailedException(f"Cannot find match in {file_path}")

    def _try_normalized_match(self, original: str, search: str, replace: str):
        """Try matching with normalized whitespace"""
        # Normalize: strip leading/trailing whitespace per line
        def normalize(text):
            return '\n'.join(line.strip() for line in text.split('\n'))

        normalized_original = normalize(original)
        normalized_search = normalize(search)

        if normalized_search in normalized_original:
            # Find the original version with proper whitespace
            lines_original = original.split('\n')
            lines_search = search.split('\n')

            # Find matching position
            for i in range(len(lines_original) - len(lines_search) + 1):
                window = lines_original[i:i + len(lines_search)]
                if normalize('\n'.join(window)) == normalized_search:
                    # Found it - replace
                    before = '\n'.join(lines_original[:i])
                    after = '\n'.join(lines_original[i + len(lines_search):])
                    return before + ('\n' if before else '') + replace + ('\n' if after else '') + after

        return None

    def _try_fuzzy_match(self, original: str, search: str, replace: str):
        """Try fuzzy matching using SequenceMatcher"""
        lines_original = original.split('\n')
        lines_search = search.split('\n')

        best_ratio = 0
        best_pos = -1

        # Slide search window through original
        for i in range(len(lines_original) - len(lines_search) + 1):
            window = '\n'.join(lines_original[i:i + len(lines_search)])
            ratio = SequenceMatcher(None, window, search).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_pos = i

        # If best match exceeds threshold, use it
        if best_ratio >= self.fuzzy_threshold and best_pos != -1:
            before = '\n'.join(lines_original[:best_pos])
            after = '\n'.join(lines_original[best_pos + len(lines_search):])
            return before + ('\n' if before else '') + replace + ('\n' if after else '') + after

        return None

    def _write_file(self, file_path: str, content: str):
        """Write content to file"""
        with open(file_path, 'w') as f:
            f.write(content)
