# Model Provider Configuration

How to configure LLM providers in team definitions. OpenClaw supports any OpenAI-compatible API, Anthropic, Google Gemini, AWS Bedrock, and more.

## Provider Config Structure

```json
"model": {
  "provider": "provider-name",
  "baseUrl": "https://api.example.com/v1",
  "apiKey": "sk-...",
  "api": "openai-completions",
  "models": [{
    "id": "model-id",
    "name": "Display Name",
    "contextWindow": 131072,
    "maxTokens": 16384,
    "input": ["text"],
    "reasoning": false
  }]
}
```

## API Types

| Value                     | Use for                                 |
| ------------------------- | --------------------------------------- |
| `openai-completions`      | OpenAI-compatible APIs (most providers) |
| `openai-responses`        | OpenAI Responses API                    |
| `anthropic-messages`      | Anthropic and Anthropic-compatible APIs |
| `google-generative-ai`    | Google Gemini                           |
| `bedrock-converse-stream` | AWS Bedrock                             |
| `github-copilot`          | GitHub Copilot                          |

## Popular Providers

Present these three as the default choices when asking the user which provider to use.

### OpenAI

```json
"model": {
  "provider": "openai",
  "baseUrl": "https://api.openai.com/v1",
  "apiKey": "sk-your-key",
  "api": "openai-completions",
  "models": [{
    "id": "gpt-4o",
    "name": "GPT-4o",
    "contextWindow": 128000,
    "maxTokens": 16384,
    "input": ["text", "image"],
    "reasoning": false
  }]
}
```

### Anthropic

```json
"model": {
  "provider": "anthropic",
  "baseUrl": "https://api.anthropic.com",
  "apiKey": "sk-ant-your-key",
  "api": "anthropic-messages",
  "models": [{
    "id": "claude-sonnet-4-5-20250929",
    "name": "Claude Sonnet 4.5",
    "contextWindow": 200000,
    "maxTokens": 8192,
    "input": ["text", "image"],
    "reasoning": false
  }]
}
```

### Google Gemini

```json
"model": {
  "provider": "google",
  "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
  "apiKey": "your-key",
  "api": "google-generative-ai",
  "models": [{
    "id": "gemini-2.5-pro",
    "name": "Gemini 2.5 Pro",
    "contextWindow": 1048576,
    "maxTokens": 8192,
    "input": ["text", "image"],
    "reasoning": false
  }]
}
```

## Other Providers

These are available when the user types a custom choice or asks for a specific provider.

### OpenRouter

```json
"model": {
  "provider": "openrouter",
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKey": "sk-or-your-key",
  "api": "openai-completions",
  "models": [{
    "id": "anthropic/claude-sonnet-4.5",
    "name": "Claude Sonnet 4.5 (via OpenRouter)",
    "contextWindow": 200000,
    "maxTokens": 8192,
    "input": ["text", "image"],
    "reasoning": false
  }]
}
```

### DeepSeek

```json
"model": {
  "provider": "deepseek",
  "baseUrl": "https://api.deepseek.com/v1",
  "apiKey": "sk-your-key",
  "api": "openai-completions",
  "models": [{
    "id": "deepseek-chat",
    "name": "DeepSeek V3",
    "contextWindow": 65536,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Groq

```json
"model": {
  "provider": "groq",
  "baseUrl": "https://api.groq.com/openai/v1",
  "apiKey": "gsk_your-key",
  "api": "openai-completions",
  "models": [{
    "id": "llama-3.3-70b-versatile",
    "name": "Llama 3.3 70B",
    "contextWindow": 131072,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Mistral

```json
"model": {
  "provider": "mistral",
  "baseUrl": "https://api.mistral.ai/v1",
  "apiKey": "your-key",
  "api": "openai-completions",
  "models": [{
    "id": "mistral-large-latest",
    "name": "Mistral Large",
    "contextWindow": 131072,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Kimi (Moonshot)

```json
"model": {
  "provider": "kimi",
  "baseUrl": "https://api.moonshot.ai/v1",
  "apiKey": "sk-your-key",
  "api": "openai-completions",
  "models": [{
    "id": "kimi-k2.5",
    "name": "Kimi K2.5",
    "contextWindow": 131072,
    "maxTokens": 16384,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Together AI

```json
"model": {
  "provider": "together",
  "baseUrl": "https://api.together.xyz/v1",
  "apiKey": "your-key",
  "api": "openai-completions",
  "models": [{
    "id": "meta-llama/Llama-3.1-70B-Instruct-Turbo",
    "name": "Llama 3.1 70B Turbo",
    "contextWindow": 131072,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Fireworks

```json
"model": {
  "provider": "fireworks",
  "baseUrl": "https://api.fireworks.ai/inference/v1",
  "apiKey": "your-key",
  "api": "openai-completions",
  "models": [{
    "id": "accounts/fireworks/models/llama-v3p1-70b-instruct",
    "name": "Llama 3.1 70B",
    "contextWindow": 131072,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### Ollama (local)

```json
"model": {
  "provider": "ollama",
  "baseUrl": "http://127.0.0.1:11434/v1",
  "apiKey": "ollama",
  "api": "openai-completions",
  "models": [{
    "id": "llama3.1:70b",
    "name": "Llama 3.1 70B",
    "contextWindow": 131072,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

### MiniMax

```json
"model": {
  "provider": "minimax",
  "baseUrl": "https://api.minimax.chat/v1",
  "apiKey": "your-key",
  "api": "openai-completions",
  "models": [{
    "id": "MiniMax-M2.1",
    "name": "MiniMax M2.1",
    "contextWindow": 200000,
    "maxTokens": 8192,
    "input": ["text"],
    "reasoning": false
  }]
}
```

## Field Defaults

Most fields are optional with sensible defaults:

- `contextWindow` defaults to 128000
- `maxTokens` defaults to min(8192, contextWindow)
- `input` defaults to `["text"]`
- `reasoning` defaults to `false`
- `cost` defaults to all zeros (free tier / unmetered)

The only required fields are `provider`, `baseUrl`, `api`, and at least one model with an `id`.

## Agent Model Reference

In agent configs, models are referenced as `provider/model-id`:

```json
"model": { "primary": "openai/gpt-4o" }
```

The `generate_config.py` script builds this automatically from the team definition's `model.provider` and `model.models[0].id`.
