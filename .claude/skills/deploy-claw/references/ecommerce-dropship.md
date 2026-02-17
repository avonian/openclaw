# Ecommerce Dropshipping Team

A 4-agent team for running a Discord-managed dropshipping business.

## Team Definition

```json
{
  "name": "dropship-crew",
  "model": {
    "provider": "<REPLACE>",
    "baseUrl": "<REPLACE>",
    "apiKey": "<REPLACE>",
    "api": "openai-completions",
    "models": [
      {
        "id": "<REPLACE>",
        "name": "<REPLACE>",
        "contextWindow": 131072,
        "maxTokens": 16384,
        "input": ["text"],
        "reasoning": false
      }
    ]
  },
  "agents": [
    {
      "id": "crate",
      "name": "Crate",
      "emoji": "\ud83d\udce6",
      "role": "Operations manager. Handles supplier communication, inventory tracking, order fulfillment, and shipping logistics.",
      "systemPromptSnippet": "You are Crate, the operations backbone of a dropshipping business. You track inventory levels, manage supplier relationships, process purchase orders, and ensure shipments go out on time. You escalate stockouts and delays to the team immediately.",
      "skills": ["github", "trello"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "harbor",
      "name": "Harbor",
      "emoji": "\ud83d\udc64",
      "role": "Customer support agent. Handles inquiries, returns, refunds, and satisfaction follow-ups.",
      "systemPromptSnippet": "You are Harbor, the friendly face of the business. You respond to customer inquiries with empathy and speed. You handle returns, refunds, and complaints. You log recurring issues and flag product quality problems to Crate.",
      "skills": ["gmail", "trello"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "flare",
      "name": "Flare",
      "emoji": "\ud83d\udcc8",
      "role": "Growth and marketing strategist. Runs ad campaigns, SEO, social media, and conversion optimization.",
      "systemPromptSnippet": "You are Flare, the marketing engine. You plan and execute ad campaigns, optimize product listings for SEO, manage social media content, and track conversion metrics. You coordinate with Bolt for landing pages and with Crate for inventory-aware promotions.",
      "skills": ["github", "notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "bolt",
      "name": "Bolt",
      "emoji": "\ud83d\udee0\ufe0f",
      "role": "Developer. Maintains the storefront, integrations, automations, and internal tools.",
      "systemPromptSnippet": "You are Bolt, the technical builder. You maintain the online storefront, build integrations with suppliers and shipping APIs, create internal automation scripts, and fix bugs. You support Flare with landing page changes and Crate with tracking dashboards.",
      "skills": ["github", "coding-agent"],
      "discordToken": "<REPLACE>"
    }
  ],
  "discord": {
    "guildId": "<REPLACE>",
    "groupPolicy": "open"
  },
  "graphiti": {
    "enabled": false,
    "neo4jPassword": "",
    "openaiApiKey": ""
  },
  "gateway": {
    "token": "<REPLACE>",
    "port": 18789
  }
}
```

## Suggested Discord Channel Structure

Create these channels in your guild before deploying:

| Channel    | Purpose                                                    |
| ---------- | ---------------------------------------------------------- |
| `#ops`     | Supplier orders, inventory alerts, shipping updates        |
| `#support` | Support tickets, refund requests, satisfaction tracking    |
| `#growth`  | Campaign planning, SEO reports, conversion experiments     |
| `#dev`     | Code reviews, deployment logs, integration work            |
| `#general` | Cross-team discussion, priorities, blockers, decisions     |
| `#alerts`  | Automated alerts: stockouts, failed shipments, site errors |

## Customization Tips

- **Model**: Replace the `model` section with your preferred provider (OpenAI, Anthropic, Kimi, etc.)
- **Skills**: Adjust per-agent skill lists based on what you have installed
- **Graphiti**: Set `enabled: true` and fill in credentials for persistent knowledge graph memory
- **Roles**: Edit `systemPromptSnippet` to match your specific business processes
