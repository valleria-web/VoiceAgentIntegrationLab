# SPRINT 2 — PROMPT 001
## Minimal Enterprise Endpoint — `get_order`

### Project

**Voice Agent Integration Lab**

### Expected branch

`sprint-2`

Before modifying anything:

1. confirm the current Git branch;
2. inspect the current repository;
3. read the frozen canonical reference:

`dev-docs/Voice Agent Integration Lab USMT v01.md`

Do not modify the frozen USMT.

---

# 1. Context

Sprint 1 established a successful real Python → ElevenLabs Text-to-Speech integration.

That work is complete and must remain intact.

Sprint 2 begins preparation for the first tool-backed operation.

The future flow will be:

User
→ ElevenLabs Agent
→ `get_order` Tool Invocation
→ Python/FastAPI
→ Mock Enterprise System
→ structured result
→ ElevenLabs Agent
→ voice response

However, this ticket implements **only the Python enterprise endpoint**.

There is no ElevenLabs Agent integration yet.

---

# 2. USMT boundary

The frozen USMT defines a formal `Operation` beginning when:

`ToolInvocationReceived`

is received from an authorized ElevenLabs tool.

That event does **not exist yet in this ticket**.

Therefore:

- do not implement `Operation`;
- do not implement protocol states;
- do not generate `operation_id`;
- do not generate `trace_id`;
- do not implement transition records;
- do not implement ElevenLabs tool logic.

This ticket creates the deterministic downstream service that a future tool invocation will call.

---

# 3. Ticket objective

Implement and verify one minimal enterprise operation:

`GET /orders/{order_id}`

For the canonical test order:

`1111`

the endpoint SHALL return:

```json
{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}