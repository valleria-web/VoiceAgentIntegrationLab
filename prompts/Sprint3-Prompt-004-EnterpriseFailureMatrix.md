# SPRINT 3 / PROMPT 004 — ENTERPRISE FAILURE MATRIX

## Project

**Voice Agent Integration Lab**

Expected working branch:

```text
sprint-3
```

---

# 1. Current baseline

The repository already contains four enterprise capabilities:

```text
GET  /orders/{order_id}
GET  /customers/{customer_id}
POST /support-tickets
GET  /support-tickets/{ticket_id}
POST /callbacks
GET  /callbacks/{callback_id}
```

Current canonical entities and operations:

```text
Order:
1111

Customer:
2001

First support ticket in a fresh runtime:
TCK-3001

First callback in a fresh runtime:
CBK-4001
```

Current test baseline:

```text
16 passed
0 failed
```

Current architecture separates:

```text
src/main.py
    HTTP / FastAPI interface and request validation

src/application/
    application services

src/adapters/mock_enterprise.py
    deterministic mock enterprise data and mutable runtime state
```

The canonical document:

```text
dev-docs/Voice Agent Integration Lab USMT v01.md
```

is **FROZEN**.

Read it before implementation only to respect its boundaries.

Do **NOT** modify, reinterpret, extend, or implement the USMT state machine during this ticket.

---

# 2. Objective

Complete the backend portion of **M3 — Enterprise Integration** by introducing and verifying a small, deterministic enterprise failure matrix.

This ticket must cover these failure classes:

```text
order not found
customer mismatch
enterprise API timeout
invalid request
```

The goal is not to build a generic error framework.

The goal is to make failure behavior explicit, observable, deterministic, and impossible to confuse with success.

This remains a backend-only ticket.

Do **NOT** configure ElevenLabs tools yet.

---

# 3. Failure matrix

The canonical failure behavior for this ticket is:

| Scenario | Canonical trigger | Expected HTTP result | Mutation allowed |
|---|---|---:|---|
| Order not found | unknown order `9999` | 404 | no |
| Customer mismatch | customer `2002` attempts to create a ticket for order `1111` | 409 | no |
| Enterprise API timeout | reserved mock order ID `TIMEOUT` | 504 | no |
| Invalid request | malformed/missing required POST payload | 422 | no |

Every failure must remain a failure.

No failure path may return a success status or create enterprise mutation.

---

# 4. Canonical order ownership

Introduce one explicit internal ownership relation:

```text
order 1111
belongs to
customer 2001
```

This ownership information is part of the mock enterprise model.

Do **NOT** change the existing public response for:

```text
GET /orders/1111
```

It must remain exactly:

```json
{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}
```

The ownership relation may be stored separately inside the mock enterprise adapter.

Do not add `customer_id` to the existing order response merely to support this ticket.

---

# 5. Secondary canonical customer

Add one additional valid customer to the mock enterprise data:

```text
customer_id:
2002
```

Expected customer:

```json
{
  "customer_id": "2002",
  "name": "Bruno Lima",
  "email": "bruno.lima@example.com",
  "status": "active"
}
```

This customer exists only to make the mismatch scenario semantically real.

`2002` is a valid customer, but does **NOT** own order `1111`.

Existing customer `2001` remains unchanged.

Existing unknown customer `9999` remains unknown.

---

# 6. Failure A — Order not found

The existing behavior:

```text
GET /orders/9999
```

must remain:

HTTP 404

```json
{
  "detail": "Order not found"
}
```

Additionally, support-ticket creation must no longer silently accept an unknown order.

This request:

```text
POST /support-tickets
```

with:

```json
{
  "customer_id": "2001",
  "order_id": "9999",
  "issue": "Delivery status follow-up"
}
```

must return:

HTTP 404

```json
{
  "detail": "Order not found"
}
```

No support ticket may be created.

No ticket identifier may be consumed.

A subsequent valid support-ticket creation in a fresh runtime must still receive:

```text
TCK-3001
```

if no prior successful ticket exists.

---

# 7. Failure B — Customer mismatch

A support ticket may only be created when the supplied customer owns the supplied order.

Canonical valid relation:

```text
customer 2001
owns order 1111
```

Canonical mismatch:

```text
customer 2002
does NOT own order 1111
```

This request:

```text
POST /support-tickets
```

with:

```json
{
  "customer_id": "2002",
  "order_id": "1111",
  "issue": "Delivery status follow-up"
}
```

must return:

HTTP 409 Conflict

with:

```json
{
  "detail": "Customer does not match order"
}
```

The error must be explicit enough for an API consumer to understand that both entities are valid but their relationship is invalid.

The mismatch must **NOT** create a support ticket.

The mismatch must **NOT** consume a ticket identifier.

Do not transform this condition into:

```text
404 Customer not found
404 Order not found
201 Created
```

---

# 8. Where the mismatch rule belongs

Preserve the established architecture:

```text
HTTP interface
    ↓
Application service
    ↓
Mock enterprise adapter
```

The mock enterprise adapter owns:

```text
customer data
order data
order/customer ownership data
mutable enterprise resources
```

The support-ticket application service owns the orchestration required to determine whether ticket creation is allowed.

The HTTP interface owns translation of application outcomes into HTTP responses.

Do **NOT** place the ownership decision directly inside the FastAPI route.

Do **NOT** hardcode:

```text
2001
1111
```

as a special-case `if` statement inside `src/main.py`.

The relation must be represented as enterprise data and evaluated through the existing application/adapter structure.

---

# 9. Failure C — Enterprise API timeout

Introduce one deterministic mock timeout trigger:

```text
order_id:
TIMEOUT
```

The reserved identifier:

```text
TIMEOUT
```

does not represent a real order.

It exists only as a deterministic test trigger for an upstream enterprise timeout.

Calling:

```text
GET /orders/TIMEOUT
```

must cause the mock enterprise adapter to represent an enterprise timeout condition.

The HTTP result must be:

HTTP 504 Gateway Timeout

```json
{
  "detail": "Enterprise API timeout"
}
```

Do **NOT** implement the timeout by sleeping for many seconds.

Do **NOT** use:

```text
time.sleep()
asyncio.sleep()
network calls
random delays
```

The timeout must be simulated immediately and deterministically through an explicit adapter-level failure signal/exception.

The purpose is to verify failure propagation, not wall-clock delay.

---

# 10. Timeout architecture

Use the smallest explicit implementation appropriate for the existing codebase.

A dedicated exception such as:

```text
EnterpriseTimeoutError
```

is acceptable if useful.

If introduced, keep it local and simple.

Expected conceptual flow:

```text
GET /orders/TIMEOUT
        ↓
application service
        ↓
mock enterprise adapter
        ↓
deterministic timeout signal
        ↓
application/HTTP translation
        ↓
HTTP 504
```

The HTTP route must not manufacture the timeout solely from the raw string `TIMEOUT`.

The timeout condition must originate in the enterprise adapter boundary.

Do not build a general-purpose exception hierarchy.

---

# 11. Failure D — Invalid request

Existing FastAPI/Pydantic validation behavior must remain authoritative for malformed request payloads.

At minimum, preserve:

```text
POST /support-tickets
```

with a missing required field:

```text
→ HTTP 422
```

and:

```text
POST /callbacks
```

with invalid phone, timezone-less datetime, or missing required field:

```text
→ HTTP 422
```

Invalid requests must not reach successful enterprise mutation.

Do not replace Pydantic validation with a custom validation framework.

---

# 12. No false success

This section is a central acceptance boundary.

For every failure scenario:

```text
order not found
customer mismatch
enterprise timeout
invalid request
```

all of the following must be true:

```text
success HTTP status is not returned
success resource is not fabricated
enterprise mutation does not occur
failure remains observable as failure
```

For mutating operations, failure must not consume the next deterministic identifier.

Example:

If the runtime begins with no support tickets and these requests occur:

```text
1. customer mismatch
2. unknown order
3. valid support-ticket creation
```

the valid support ticket must still be:

```text
TCK-3001
```

not:

```text
TCK-3003
```

This is evidence that failed operations did not mutate enterprise state.

This ticket still does **NOT** implement the USMT state machine.

It preserves the behavioral invariant only:

```text
reported success requires verified enterprise success
```

---

# 13. Scope of support-ticket validation

For `POST /support-tickets`, the application flow must now distinguish at least:

```text
valid customer + valid owned order
    → create ticket

valid customer + unknown order
    → Order not found

valid customer + valid order owned by another customer
    → Customer does not match order
```

The canonical valid case remains:

```text
customer_id = 2001
order_id = 1111
```

Do not add unrelated support-ticket workflow states such as:

```text
in_progress
resolved
closed
```

The created ticket still begins with:

```text
status = open
```

No SupportTicket state machine is introduced in this ticket.

---

# 14. Callback behavior

Callback creation remains unchanged in this ticket.

Do **NOT** add:

```text
customer mismatch validation for callbacks
customer existence enforcement for callbacks
duplicate callback detection
business-hours rules
callback conflict policy
```

The existing callback behavior is regression baseline only.

---

# 15. Tests

Add automated tests covering at least the following behaviors.

## TEST 1 — Secondary customer exists

```text
GET /customers/2002
```

Expected:

HTTP 200

```json
{
  "customer_id": "2002",
  "name": "Bruno Lima",
  "email": "bruno.lima@example.com",
  "status": "active"
}
```

---

## TEST 2 — Support ticket rejects unknown order

POST:

```text
/support-tickets
```

with:

```json
{
  "customer_id": "2001",
  "order_id": "9999",
  "issue": "Delivery status follow-up"
}
```

Expected:

HTTP 404

```json
{
  "detail": "Order not found"
}
```

Verify that no support ticket was created.

---

## TEST 3 — Support ticket rejects customer mismatch

POST:

```text
/support-tickets
```

with:

```json
{
  "customer_id": "2002",
  "order_id": "1111",
  "issue": "Delivery status follow-up"
}
```

Expected:

HTTP 409

```json
{
  "detail": "Customer does not match order"
}
```

Verify that no support ticket was created.

---

## TEST 4 — Failed ticket requests do not consume IDs

In a clean/reset test state:

1. submit the canonical customer mismatch;
2. submit the canonical unknown-order request;
3. submit the canonical valid ticket request.

The successful ticket must be:

```text
TCK-3001
```

This test is mandatory.

---

## TEST 5 — Enterprise timeout

```text
GET /orders/TIMEOUT
```

Expected:

HTTP 504

```json
{
  "detail": "Enterprise API timeout"
}
```

The request must complete through deterministic simulation.

Do not make the test depend on waiting for a real timeout.

---

## TEST 6 — Existing order-not-found behavior

```text
GET /orders/9999
```

must remain:

HTTP 404

```json
{
  "detail": "Order not found"
}
```

---

## TEST 7 — Invalid support-ticket request remains invalid

Submit a support-ticket POST missing a required field.

Expected:

```text
HTTP 422
```

Verify that no ticket state is created and no ticket ID is consumed.

---

## Regression

Run the complete existing test suite.

All existing:

```text
order tests
customer tests
support-ticket tests
callback tests
```

must continue to pass.

Expected baseline before this ticket:

```text
16 passed
0 failed
```

---

# 16. State reset and test isolation

The mock enterprise contains mutable in-memory state.

Tests must remain deterministic and isolated.

Use the smallest mechanism consistent with the existing test structure to ensure one test does not accidentally consume identifiers or leave mutable state that changes another test.

Do not add a database.

Do not introduce a large fixture framework if a small explicit reset mechanism already exists or is sufficient.

The production/runtime behavior may remain process-local.

---

# 17. Explicitly out of scope

Do **NOT** implement:

- ElevenLabs webhook configuration
- Agent tool configuration
- `create_support_ticket` ElevenLabs tool
- `schedule_callback` ElevenLabs tool
- real external enterprise APIs
- real network timeout behavior
- retry logic
- circuit breakers
- exponential backoff
- fallback providers
- customer mismatch rules for callbacks
- callback conflict policy
- support-ticket lifecycle state machine
- `operation_id`
- `trace_id`
- structured logging
- observability framework
- `Operation` object
- USMT runtime states
- state-machine transitions
- authentication
- authorization
- database persistence
- frontend
- deployment
- Docker
- generic repository framework
- generic enterprise abstraction
- unrelated refactoring

Do **NOT** modify:

```text
dev-docs/Voice Agent Integration Lab USMT v01.md
```

---

# 18. Implementation style

Keep the implementation small, explicit, and inspectable.

Use type annotations where appropriate.

Prefer existing project conventions.

Do not build an enterprise error framework.

Do not introduce abstractions merely because additional failure cases may exist later.

The failure path should be understandable by directly following:

```text
HTTP
→ application service
→ mock enterprise adapter
→ explicit outcome/failure
```

Preserve existing successful behavior exactly unless this prompt explicitly changes it.

---

# 19. Execution procedure

Before modifying code:

1. Confirm current branch.

Expected:

```text
sprint-3
```

2. Inspect the current repository structure.

3. Run the complete test suite.

Expected baseline:

```text
16 passed
0 failed
```

4. Read:

```text
dev-docs/Voice Agent Integration Lab USMT v01.md
```

only to preserve its frozen boundaries.

5. Inspect the existing order, customer, support-ticket, callback, and mock-enterprise implementation before choosing the smallest change.

Then implement the ticket.

After implementation:

1. Run the complete pytest suite.
2. Confirm existing order tests pass.
3. Confirm existing customer tests pass.
4. Confirm existing support-ticket tests pass.
5. Confirm existing callback tests pass.
6. Confirm all new failure-matrix tests pass.
7. If practical, start FastAPI manually and verify:

```text
GET /customers/2002
GET /orders/9999
GET /orders/TIMEOUT
```

8. Manually verify:

```text
POST /support-tickets
customer 2002 + order 1111
```

returns HTTP 409.

9. Manually verify:

```text
POST /support-tickets
customer 2001 + order 9999
```

returns HTTP 404.

10. Inspect git diff.
11. Inspect git status.
12. Confirm the USMT was not modified.
13. Confirm no secret/runtime artifact was added.

Do not commit automatically.

---

# 20. Acceptance criteria

PASS only if all of the following are true:

- [ ] Existing canonical order `1111` remains unchanged
- [ ] Existing canonical customer `2001` remains unchanged
- [ ] Customer `2002` exists and is valid
- [ ] Internal ownership relation defines order `1111` as owned by customer `2001`
- [ ] Public `GET /orders/1111` response remains unchanged
- [ ] `GET /orders/9999` returns HTTP 404
- [ ] Unknown-order error body remains exactly `{"detail":"Order not found"}`
- [ ] Support-ticket creation with order `9999` returns HTTP 404
- [ ] Customer `2002` + order `1111` returns HTTP 409
- [ ] Mismatch body is exactly `{"detail":"Customer does not match order"}`
- [ ] Customer mismatch does not create a ticket
- [ ] Unknown order does not create a ticket
- [ ] Failed ticket creation does not consume a ticket ID
- [ ] A subsequent first successful ticket remains `TCK-3001`
- [ ] `GET /orders/TIMEOUT` returns HTTP 504
- [ ] Timeout body is exactly `{"detail":"Enterprise API timeout"}`
- [ ] Timeout originates from the adapter boundary, not a raw FastAPI route special case
- [ ] Timeout simulation does not sleep or call a network
- [ ] Invalid request remains HTTP 422
- [ ] Invalid request does not mutate enterprise state
- [ ] No failure path returns false success
- [ ] HTTP interface remains thin
- [ ] Application service owns support-ticket orchestration
- [ ] Mock enterprise adapter owns entity/ownership data and timeout simulation
- [ ] Existing callback behavior remains unchanged
- [ ] Existing support-ticket successful behavior remains unchanged
- [ ] Complete pytest suite passes
- [ ] Frozen USMT remains unchanged
- [ ] No ElevenLabs tool was configured
- [ ] No Operation/state-machine/traceability implementation was introduced
- [ ] No secrets were exposed

---

# 21. Final report

At completion report exactly this structure:

```text
SPRINT 3 / PROMPT 004 — ENTERPRISE FAILURE MATRIX


Status:

PASS or FAIL


Branch:

<current branch>


Python:

<version>


Files created:

<list>


Files modified:

<list>


Baseline tests:

<count passed / failed>


Final tests:

<count passed / failed>


Secondary customer result:

<HTTP status + body>


Order-not-found result:

<HTTP status + body>


Support-ticket unknown-order result:

<HTTP status + body>


Customer-mismatch result:

<HTTP status + body>


Mismatch mutation check:

<result>


Failed-ID-consumption check:

<result>


Enterprise-timeout result:

<HTTP status + body>


Invalid-request result:

<HTTP status>


Order regression:

PASS or FAIL


Customer regression:

PASS or FAIL


Support-ticket regression:

PASS or FAIL


Callback regression:

PASS or FAIL


USMT modified:

yes/no


Secrets exposed:

yes/no


Architecture summary:

State briefly where:

- HTTP error translation lives
- support-ticket orchestration lives
- order/customer ownership data lives
- timeout simulation originates


No-false-success summary:

State whether:

- unknown order
- customer mismatch
- enterprise timeout
- invalid request

all remain failures and avoid unintended enterprise mutation.


Scope confirmation:

Explicitly confirm that no:

- ElevenLabs tool
- retry/circuit-breaker behavior
- callback mismatch policy
- support-ticket state machine
- Operation state machine
- traceability implementation

was added.


Finish with exactly one of:

SPRINT 3 / PROMPT 004 — PASSED

or

SPRINT 3 / PROMPT 004 — FAILED


Do not proceed beyond Prompt 004.
Stop after the final report.
```
