"""Knowledge-based skill tools for Claude Code compatibility."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
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

    def __init__(self, skill: ClaudeSkill, skill_path: Path):
        """
        Initialize KnowledgeTool.

        Args:
            skill: Parsed Claude Code skill
            skill_path: Path to the skill directory
        """
        self.skill = skill
        self.skill_path = skill_path

    async def execute(self, query: str) -> str:
        """
        Execute knowledge tool by returning skill content or running scripts.

        Args:
            query: User query (not used but kept for interface consistency)

        Returns:
            Skill content as formatted response or script execution result
        """
        logger.debug(f"Executing knowledge tool: {self.skill.name}")
        
        # Check if there are scripts in the skill directory
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists() and any(scripts_dir.iterdir()):
            logger.debug(f"Found scripts directory for skill {self.skill.name}: {scripts_dir}")
            
            # Try to execute the main script
            main_script = scripts_dir / "main.py"
            if not main_script.exists():
                # Look for any Python script
                py_scripts = list(scripts_dir.glob("*.py"))
                if py_scripts:
                    main_script = py_scripts[0]
                else:
                    logger.warning(f"No Python scripts found in {scripts_dir}")
                    return self._get_skill_content()
            
            try:
                logger.info(f"Executing script: {main_script}")
                
                # Set UTF-8 encoding for Windows compatibility
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                
                # Run the script asynchronously
                process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    str(main_script),
                    cwd=str(self.skill_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"Script execution successful for {self.skill.name}")
                    return f"""Using skill: {self.skill.name}

{self.skill.description}

---

Script execution result:
{stdout.decode('utf-8')}
"""
                else:
                    logger.error(f"Script execution failed for {self.skill.name}: {stderr.decode('utf-8')}")
                    return f"""Using skill: {self.skill.name}

{self.skill.description}

---

Script execution failed:
{stderr.decode('utf-8')}
"""
            except Exception as e:
                logger.error(f"Error executing script for {self.skill.name}: {e}")
                return self._get_skill_content()
        
        # If no scripts, return skill content
        return self._get_skill_content()

    def _get_skill_content(self) -> str:
        """
        Get skill content as formatted response.

        Returns:
            Skill content as formatted response
        """
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
