# Graphiti Knowledge Graph Memory

Graphiti provides Layer 3 persistent memory via a Neo4j-backed knowledge graph, letting agents remember facts, relationships, and context across sessions.

## Three-Layer Memory Architecture

| Layer                    | Storage                  | Scope               | Persistence |
| ------------------------ | ------------------------ | ------------------- | ----------- |
| **L1 — Workspace**       | SOUL.md, MEMORY.md, etc. | Per-agent           | File-based  |
| **L2 — Session**         | Conversation history     | Per-session         | Ephemeral   |
| **L3 — Knowledge Graph** | Neo4j + Graphiti         | Shared or per-agent | Persistent  |

Graphiti is Layer 3 — it complements, not replaces, workspace files and session memory.

## Docker Services

The `docker-compose.team.yml` template includes two Graphiti-related services under the `graphiti` profile:

### Neo4j

- Image: `neo4j:5-community`
- Ports: `7474` (browser), `7687` (bolt)
- Plugin: APOC
- Health check: `cypher-shell "RETURN 1"`
- Volume: `neo4j-data` (named, persistent)

### Graphiti API

- Image: `zepai/graphiti`
- Port: `8000`
- Depends on Neo4j health check
- Requires `OPENAI_API_KEY` for embeddings

## Enabling Graphiti

1. In your team definition, set:

   ```json
   "graphiti": {
     "enabled": true,
     "neo4jPassword": "your-strong-password",
     "openaiApiKey": "sk-your-openai-key"
   }
   ```

2. Deploy with the graphiti profile:

   ```bash
   docker compose -f docker-compose.team.yml --profile graphiti up -d
   ```

3. Verify services are healthy:

   ```bash
   # Neo4j
   curl -s http://localhost:7474 | head -1

   # Graphiti API
   curl -s http://localhost:8000/healthcheck
   ```

## Agent Usage

Agents interact with Graphiti through shell tools:

- **`graphiti-search.sh <query>`** — Semantic search over the knowledge graph
- **`graphiti-log.sh <fact>`** — Store a new fact or relationship

These tools are typically provided as agent skills. When Graphiti is enabled, agents can:

- Remember customer preferences and order history
- Track supplier reliability and lead times
- Build up institutional knowledge over time

## Without Docker

If running natively (no Docker), you need:

1. A Neo4j 5 instance (local or cloud)
2. The Graphiti API server pointing at your Neo4j
3. Set `NEO4J_URI`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY` in your environment

## Troubleshooting

| Issue                  | Fix                                                              |
| ---------------------- | ---------------------------------------------------------------- |
| Neo4j won't start      | Check disk space and port 7687 availability                      |
| Graphiti can't connect | Wait for Neo4j health check to pass before starting Graphiti     |
| Embedding errors       | Verify OPENAI_API_KEY is valid and has credits                   |
| Slow queries           | Check Neo4j memory settings; default container limits may be low |
