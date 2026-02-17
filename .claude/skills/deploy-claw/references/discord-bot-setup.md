# Discord Bot Setup Guide

Step-by-step guide for creating Discord bot accounts for your team agents.

## Prerequisites

- A Discord account with admin access to the target guild (server)
- One bot application per agent (each agent needs its own token)

## Steps (repeat for each agent)

### 1. Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Name it after your agent (e.g., "Ops Bot", "Customer Bot")
4. Click **Create**

### 2. Make the Bot Private

1. In the left sidebar, click **Installation**
2. Set **Install Link** to **None**
3. In the left sidebar, click **Bot**
4. Disable **Public Bot** (this prevents anyone else from adding your bot to their servers)
5. Click **Save Changes**

### 3. Configure the Bot

1. On the Bot page, under **Privileged Gateway Intents**, enable:
   - **Message Content Intent** (required for reading messages)
2. Optionally enable:
   - **Server Members Intent** (for member info tools)
   - **Presence Intent** (for presence features)
3. Click **Save Changes**

### 4. Copy the Bot Token

1. On the Bot page, click **Reset Token** (or **Copy** if visible)
2. Save this token — you'll need it for `discordToken` in your team definition
3. **Never share or commit tokens to version control**

### 5. Generate the Invite URL

1. In the left sidebar, click **OAuth2** > **URL Generator**
2. Under **Scopes**, select:
   - `bot`
   - `applications.commands`
3. Under **Bot Permissions**, select:
   - Send Messages
   - Send Messages in Threads
   - Embed Links
   - Attach Files
   - Read Message History
   - Add Reactions
   - Use External Emojis
   - Manage Messages (for pins)
   - Manage Threads
   - Create Public Threads
   - Create Private Threads
4. Copy the generated URL at the bottom

### 6. Invite the Bot to Your Guild

1. Open the generated URL in your browser
2. Select your target guild from the dropdown
3. Click **Authorize**
4. Complete the CAPTCHA

### 7. Get the Guild ID

1. In Discord, go to **User Settings** > **Advanced** > enable **Developer Mode**
2. Right-click your server name in the sidebar
3. Click **Copy Server ID**
4. Use this as `discord.guildId` in your team definition

## Token Format

A valid Discord bot token looks like:

```
YOUR_BOT_ID.TIMESTAMP.HMAC_TOKEN_HERE
```

It has three segments separated by dots. The validate script checks for this format.

## Troubleshooting

| Issue                   | Fix                                                              |
| ----------------------- | ---------------------------------------------------------------- |
| Bot appears offline     | Check that the token is correct and the gateway is running       |
| Bot can't read messages | Ensure **Message Content Intent** is enabled in the portal       |
| Bot can't send messages | Check channel permissions — bot needs Send Messages              |
| "Missing Access" errors | Re-invite with the correct permissions using step 5              |
| Bot responds to itself  | Set `allowBots: false` in config (default) or use agent bindings |

## Security Notes

- Each agent **must** have its own bot token — never share tokens between agents
- Store tokens in the team definition file, not in environment variables or code
- The `validate_team.py` script checks token format but cannot verify validity (that requires connecting to Discord)
