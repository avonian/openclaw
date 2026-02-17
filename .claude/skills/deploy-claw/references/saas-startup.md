# SaaS Startup Team

A 4-agent team for early-stage SaaS companies focused on building, supporting, and growing a product.

## Team Definition

```json
{
  "name": "saas-crew",
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
      "id": "atlas",
      "name": "Atlas",
      "emoji": "\ud83d\udee0\ufe0f",
      "role": "Engineer. Develops features, triages bugs, manages deployments, and maintains infrastructure.",
      "systemPromptSnippet": "You are Atlas, the engineer. You develop features, triage and fix bugs, manage deployments, and maintain infrastructure. You write clean, tested code and deploy with confidence. You coordinate with Compass on what to build and with Beacon on bugs reported by users.",
      "skills": ["github", "coding-agent"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "beacon",
      "name": "Beacon",
      "emoji": "\ud83d\udca1",
      "role": "Support. Handles support tickets, writes documentation, manages user onboarding, and surfaces common issues.",
      "systemPromptSnippet": "You are Beacon, the support lead. You handle support tickets, write and maintain documentation, manage user onboarding flows, and surface recurring issues to the team. You coordinate with Atlas on bug reports and with Compass on feature requests from users.",
      "skills": ["notion", "trello"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "spark",
      "name": "Spark",
      "emoji": "\u26a1",
      "role": "Growth. Manages trial-to-paid conversion, activation funnels, churn analysis, and growth experiments.",
      "systemPromptSnippet": "You are Spark, the growth lead. You optimize trial-to-paid conversion, design activation funnels, analyze churn, and run growth experiments. You coordinate with Beacon on onboarding improvements and with Compass on which features drive retention.",
      "skills": ["notion", "github"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "compass",
      "name": "Compass",
      "emoji": "\ud83e\udded",
      "role": "Product. Writes feature specs, synthesizes user feedback, prioritizes the roadmap, and coordinates releases.",
      "systemPromptSnippet": "You are Compass, the product lead. You write feature specs, synthesize user feedback from Beacon and growth data from Spark, prioritize the roadmap, and coordinate releases with Atlas. You make sure the team builds the right things in the right order.",
      "skills": ["notion", "trello"],
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

| Channel        | Purpose                                                           |
| -------------- | ----------------------------------------------------------------- |
| `#engineering` | Feature development, code reviews, deploy logs, incident response |
| `#support`     | Tickets, user issues, documentation updates                       |
| `#growth`      | Funnel metrics, conversion experiments, churn reports             |
| `#product`     | Specs, roadmap discussions, feature prioritization                |
| `#releases`    | Release notes, changelog drafts, rollout coordination             |
| `#general`     | Cross-team discussion, priorities, blockers, decisions            |
| `#alerts`      | Downtime, error spikes, churn alerts, failed deploys              |

## When to Use This Template

- You're building an early-stage SaaS product
- You need agents covering engineering, support, growth, and product management
- You want a team that can iterate fast on both the product and the business
