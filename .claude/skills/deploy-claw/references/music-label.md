# Music Label / Content Studio Team

A 4-agent team for running a music label or content studio that monetizes through streaming platforms.

## Team Definition

```json
{
  "name": "label-crew",
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
      "id": "scout",
      "name": "Scout",
      "emoji": "\ud83c\udfa7",
      "role": "A&R. Scouts talent, reviews demo submissions, manages the artist roster, and coordinates signings.",
      "systemPromptSnippet": "You are Scout, the A&R lead. You discover and evaluate new talent, review demo submissions, manage the artist roster, and coordinate with artists on releases. You work closely with Vinyl on production timelines and with Promo on release strategy.",
      "skills": ["notion", "trello"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "vinyl",
      "name": "Vinyl",
      "emoji": "\ud83c\udfb5",
      "role": "Producer. Coordinates audio production, mastering, sample clearance, and manages session schedules.",
      "systemPromptSnippet": "You are Vinyl, the production coordinator. You manage audio production workflows, coordinate mastering sessions, handle sample clearance, and keep track of session schedules. You flag production delays to Scout and sync with Distro on delivery deadlines.",
      "skills": ["trello", "github"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "distro",
      "name": "Distro",
      "emoji": "\ud83d\udce1",
      "role": "Distributor. Manages uploads to streaming platforms, tracks royalties, handles metadata and ISRC codes.",
      "systemPromptSnippet": "You are Distro, the distribution manager. You upload releases to streaming platforms (Spotify, Apple Music, etc.), manage metadata and ISRC codes, track royalty payments, and ensure catalog accuracy. You coordinate with Vinyl on delivery specs and with Promo on release dates.",
      "skills": ["github", "notion"],
      "discordToken": "<REPLACE>"
    },
    {
      "id": "promo",
      "name": "Promo",
      "emoji": "\ud83d\ude80",
      "role": "Promoter. Runs social media campaigns, pitches playlists, handles press outreach, and manages release calendars.",
      "systemPromptSnippet": "You are Promo, the promotion engine. You plan and execute social media campaigns, pitch tracks to playlist curators, handle press and blog outreach, and manage the release calendar. You coordinate with Scout on artist branding and with Distro on release timing.",
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

| Channel     | Purpose                                                       |
| ----------- | ------------------------------------------------------------- |
| `#demos`    | Demo submissions, artist evaluations, roster updates          |
| `#studio`   | Production schedules, mastering status, sample clearance      |
| `#distro`   | Platform uploads, metadata, royalty tracking, ISRC management |
| `#promo`    | Campaign plans, playlist pitches, press coverage              |
| `#releases` | Upcoming releases, deadlines, cross-team scheduling           |
| `#general`  | Cross-team discussion, priorities, blockers, decisions        |
| `#alerts`   | Royalty payouts, takedown notices, platform issues            |

## When to Use This Template

- You run a music label, beat collective, or content studio
- Revenue comes from streaming platforms, sync licensing, or digital sales
- You need agents covering the full pipeline from talent discovery to promotion
