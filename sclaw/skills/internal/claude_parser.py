"""Claude Code skill format parser (YAML + Markdown)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from sclaw.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClaudeSkill:
    """Parsed Claude Code skill."""

    name: str
    description: str
    content: str
    triggers: list[str]

    @classmethod
    def from_file(cls, file_path: Path) -> Optional["ClaudeSkill"]:
        """
        Parse a Claude Code skill file.

        Args:
            file_path: Path to .md or .yaml file

        Returns:
            Parsed ClaudeSkill or None if invalid
        """
        logger.debug(f"[DEBUG] Attempting to parse skill file: {file_path}")
        
        try:
            content = file_path.read_text(encoding="utf-8")
            logger.debug(f"[DEBUG] Successfully read {len(content)} bytes from {file_path}")
        except Exception as e:
            logger.error(f"Failed to read skill file {file_path}: {type(e).__name__}: {e}")
            logger.debug(f"[DEBUG] File path absolute: {file_path.absolute()}")
            logger.debug(f"[DEBUG] File exists: {file_path.exists()}")
            logger.debug(f"[DEBUG] File is readable: {file_path.is_file()}")
            return None

        # Parse YAML frontmatter
        yaml_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not yaml_match:
            logger.warning(f"No YAML frontmatter found in {file_path}")
            logger.debug(f"[DEBUG] Content preview (first 200 chars): {content[:200]}")
            return None

        yaml_str, markdown_content = yaml_match.groups()
        logger.debug(f"[DEBUG] YAML frontmatter length: {len(yaml_str)} bytes")
        logger.debug(f"[DEBUG] Markdown content length: {len(markdown_content)} bytes")

        try:
            metadata = yaml.safe_load(yaml_str)
            logger.debug(f"[DEBUG] Parsed metadata: {metadata}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML in {file_path}: {type(e).__name__}: {e}")
            logger.debug(f"[DEBUG] YAML content: {yaml_str}")
            return None

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        triggers = metadata.get("triggers", [])

        logger.debug(f"[DEBUG] Extracted name: '{name}'")
        logger.debug(f"[DEBUG] Extracted description: '{description[:100]}...'")

        if not name or not description:
            logger.warning(f"Missing name or description in {file_path}")
            logger.debug(f"[DEBUG] Name empty: {not name}, Description empty: {not description}")
            return None

        logger.debug(f"[DEBUG] Successfully parsed skill: {name}")
        return cls(
            name=name,
            description=description,
            content=markdown_content.strip(),
            triggers=triggers if triggers else cls._extract_triggers(description),
        )

    @staticmethod
    def _extract_triggers(description: str) -> list[str]:
        """
        Extract trigger keywords from description.

        Args:
            description: Skill description

        Returns:
            List of trigger keywords
        """
        # Simple keyword extraction from description
        words = re.findall(r"\b\w{3,}\b", description.lower())
        # Remove common words
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "with", "this", "that", "from", "they", "will", "have", "been", "more", "when", "into", "some", "than", "them", "very", "just", "over", "such", "your", "about", "would", "which", "their"}
        keywords = [w for w in words if w not in stop_words]
        return keywords[:10]  # Limit to top 10 keywords

    def to_tool_schema(self) -> dict:
        """
        Convert to tool schema format.

        Returns:
            Tool schema dict
        """
        return {
            "type": "function",
            "function": {
                "name": f"skill_{self.name}",
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User query or request",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
