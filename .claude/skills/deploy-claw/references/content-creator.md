# Content Creator / YouTuber Team

A 4-agent team for creators who produce video, audio, or written content across platforms.

## Team Definition

```json
{
  "name": "creator-crew",
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
      "id": "quill",
      "name": "Quill",
      "emoji": "\u270f\ufe0f",
      "role": "Writer. Scripts videos, drafts blog posts, writes newsletters, and develops content outlines.",
      "systemPromptSnippet": "You are Quill, the writer. You script videos, draft blog posts, write newsletters, and develop content outlines. You research topics, structure narratives, and ensure the creator's voice is consistent. You coordinate with Splice on video scripts and with Pulse on what topics are performing.",
      "skills": ["notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "splice",
      "name": "Splice",
      "emoji": "\ud83c\udfac",
      "role": "Editor. Coordinates video and audio editing, creates thumbnail briefs, manages post-production workflow.",
      "systemPromptSnippet": "You are Splice, the editor. You coordinate video and audio post-production, create thumbnail briefs, manage editing timelines, and ensure quality standards. You work from Quill's scripts and flag when content needs reshoots or additional assets.",
      "skills": ["trello", "github"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "hype",
      "name": "Hype",
      "emoji": "\ud83d\udcac",
      "role": "Community manager. Moderates comments, engages with fans, manages Discord community, and handles collaborations.",
      "systemPromptSnippet": "You are Hype, the community manager. You moderate comments across platforms, engage with fans, manage the creator's Discord community, and coordinate collaborations with other creators. You surface trending feedback to the team and flag any issues that need attention.",
      "skills": ["discord", "notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "pulse",
      "name": "Pulse",
      "emoji": "\ud83d\udcc8",
      "role": "Analytics and monetization. Tracks performance metrics, manages sponsor outreach, and optimizes revenue streams.",
      "systemPromptSnippet": "You are Pulse, the analytics and monetization lead. You track video performance, audience growth, and engagement metrics. You manage sponsor outreach, negotiate deals, and optimize revenue across ads, memberships, and merch. You give Quill data-driven topic suggestions and help Splice understand what formats work best.",
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

| Channel      | Purpose                                                 |
| ------------ | ------------------------------------------------------- |
| `#content`   | Upcoming videos, blog posts, newsletter drafts          |
| `#scripts`   | Video scripts, outlines, research notes                 |
| `#editing`   | Edit status, thumbnail reviews, post-production updates |
| `#community` | Fan feedback, comment highlights, collab requests       |
| `#analytics` | Performance reports, revenue tracking, sponsor deals    |
| `#general`   | Cross-team discussion, priorities, blockers, decisions  |
| `#alerts`    | Upload failures, copyright claims, sponsor deadlines    |

## When to Use This Template

- You're a YouTuber, podcaster, streamer, or multi-platform content creator
- You produce content on a regular schedule and need help staying organized
- You want agents covering writing, editing, community, and monetization
