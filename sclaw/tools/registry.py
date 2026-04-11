"""Tool registration system with decorator-based discovery."""

from __future__ import annotations

import importlib
import importlib.util
import os
import stat
import sys
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from sclaw.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ToolInfo:
    """Information about a registered tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable
    needs_confirmation: bool = False
    required_params: list[str] = field(default_factory=list)


# Global tool registry
_registry: dict[str, ToolInfo] = {}
_core_tools_loaded = False

_CORE_TOOL_MODULES = (
    "sclaw.tools.files",
    "sclaw.tools.memory_tools",
    "sclaw.tools.shell",
    "sclaw.tools.spawn",
    "sclaw.tools.web",
)

_CORE_TOOL_NAMES = {
    "file_read",
  #  "file_write",
    "file_list",
    "shell_exec",
    "web_search",
    "web_fetch",
    "memory_save",
    "memory_search",
    "spawn_task",
}


def _core_tools_present() -> bool:
    """Check if all core tools are registered."""
    return _CORE_TOOL_NAMES.issubset(_registry.keys())


def _load_core_tools() -> None:
    """Ensure core tool modules are imported and registered."""
    global _core_tools_loaded
    if _core_tools_loaded and _core_tools_present():
        return

    needs_reload = not _core_tools_present()
    for module_name in _CORE_TOOL_MODULES:
        try:
            if needs_reload and module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"Failed to load core tool module {module_name}: {e}")

    _core_tools_loaded = True


def tool(
    name: str,
    description: str,
    parameters: dict[str, Any],
    needs_confirmation: bool = False,
    required: Optional[list[str]] = None,
) -> Callable:
    """
    Decorator to register a tool.

    Args:
        name: Tool name (used in LLM tool_calls)
        description: Human-readable description for LLM
        parameters: JSON Schema for parameters
        needs_confirmation: If True, always asks user before executing
        required: List of required parameter names (defaults to all)

    Example:
        @tool(
            name="web_search",
            description="Search the internet",
            parameters={"query": {"type": "string", "description": "Search query"}}
        )
        async def web_search(query: str) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        req_params = required if required is not None else list(parameters.keys())
        _registry[name] = ToolInfo(
            name=name,
            description=description,
            parameters=parameters,
            handler=func,
            needs_confirmation=needs_confirmation,
            required_params=req_params,
        )
        if _tool_registry is not None:
            _tool_registry.tools[name] = _registry[name]

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self) -> None:
        """Initialize with copy of global registry."""
        self.tools: dict[str, ToolInfo] = dict(_registry)

    def get_schemas(self) -> list[dict[str, Any]]:
        """
        Generate OpenAI-compatible tool schemas for LLM.

        Returns:
            List of tool schemas in OpenAI format
        """
        schemas = []
        for name, info in _registry.items():
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": info.name,
                        "description": info.description,
                        "parameters": {
                            "type": "object",
                            "properties": info.parameters,
                            "required": info.required_params,
                        },
                    },
                }
            )
        return schemas

    def get_tool_names(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self.tools.keys())

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        confirm_callback: Optional[Callable] = None,
    ) -> str:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Tool name
            arguments: Tool arguments
            confirm_callback: Optional async callback for user confirmation

        Returns:
            Tool result as string
        """
        if name not in self.tools:
            return f"Unknown tool: {name}"

        tool_info = self.tools[name]

        # Tools that always need confirmation
        if tool_info.needs_confirmation and confirm_callback:
            import json

            approved = await confirm_callback(
                f"Tool `{name}` wants to run with:\n"
                f"```\n{json.dumps(arguments, indent=2)}\n```\n\nAllow?"
            )
            if not approved:
                return "User denied this action."

        try:
            # Handle malformed LLM output: {'parameters': {'query': '...'}}
            if "parameters" in arguments and len(arguments) == 1:
                logger.warning(f"Tool {name}: unwrapping nested 'parameters' from LLM")
                arguments = arguments["parameters"]

            result = await tool_info.handler(**arguments)
            return str(result)
        except TypeError as e:
            return f"Invalid arguments for {name}: {e}"
        except Exception as e:
            return f"Tool {name} failed: {e}"

    def load_skills(self, skills_dir: str, log_config: Optional[dict] = None) -> None:
        """
        Auto-discover and load skills from skills directory.

        Supports Claude Code skills in folder structure:
        - skills/weather/skill.md -> skill name: weather
        - skills/github/skill.md -> skill name: github

        Only loads files owned by the current user and not writable by
        group/others (prevents tampering by other users on shared systems).

        Args:
            skills_dir: Path to skills directory
            log_config: Optional logging configuration dict with 'level' and 'file' keys
        """
        # Create a dedicated logger for skill loading if log_config is provided
        if log_config:
            from sclaw.core.logger import setup_logger
            skill_logger = setup_logger("sclaw.skills", log_config=log_config)
        else:
            skill_logger = logger
        
        import platform
        skill_logger.info(f"[INFO] Platform: {platform.system()}")
        skill_logger.info(f"[INFO] Current user: {os.getuid() if hasattr(os, 'getuid') else 'N/A (Windows)'}")
        
        skills_path = Path(skills_dir)
        skill_logger.info(f"Loading skills from directory: {skills_path.absolute()}")
        
        if not skills_path.exists():
            skill_logger.warning(f"Skills directory not found: {skills_path.absolute()}")
            skill_logger.warning(f"[INFO] Directory exists check: False")
            skill_logger.warning(f"[INFO] Parent directory exists: {skills_path.parent.exists()}")
            return

        skill_logger.info(f"[INFO] Directory exists: True")
        skill_logger.info(f"[INFO] Directory is readable: {os.access(skills_path, os.R_OK)}")
        
        # Check directory ownership and permissions
        try:
            dir_stat = skills_path.stat()
            skill_logger.info(f"[INFO] Directory stat: st_uid={dir_stat.st_uid}, st_mode={oct(dir_stat.st_mode)}")
            
            # Skip ownership check on Windows (no getuid)
            if platform.system() != "Windows":
                current_uid = os.getuid()
                skill_logger.info(f"[INFO] Ownership check: dir_uid={dir_stat.st_uid}, current_uid={current_uid}")
                if dir_stat.st_uid != current_uid:
                    skill_logger.warning(f"Skills directory not owned by current user: {skills_path}")
                    skill_logger.warning(f"[INFO] Owner mismatch: directory owned by {dir_stat.st_uid}, current user is {current_uid}")
                    return
            
            # Skip permission check on Windows (different permission model)
            if platform.system() != "Windows":
                is_writable_by_group = dir_stat.st_mode & stat.S_IWGRP
                is_writable_by_others = dir_stat.st_mode & stat.S_IWOTH
                skill_logger.info(f"[INFO] Permission check: writable_by_group={bool(is_writable_by_group)}, writable_by_others={bool(is_writable_by_others)}")
                if is_writable_by_group or is_writable_by_others:
                    skill_logger.warning(f"Skills directory writable by others: {skills_path}")
                    return
        except OSError as e:
            skill_logger.error(f"[INFO] OSError during directory stat check: {e}")
            return

        # Load Claude Code skills from folders
        from sclaw.skills.internal.claude_parser import ClaudeSkill
        from sclaw.skills.internal.knowledge_tool import KnowledgeTool

        # Iterate through skill folders
        skill_count = 0
        skipped_count = 0
        error_count = 0
        
        skill_logger.info(f"[INFO] Starting directory iteration...")
        try:
            all_items = list(skills_path.iterdir())
            skill_logger.info(f"[INFO] Found {len(all_items)} items in directory")
        except Exception as e:
            skill_logger.error(f"[INFO] Failed to iterate directory: {e}")
            return
        
        for skill_folder in all_items:
            skill_logger.info(f"[INFO] Processing item: {skill_folder.name}, is_dir={skill_folder.is_dir()}")
            
            if not skill_folder.is_dir():
                skill_logger.info(f"[INFO] Skipping {skill_folder.name}: not a directory")
                skipped_count += 1
                continue
            
            # Skip hidden folders
            if skill_folder.name.startswith("_"):
                skill_logger.info(f"[INFO] Skipping {skill_folder.name}: hidden folder")
                skipped_count += 1
                continue

            # Look for skill.md in the folder
            skill_file = skill_folder / "skill.md"
            skill_logger.info(f"[INFO] Checking for skill.md in {skill_folder.name}: {skill_file.exists()}")
            if not skill_file.exists():
                skill_logger.info(f"Skipping folder {skill_folder.name}: no skill.md found")
                skipped_count += 1
                continue

            # Validate file ownership and permissions
            try:
                file_stat = skill_file.stat()
                skill_logger.info(f"[INFO] {skill_folder.name}/skill.md stat: st_uid={file_stat.st_uid}, st_mode={oct(file_stat.st_mode)}")
                
                # Skip ownership check on Windows (no getuid)
                if platform.system() != "Windows":
                    current_uid = os.getuid()
                    skill_logger.info(f"[INFO] {skill_folder.name} ownership check: file_uid={file_stat.st_uid}, current_uid={current_uid}")
                    if file_stat.st_uid != current_uid:
                        skill_logger.warning(f"Skipping Claude skill {skill_folder.name}: not owned by current user")
                        skill_logger.warning(f"[INFO] {skill_folder.name} owner mismatch: file owned by {file_stat.st_uid}, current user is {current_uid}")
                        skipped_count += 1
                        continue
                
                # Skip permission check on Windows (different permission model)
                if platform.system() != "Windows":
                    is_writable_by_group = file_stat.st_mode & stat.S_IWGRP
                    is_writable_by_others = file_stat.st_mode & stat.S_IWOTH
                    skill_logger.info(f"[INFO] {skill_folder.name} permission check: writable_by_group={bool(is_writable_by_group)}, writable_by_others={bool(is_writable_by_others)}")
                    if is_writable_by_group or is_writable_by_others:
                        skill_logger.warning(f"Skipping Claude skill {skill_folder.name}: writable by group/others")
                        skipped_count += 1
                        continue
            except OSError as e:
                skill_logger.error(f"[INFO] OSError during file stat check for {skill_folder.name}: {e}")
                error_count += 1
                continue

            try:
                skill_logger.info(f"[INFO] Attempting to parse {skill_folder.name}/skill.md...")
                skill = ClaudeSkill.from_file(skill_file)
                if skill:
                    # Override skill name with folder name
                    skill.name = skill_folder.name
                    skill_logger.info(f"[INFO] Successfully parsed {skill_folder.name}: name={skill.name}, description={skill.description[:50]}...")
                    
                    # Use KnowledgeTool for all skills
                    skill_logger.info(f"[INFO] Using KnowledgeTool for {skill.name}")
                    knowledge_tool = KnowledgeTool(skill, skill_folder)
                    tool_info = knowledge_tool.to_tool_info()
                    
                    self.tools[tool_info.name] = tool_info
                    _registry[tool_info.name] = tool_info
                    skill_count += 1
                    skill_logger.info(f"Loaded skill: {skill_folder.name} -> {tool_info.name}")
                else:
                    skill_logger.warning(f"[INFO] ClaudeSkill.from_file returned None for {skill_folder.name}")
                    error_count += 1
            except Exception as e:
                skill_logger.error(f"[INFO] Exception while loading {skill_folder.name}: {type(e).__name__}: {e}")
                import traceback
                skill_logger.error(f"[INFO] Traceback: {traceback.format_exc()}")
                error_count += 1

        skill_logger.info(f"Total skills loaded: {skill_count}")
        skill_logger.info(f"Skipped items: {skipped_count}")
        skill_logger.info(f"Errors encountered: {error_count}")
        
        # Merge newly loaded tools
        self.tools.update(_registry)
        
        # Also update global registry to include skills
        _registry.update(self.tools)

    def register(self, tool_info: ToolInfo) -> None:
        """Manually register a tool."""
        self.tools[tool_info.name] = tool_info
        _registry[tool_info.name] = tool_info


# Global registry instance
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry
    _load_core_tools()
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _tool_registry, _registry, _core_tools_loaded
    _registry.clear()
    _tool_registry = None
    _core_tools_loaded = False
