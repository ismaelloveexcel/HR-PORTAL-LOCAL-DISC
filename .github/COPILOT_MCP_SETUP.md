## MCP configuration for Copilot coding agent

Configure in **Repository Settings → Copilot → Coding agent → MCP configuration** with JSON:

```json
{
  "mcpServers": {
    "web-fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "env": {
        "ALLOWED_ORIGINS": "https://www.mohre.gov.ae,https://u.ae,https://uaelegislation.gov.ae"
      }
    }
  }
}
```

This allows the agent to fetch official UAE sources (MOHRE, UAE portal, UAE legislation).
