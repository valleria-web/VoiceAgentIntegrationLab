# SPRINT 2 — PROMPT 002 / PART 2
## First ElevenLabs Agent + `get_order` Webhook Tool

### Project

Voice Agent Integration Lab

### Branch

Expected branch:

sprint-2

Before modifying anything:

1. confirm the current Git branch;
2. inspect repository status;
3. read:

dev-docs/Voice Agent Integration Lab USMT v01.md

4. review the completed Sprint 2 / Prompt 001 implementation;
5. review Sprint 2 / Prompt 002 / Part 1 evidence.

The frozen USMT is authoritative and MUST NOT be modified.

---

# 1. Verified baseline

The following has already been proven:

Python
→ FastAPI
→ Application Service
→ Mock Enterprise Adapter

Canonical endpoint:

GET /orders/1111

returns:

{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}

Unknown:

GET /orders/9999

returns HTTP 404:

{
  "detail": "Order not found"
}

The endpoint has also been successfully exposed through a Cloudflare Quick Tunnel and verified publicly.

The Quick Tunnel hostname is temporary and MUST NOT be hardcoded or reused from previous runs.

Existing tests:

3 passed

---

# 2. Objective

Establish the first real tool-backed interaction:

User
→ ElevenLabs Agent
→ `get_order`
→ Webhook Tool Invocation
→ Cloudflare Quick Tunnel
→ FastAPI
→ Application Service
→ Mock Enterprise Adapter
→ Structured Result
→ ElevenLabs Agent
→ User-facing voice response

This will provide the first real runtime evidence corresponding to the USMT boundary:

ToolInvocationReceived

However, this ticket does NOT implement the USMT state machine in code.

---

# 3. Important implementation strategy

This ticket contains a HUMAN DASHBOARD CHECKPOINT.

Do NOT attempt to automate ElevenLabs Agent creation through the ElevenLabs API.

Do NOT modify API-key permissions for ElevenAgents.

Do NOT create the Agent programmatically.

The user will create and configure the first Agent manually in the ElevenLabs dashboard.

The purpose is to understand the ElevenLabs Agent + Tool model directly before automating it in later work.

Codex should:

- verify the local system;
- help prepare the public endpoint;
- preserve the existing application;
- provide runtime evidence;
- review results after the user performs the ElevenLabs dashboard configuration.

---

# 4. Application-code constraint

Prefer ZERO application code changes.

The existing endpoint is already sufficient for the first Webhook Tool.

Do NOT modify:

src/application/order_service.py
src/adapters/mock_enterprise.py

Do NOT modify:

src/main.py

unless a verified incompatibility with the ElevenLabs webhook request is observed during the real integration.

Do not proactively anticipate such a problem.

Observe first.

---

# 5. Pre-integration verification

Run:

python --version

Run the existing test suite.

Required:

3 passed

Then start FastAPI:

.\venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000

Verify:

GET http://127.0.0.1:8000/orders/1111

returns the canonical payload.

---

# 6. Public tunnel

Start a new Cloudflare Quick Tunnel:

cloudflared tunnel --url http://localhost:8000

Capture the newly generated runtime hostname:

https://<temporary-host>.trycloudflare.com

Verify:

GET https://<temporary-host>.trycloudflare.com/orders/1111

returns HTTP 200 and the canonical payload.

Do NOT persist this hostname in:

- source code;
- .env;
- USMT;
- permanent documentation;
- configuration committed to Git.

The hostname exists only for the current runtime session.

---

# 7. HUMAN CHECKPOINT — Create ElevenLabs Agent

At this point STOP remote automation.

The user must create the Agent manually in the ElevenLabs dashboard.

Create:

Name:

Voice Agent Integration Lab

Template:

Blank template

The first agent should be intentionally minimal.

Do not configure knowledge bases, workflows, multiple tools, RAG, MCP, phone integration, or external services.

---

# 8. Agent language / business context

This first demo represents a Brazilian customer-support scenario.

Preferred first message:

Olá! Posso ajudar a consultar o status do seu pedido. Qual é o número do pedido?

The Agent should be able to converse naturally in Portuguese.

Avoid unnecessary persona or marketing copy.

The purpose is technical integration testing.

---

# 9. Agent system prompt

Use a minimal system prompt equivalent to:

You are a customer-support assistant for a Brazilian e-commerce integration demo.

Your responsibility in this experiment is limited to helping users check order status.

When the user asks about the status or expected delivery of an order:

1. obtain the order ID from the user;
2. call the `get_order` tool;
3. answer using only the data returned by the tool.

Do not invent order information.

Do not guess an order status.

Do not claim that an order exists unless the tool returns it successfully.

If the order cannot be found, tell the user that the order was not found and ask them to verify the order number.

If the tool fails, do not represent the operation as successful.

Keep responses concise and natural.

This prompt intentionally reflects the USMT invariant:

No false success.

Do not include internal USMT terminology in user-facing responses.

---

# 10. Create Webhook Tool

Inside the Agent configuration choose:

Add Tool
→ Webhook

Configure:

Name:

get_order

Description:

Retrieve the current status and estimated delivery date of an order when the customer asks where an order is or when it is expected to arrive.

Method:

GET

URL:

https://<CURRENT-QUICK-TUNNEL-HOST>/orders/{order_id}

IMPORTANT:

Use the CURRENT runtime Cloudflare hostname.

Do not use a hostname from an earlier tunnel session.

---

# 11. Path parameter

Define one path parameter:

Identifier:

order_id

Type:

string

Required:

true

Description:

The order identifier provided by the customer. Use the exact identifier stated by the customer and do not invent or transform it.

The URL must resolve dynamically as:

/orders/{order_id}

For example:

User says:

1111

Tool request becomes:

GET /orders/1111

---

# 12. No additional parameters

Do NOT add:

- query parameters;
- request body;
- customer ID;
- authentication data;
- email;
- address;
- conversation metadata;
- artificial trace IDs.

This first Tool contract requires only:

order_id

---

# 13. Tool-assignment verification

Confirm that `get_order` is actually available to:

Voice Agent Integration Lab

Do not merely create the tool in the workspace without attaching/making it available to the Agent.

The Agent must be capable of selecting it during the conversation.

---

# 14. First canonical conversation

Use the ElevenLabs dashboard test/conversation interface.

Speak or type something equivalent to:

Onde está meu pedido 1111?

Expected reasoning behavior:

User intent
→ order status request
→ extract order_id = "1111"
→ call get_order
→ receive structured response
→ answer based on response

Expected backend request:

GET /orders/1111

Expected backend result:

{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}

Expected semantic response from the Agent:

- order 1111 is in transit;
- estimated delivery is August 28, 2026.

Exact natural-language wording does not need to be predetermined.

The factual content must match the tool result.

---

# 15. Required runtime evidence

Observe both sides.

## ElevenLabs evidence

Confirm that the conversation shows a `get_order` tool invocation with:

order_id = 1111

If the dashboard exposes tool-call details, inspect them.

Do not expose account secrets.

## Python/FastAPI evidence

Observe the Uvicorn runtime.

Confirm that an HTTP request reaches:

GET /orders/1111

through the active public tunnel.

The combination of:

ElevenLabs tool-call evidence
+
FastAPI request evidence

is our first evidence that an actual ElevenLabs Tool Invocation crossed the system boundary.

---

# 16. First USMT boundary observation

If and only if both pieces of evidence are present:

1. ElevenLabs shows `get_order` was invoked;
2. FastAPI receives the corresponding request;

we may state:

Observed runtime event:

ToolInvocationReceived

IMPORTANT:

This is an observed event classification.

Do NOT implement:

- `Operation`;
- `Received` state object;
- protocol engine;
- transition record;
- operation_id;
- trace_id.

The runtime state-machine implementation belongs to a later ticket.

---

# 17. End-to-end completion observation

The first canonical interaction is manually considered end-to-end successful only if:

1. User requests order 1111.
2. Agent calls `get_order`.
3. FastAPI receives `/orders/1111`.
4. Mock enterprise returns the canonical record.
5. ElevenLabs receives the tool result.
6. Agent responds to the user.
7. Agent response accurately reflects:
   - `in_transit`
   - `2026-08-28`

This provides evidence corresponding to the USMT happy path, but it does NOT mean runtime state enforcement has been implemented.

Use wording such as:

Manual evidence supports an end-to-end completed interaction.

Do not claim:

Canonical Operation engine implemented.

---

# 18. Negative test — unknown order

Run a second conversation:

Onde está meu pedido 9999?

Expected:

Agent
→ get_order(order_id="9999")
→ public endpoint
→ FastAPI
→ HTTP 404

The Agent must NOT invent an order.

The user-facing response should communicate that the order was not found or could not be retrieved and invite the user to verify the identifier.

This directly exercises the USMT invariant:

No false success.

---

# 19. Tool-selection test

Run one non-order statement, for example:

Olá, tudo bem?

Expected:

The Agent MAY answer conversationally.

It SHOULD NOT invoke `get_order`.

This establishes that the tool is selected because of relevant intent rather than called indiscriminately.

---

# 20. Evidence matrix

At the end of testing, report this matrix:

CASE A — Canonical order

Input:
Onde está meu pedido 1111?

Tool selected:
yes/no

Parameter:
1111

FastAPI request observed:
yes/no

HTTP result:
200 / other

Agent grounded in returned payload:
yes/no

CASE B — Unknown order

Input:
Onde está meu pedido 9999?

Tool selected:
yes/no

FastAPI request observed:
yes/no

HTTP result:
404 / other

Agent invented order data:
yes/no

CASE C — Non-order conversation

Input:
Olá, tudo bem?

get_order invoked:
yes/no

Expected:
no

---

# 21. Failure handling

If the Agent does not call the tool:

Do NOT modify application architecture.

Inspect first:

- tool assignment;
- tool name;
- tool description;
- path parameter description;
- Agent system prompt.

Make the smallest configuration correction supported by evidence.

If the Webhook call fails:

Inspect:

- current Quick Tunnel process;
- current hostname;
- FastAPI process;
- generated request path;
- ElevenLabs tool error.

Do not guess.

If ElevenLabs sends a request shape incompatible with our endpoint:

Capture the non-sensitive evidence first.

Only then propose the smallest code change.

Do not refactor unrelated layers.

---

# 22. Security

The current API contains only deterministic mock data.

Still confirm:

- `.env` remains ignored;
- `ELEVENLABS_API_KEY` is not exposed;
- Cloudflare URL contains no secret;
- no real customer information is used;
- no secret is entered into URL parameters;
- no secret is persisted in Git.

Do not print API keys.

---

# 23. Explicitly out of scope

Do NOT implement:

- create_support_ticket;
- POST enterprise operations;
- database;
- authentication architecture;
- Operation class;
- operation_id;
- trace_id;
- state-machine engine;
- transition records;
- persistence;
- FastAPI refactoring;
- production deployment;
- permanent Cloudflare tunnel;
- ElevenLabs Agent creation via API;
- agent configuration automation;
- multiple tools;
- frontend.

This ticket proves ONE tool-backed read operation.

---

# 24. Tests after integration

After completing the ElevenLabs runtime test:

Stop the temporary Cloudflare tunnel.

Stop Uvicorn.

Run the local automated suite again.

Expected:

3 passed

Confirm that integration experimentation did not regress the enterprise endpoint.

---

# 25. Git verification

Run:

git status

Confirm:

- `.env` ignored;
- `venv/` ignored;
- generated audio ignored;
- no temporary tunnel URL persisted;
- no ElevenLabs runtime credential persisted;
- frozen USMT unchanged.

Do not commit automatically.

---

# 26. Acceptance criteria

This ticket passes only when:

- frozen USMT remains unchanged;
- existing local tests remain `3 passed`;
- current FastAPI endpoint works;
- current Cloudflare Quick Tunnel works;
- ElevenLabs Agent exists using a Blank/minimal configuration;
- `get_order` exists as a Webhook Tool;
- `order_id` is correctly defined as a required path parameter;
- the tool is available to the Agent;
- request for order `1111` causes a real `get_order` invocation;
- FastAPI receives `/orders/1111`;
- the tool returns the canonical enterprise payload;
- Agent response reflects the real returned values;
- unknown order `9999` does not generate fabricated order information;
- unrelated conversation does not trigger `get_order`;
- no runtime USMT state machine has been implemented;
- no secrets enter Git.

---

# 27. Final report

Provide:

## Agent

Agent name

Do not expose credentials.

## Tool configuration

Tool:
get_order

Method:
GET

Parameter:
order_id

Do not persist the temporary tunnel hostname in source code.

## Canonical runtime test

Report:

User request
Tool invocation observed
Tool parameter
FastAPI request
HTTP result
Enterprise payload
Agent final response summary

## Unknown-order test

Report:

Tool invocation
HTTP result
Agent behavior
Whether false success occurred

## Tool-selection test

Report whether `get_order` was incorrectly invoked for the unrelated message.

## USMT evidence

State whether:

ToolInvocationReceived

was directly observed through correlated ElevenLabs + FastAPI runtime evidence.

State whether manual end-to-end evidence supports successful completion.

Do NOT claim that runtime state enforcement exists.

## Tests

Report final local pytest result.

## Source changes

If none:

Application source changes: none.

If any were required, list exact evidence and smallest change made.

## Security

Confirm:

.env ignored
venv ignored
no ElevenLabs secret exposed
no permanent Cloudflare URL persisted
USMT unchanged

## Result

Finish with exactly one:

SPRINT 2 / PROMPT 002 / PART 2 — PASSED

or

SPRINT 2 / PROMPT 002 / PART 2 — BLOCKED

If blocked, provide only evidence-backed blockers.