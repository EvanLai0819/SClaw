---
name: summarize-url
description: Fetch a URL and provide a detailed summary of its content in 3-5 bullet points
triggers:
  - summarize
  - summary
  - summarize url
  - url summary
  - page summary
---

# URL Summarization

This skill fetches web page content and provides a concise summary using AI.

## Parameters

- **url**: URL to summarize (e.g., 'https://example.com/article')

## Usage Examples

```
Summarize this article: https://example.com/news
```

```
Please provide a summary of https://github.com/project/readme
```

```
Summarize the content of this URL
```

## How It Works

1. Fetches the web page content
2. Uses AI to analyze and summarize the content
3. Returns 3-5 bullet points highlighting main points
4. Focuses on key information and insights

## Notes

- Works with most publicly accessible web pages
- Summary is concise and focused on main points
- May not work with pages requiring authentication
- Large pages may take longer to process
