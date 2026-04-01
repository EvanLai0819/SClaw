---
name: github-repo-info
description: Get information about a GitHub repository including stars, forks, description, URL, language and last updated date
triggers:
  - github
  - repository
  - repo info
  - github repo
  - repository info
---

# GitHub Repository Information

This skill provides detailed information about GitHub repositories via the GitHub REST API.

## Parameters

- **repo**: Repository in format 'owner/name' (e.g., 'python/cpython', 'openai/openai')

## Usage Examples

```
Get info about python/cpython repository
```

```
Show me the GitHub repository for openai/openai
```

## Information Provided

- Repository name
- Star count
- Fork count
- Description
- Repository URL
- Primary language
- Last updated date

## Notes

- Requires a valid GitHub repository path
- Uses GitHub public API (no authentication needed)
- Returns HTTP 404 if repository not found
