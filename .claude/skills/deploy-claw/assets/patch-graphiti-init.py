"""Patch graphiti server zep_graphiti.py to properly close client after init."""

FILEPATH = '/opt/graphiti/src/graph_service/zep_graphiti.py'

with open(FILEPATH, 'r') as f:
    content = f.read()

# Fix initialize_graphiti to close the client after building indices
old = '''async def initialize_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await client.build_indices_and_constraints()'''

new = '''async def initialize_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    try:
        await client.build_indices_and_constraints()
    finally:
        await client.close()'''

if old in content:
    content = content.replace(old, new)
    with open(FILEPATH, 'w') as f:
        f.write(content)
    print(f'Patched {FILEPATH}')
else:
    print(f'WARNING: Could not find target in {FILEPATH}')
