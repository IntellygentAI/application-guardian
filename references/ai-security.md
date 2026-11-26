# AI and LLM security

If the application has no model, retrieval, tool use, or agent runtime, mark this domain NOT APPLICABLE.

Prompt injection cannot be removed by stronger system-prompt wording. Design the product so a manipulated model still cannot cross a security boundary.

## Prompt injection and AI abuse

Inspect every model input and tool integration. Test direct and indirect injection with synthetic content in an authorised environment:

- Instructions to ignore the system prompt or reveal configuration
- Conflicting instructions inside an uploaded document or retrieved page
- A request for another user's conversation history
- A request to perform an unauthorised administrative action or bypass a quota
- A request for data outside the caller's permissions

User content and retrieved documents are untrusted. System prompts contain no live secrets. Sensitive tools enforce authorisation independently of the model. The model cannot grant itself permissions. Generated commands are validated before execution. Sensitive actions require confirmation where the product requires it. Network and filesystem access are restricted.

An AI reply that refuses a malicious sentence is not evidence that its tools are safe. Test the tool boundary directly.

## Data isolation

Check whether the model can receive another user's conversations, another organisation's documents, private vector records, administrator notes, restricted files, or a previous session from a different account.

Audit retrieval, vector stores, embedding storage, conversation history, caches, tool responses, memory, and shared agent workspaces.

Enforce access control before data is retrieved or placed in the prompt. Tenant isolation lives outside the model.

## Cost and resource abuse

Test long prompts, repeated expensive requests, large uploads, excessive output, unbounded agent loops, repeated tool calls, concurrent model requests, and requests over the account quota.

Require input size limits, output token limits, per-account quotas, concurrency limits, timeouts, tool budgets, agent iteration limits, cost monitoring, and cancellation.

One user must not be able to create uncontrolled infrastructure or provider cost.

## Output handling

Model output is data. HTML, Markdown, SQL, shell, and file paths produced by the model are validated before they are rendered, queried, or executed. A structured tool argument is checked against a schema. The model does not choose the allowlist.

## Supply chain

Untrusted models, plugins, and downloaded knowledge files are covered in [supply-chain-security.md](supply-chain-security.md). MCP tools and delegation are covered in [agent-mcp-security.md](agent-mcp-security.md).
