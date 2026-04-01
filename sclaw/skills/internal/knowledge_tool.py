"""Knowledge-based skill tools for Claude Code compatibility."""

from __future__ import annotations

from typing import Any

from sclaw.core.logger import get_logger
from sclaw.skills.internal.claude_parser import ClaudeSkill
from sclaw.tools.registry import ToolInfo

logger = get_logger(__name__)


class KnowledgeTool:
    """
    Knowledge-based tool that returns skill content instead of executing code.

    Used for Claude Code skills that provide guidance/instructions
    rather than executable functionality.
    """

    def __init__(self, skill: ClaudeSkill):
        """
        Initialize KnowledgeTool.

        Args:
            skill: Parsed Claude Code skill
        """
        self.skill = skill

    async def execute(self, query: str) -> str:
        """
        Execute knowledge tool by returning skill content.

        Args:
            query: User query (not used but kept for interface consistency)

        Returns:
            Skill content as formatted response
        """
        logger.debug(f"Executing knowledge tool: {self.skill.name}")
        
        return f"""Using skill: {self.skill.name}

{self.skill.description}

---

{self.skill.content}
"""

    def to_tool_info(self) -> ToolInfo:
        """
        Convert to ToolInfo for registry.

        Returns:
            ToolInfo instance
        """
        return ToolInfo(
            name=f"skill_{self.skill.name}",
            description=self.skill.description,
            parameters={
                "query": {
                    "type": "string",
                    "description": "User query or request",
                }
            },
            handler=self.execute,
            needs_confirmation=False,
            required_params=["query"],
        )
