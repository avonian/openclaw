# Agency / Freelance Studio Team

A 4-agent team for running a client services agency or freelance studio.

## Team Definition

```json
{
  "name": "agency-crew",
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
      "id": "captain",
      "name": "Captain",
      "emoji": "\ud83d\udccb",
      "role": "Project manager. Handles client communication, project timelines, invoicing, and resource allocation.",
      "systemPromptSnippet": "You are Captain, the project manager. You own client relationships, manage project timelines and milestones, handle invoicing and contracts, and allocate work across the team. You keep clients informed and the team unblocked. You escalate scope creep and missed deadlines immediately.",
      "skills": ["trello", "notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "canvas",
      "name": "Canvas",
      "emoji": "\ud83c\udfa8",
      "role": "Creative. Manages design briefs, copywriting, brand assets, and creative direction.",
      "systemPromptSnippet": "You are Canvas, the creative lead. You handle design briefs, write copy, manage brand assets, and set creative direction for client projects. You work with Captain on client expectations and hand off specs to Forge for implementation.",
      "skills": ["notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "forge",
      "name": "Forge",
      "emoji": "\u2699\ufe0f",
      "role": "Developer. Builds client deliverables, maintains codebases, handles integrations and deployments.",
      "systemPromptSnippet": "You are Forge, the developer. You build client deliverables — websites, apps, integrations, automations. You take specs from Canvas and Captain, write clean code, and deploy on time. You flag technical risks early and suggest pragmatic solutions.",
      "skills": ["github", "coding-agent"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "hunter",
      "name": "Hunter",
      "emoji": "\ud83c\udfaf",
      "role": "Biz dev. Handles lead generation, proposals, pipeline tracking, and partnership outreach.",
      "systemPromptSnippet": "You are Hunter, the business development lead. You generate leads, write proposals, track the sales pipeline, and pursue partnerships. You coordinate with Captain on capacity before committing to new projects and with Canvas on pitch materials.",
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

| Channel     | Purpose                                                  |
| ----------- | -------------------------------------------------------- |
| `#projects` | Active project updates, milestone tracking, deliverables |
| `#creative` | Design briefs, copy drafts, brand assets, feedback       |
| `#dev`      | Code reviews, deploy logs, technical discussions         |
| `#sales`    | Leads, proposals, deal status, partnership opportunities |
| `#billing`  | Invoices, contracts, payment tracking                    |
| `#general`  | Cross-team discussion, priorities, blockers, decisions   |
| `#alerts`   | Deadline reminders, overdue invoices, client escalations |

## When to Use This Template

- You run a web agency, design studio, or freelance collective
- You juggle multiple client projects simultaneously
- You need agents covering sales, project management, creative, and delivery
