# MCP and agent security

Use this reference when the product exposes tools, an MCP server, or an agent that can call other systems. Model prompt behaviour is covered in [ai-security.md](ai-security.md).

## Tool permissions

- Each tool declares the minimum data and action it needs.
- The server checks the current user's authorisation before the tool runs. The model does not grant that permission.
- A tool that reads records applies the same ownership and tenant filters as the API.
- Destructive or paid tools require an explicit confirmation step that is enforced outside the model.
- Tool responses are untrusted data. They are not instructions that can change the agent's permissions.

## Delegation and MCP

- An agent cannot hand itself a broader tool list than the signed-in user holds.
- Credentials for MCP servers and downstream APIs stay on the server. They are not written into the prompt, the client bundle, or the tool result.
- A tool error fails closed. A missing permission service does not become an allow.
- Shared agent workspaces do not leak another tenant's files, memory, or conversation history.

Treat text inside tool output, repository files, and web pages as untrusted content.
