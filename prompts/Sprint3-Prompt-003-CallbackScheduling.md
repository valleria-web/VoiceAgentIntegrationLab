# SPRINT 3 / PROMPT 003 — CALLBACK SCHEDULING

## Project

**Voice Agent Integration Lab**

Expected working branch:

```text
sprint-3
```

---

# 1. Current baseline

The repository already contains three enterprise capabilities:

```text
GET /orders/{order_id}
GET /customers/{customer_id}
POST /support-tickets
GET /support-tickets/{ticket_id}
```

Canonical order:

```text
GET /orders/1111
```

HTTP 200

```json
{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}
```

Canonical customer:

```text
GET /customers/2001
```

HTTP 200

```json
{
  "customer_id": "2001",
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "status": "active"
}
```

Canonical support-ticket creation:

```text
POST /support-tickets
```

Canonical first ticket in a fresh runtime:

```text
TCK-3001
```

Support-ticket mutation is retained in process-local memory and can be observed through:

```text
GET /support-tickets/{ticket_id}
```

Current test baseline:

```text
10 passed
0 failed
```

Current architecture separates:

```text
src/main.py
    HTTP / FastAPI interface

src/application/
    application services

src/adapters/mock_enterprise.py
    deterministic mock enterprise behavior and mutable runtime state
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

Add the second mutating enterprise capability:

```text
POST /callbacks
```

A successful request schedules a callback inside the mock enterprise system.

The scheduled callback must then be observable through:

```text
GET /callbacks/{callback_id}
```

This ticket must prove:

```text
request
→ HTTP validation
→ application service
→ mock enterprise mutation
→ structured callback result
→ subsequent retrieval of the scheduled callback
```

This remains a backend-only ticket.

Do **NOT** configure ElevenLabs tools yet.

---

# 3. Canonical callback request

Use this exact canonical request:

```text
POST /callbacks
```

Content-Type:

```text
application/json
```

Body:

```json
{
  "customer_id": "2001",
  "phone": "+5511999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up"
}
```

All identifiers remain strings.

The phone number uses E.164-style international notation.

The scheduled time includes an explicit timezone offset.

---

# 4. Canonical success result

The first successfully scheduled callback in a fresh runtime must receive:

```text
callback_id:
CBK-4001
```

Expected HTTP response:

```text
201 Created
```

Expected body:

```json
{
  "callback_id": "CBK-4001",
  "customer_id": "2001",
  "phone": "+5511999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up",
  "status": "scheduled"
}
```

Do **NOT** add:

- creation timestamps
- random UUIDs
- random values
- external identifiers
- generated metadata

The mock behavior must remain deterministic and easy to verify.

---

# 5. Mutation requirement

Returning HTTP 201 and a JSON object is **NOT** sufficient.

The mock enterprise adapter must actually retain the scheduled callback in runtime memory.

After a successful:

```text
POST /callbacks
```

the resource must be retrievable through:

```text
GET /callbacks/CBK-4001
```

Expected HTTP 200:

```json
{
  "callback_id": "CBK-4001",
  "customer_id": "2001",
  "phone": "+5511999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up",
  "status": "scheduled"
}
```

The callback store may be process-local and in-memory.

Persistence across process restarts is **NOT** required.

Do **NOT** add a database.

---

# 6. Unknown callback

Use this canonical unknown callback:

```text
CBK-9999
```

```text
GET /callbacks/CBK-9999
```

must return:

HTTP 404

```json
{
  "detail": "Callback not found"
}
```

---

# 7. Request validation

The callback request must require:

```text
customer_id
phone
scheduled_for
reason
```

All four fields are required.

Empty values must not be accepted as successful callback scheduling.

## Phone validation

The `phone` value must use a simple E.164-style format:

```text
+<country code><subscriber number>
```

For this ticket, validate only the structural format.

Do **NOT** attempt carrier validation, country-specific telecom validation, or external phone verification.

The canonical valid value is:

```text
+5511999990001
```

An obviously invalid value such as:

```text
11999990001
```

must fail request validation and must not create a callback.

Do not add a phone-validation dependency if a small explicit validation rule is sufficient.

## Scheduled time validation

`scheduled_for` must be a valid ISO-8601 datetime with an explicit timezone offset.

Canonical value:

```text
2026-08-29T15:00:00-03:00
```

A datetime without timezone information must not be accepted.

For this ticket, validate the datetime representation and timezone-awareness only.

Do **NOT** compare the requested time against the current wall clock.

This prevents tests from becoming date-dependent and keeps the ticket deterministic.

Future/past scheduling policy is outside the scope of this ticket.

## Reason validation

`reason` must be a non-empty string.

Do not introduce a taxonomy or enum of callback reasons yet.

Use FastAPI/Pydantic validation in the simplest appropriate way.

Do not build a custom validation framework.

---

# 8. Architecture

Preserve the established layer separation:

```text
HTTP interface
    ↓
Application service
    ↓
Mock enterprise adapter
```

Create:

```text
src/application/callback_service.py
```

Extend:

```text
src/adapters/mock_enterprise.py
```

Modify:

```text
src/main.py
```

only as required to expose:

```text
POST /callbacks
GET /callbacks/{callback_id}
```

Responsibilities:

## `src/main.py`

- HTTP routing
- request/response boundary
- HTTP status translation
- Pydantic request validation

## `src/application/callback_service.py`

- application mediation
- call the enterprise adapter
- expose callback creation and retrieval behavior to the HTTP layer

## `src/adapters/mock_enterprise.py`

- own callback runtime state
- generate deterministic callback identifiers
- store scheduled callbacks
- retrieve stored callbacks

Do **NOT** hardcode the canonical success response directly inside the FastAPI route.

---

# 9. Callback identifiers

Use deterministic sequential mock identifiers beginning with:

```text
CBK-4001
```

For example, within one fresh runtime:

```text
first callback  → CBK-4001
second callback → CBK-4002
```

Do not use:

```text
uuid.uuid4()
random
timestamps
external APIs
```

The exact internal implementation is up to you as long as behavior remains small, explicit, and deterministic.

Callback identifiers must be independent from support-ticket identifiers.

---

# 10. Important domain boundaries

Do **NOT** introduce new cross-entity domain rules during this ticket.

Specifically, do **NOT** implement:

```text
customer mismatch
order/customer ownership validation
customer existence enforcement
callback conflict detection
duplicate callback prevention
business-hours policy
future/past scheduling policy
```

The canonical request uses:

```text
customer_id = 2001
```

because customer `2001` already exists in the mock enterprise baseline.

However, this ticket does not yet establish callback eligibility rules based on customer state.

Those rules belong to later modeling or failure tickets.

---

# 11. Tests

Add automated tests covering at least the following behaviors.

## TEST 1 — Successful callback scheduling

POST:

```text
/callbacks
```

with:

```json
{
  "customer_id": "2001",
  "phone": "+5511999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up"
}
```

Expected:

```text
HTTP 201
```

and the canonical callback structure.

---

## TEST 2 — Mutation is observable

Create a callback.

Then retrieve it using:

```text
GET /callbacks/{returned_callback_id}
```

Expected:

```text
HTTP 200
```

The retrieved callback must equal the resource returned by the successful POST.

This proves that the mock enterprise state actually changed.

---

## TEST 3 — Unknown callback

```text
GET /callbacks/CBK-9999
```

Expected:

HTTP 404

```json
{
  "detail": "Callback not found"
}
```

---

## TEST 4 — Invalid phone

Send:

```json
{
  "customer_id": "2001",
  "phone": "11999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up"
}
```

Expected:

```text

Invalid phone number format. Expected value beginning with +

```

The request must **NOT** produce HTTP 201 and must **NOT** create a callback.

---

## TEST 5 — Timezone is required

Send a callback request with:

```text
scheduled_for = 2026-08-29T15:00:00
```

with no timezone or UTC offset.

Expected:

```text
HTTP validation failure
```

The request must **NOT** produce HTTP 201 and must **NOT** create a callback.

---

## TEST 6 — Missing required field

Send a POST missing at least one required field.

Expected:

```text
HTTP validation failure, all fields must be filled
```

The request must **NOT** produce HTTP 201.

---

## Regression

Run the complete existing test suite.

All existing:

```text
order tests
customer tests
support-ticket tests
```

must continue to pass.

Expected baseline before this ticket:

```text
10 passed
0 failed
```

---

# 12. No false success

A callback may only be reported as successfully scheduled when the mock enterprise adapter has actually accepted and stored it.

The HTTP layer must not manufacture a successful callback result without enterprise mutation.

Invalid requests must remain failures.

A validation failure must never be transformed into:

```text
status = scheduled
```

This ticket does **NOT** implement the USMT invariant as a runtime state machine.

It only preserves the behavioral principle:

```text
reported success requires verified enterprise success
```

---

# 13. Explicitly out of scope

Do **NOT** implement:

- ElevenLabs webhook configuration
- `schedule_callback` Agent tool
- customer mismatch
- order/customer ownership validation
- API timeout simulation
- callback conflict detection
- duplicate scheduling policy
- business-hours policy
- future/past time policy
- external calendar integration
- external telephony integration
- `operation_id`
- `trace_id`
- structured logging
- observability framework
- `Operation` object
- USMT states
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

# 14. Implementation style

Keep the implementation small and explicit.

Use type annotations where appropriate.

Prefer the existing project conventions.

Use standard Python/Pydantic capabilities where sufficient.

Do not add a third-party date/time or phone-validation package unless it is genuinely necessary.

Do not introduce abstractions merely because additional enterprise operations may be added later.

The behavior should remain understandable by directly following:

```text
HTTP
→ application service
→ mock enterprise adapter
```

---

# 15. Execution procedure

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
10 passed
0 failed
```

4. Read:

```text
dev-docs/Voice Agent Integration Lab USMT v01.md
```

only to preserve its frozen boundaries.

Then implement the ticket.

After implementation:

1. Run the complete pytest suite.
2. Confirm all existing order tests pass.
3. Confirm all existing customer tests pass.
4. Confirm all existing support-ticket tests pass.
5. Confirm all new callback tests pass.
6. If practical, start FastAPI manually and verify:

```text
POST /callbacks
GET /callbacks/CBK-4001
GET /callbacks/CBK-9999
```

7. Manually verify one invalid phone request.
8. Manually verify one timezone-less datetime request.
9. Inspect git diff.
10. Inspect git status.
11. Confirm the frozen USMT was not modified.
12. Confirm no secret/runtime artifact was added.

Do not commit automatically.

---

# 16. Acceptance criteria

PASS only if all of the following are true:

- [ ] `POST /callbacks` exists
- [ ] Canonical request returns HTTP 201
- [ ] First callback in a fresh runtime is `CBK-4001`
- [ ] Successful response contains exactly:

```json
{
  "callback_id": "CBK-4001",
  "customer_id": "2001",
  "phone": "+5511999990001",
  "scheduled_for": "2026-08-29T15:00:00-03:00",
  "reason": "Order delivery follow-up",
  "status": "scheduled"
}
```

- [ ] Successful scheduling causes real in-memory mock enterprise mutation
- [ ] `GET /callbacks/CBK-4001` can observe the scheduled callback
- [ ] `GET /callbacks/CBK-9999` returns HTTP 404
- [ ] Unknown-callback error body is exactly:

```json
{
  "detail": "Callback not found"
}
```

- [ ] Invalid phone cannot produce HTTP 201
- [ ] Timezone-less `scheduled_for` cannot produce HTTP 201
- [ ] Missing required input cannot produce HTTP 201
- [ ] Validation failure does not create callback state
- [ ] HTTP interface remains thin
- [ ] `callback_service.py` mediates application behavior
- [ ] `mock_enterprise.py` owns mutable callback state
- [ ] Callback IDs are deterministic and independent from ticket IDs
- [ ] Existing order behavior remains unchanged
- [ ] Existing customer behavior remains unchanged
- [ ] Existing support-ticket behavior remains unchanged
- [ ] Complete pytest suite passes
- [ ] Frozen USMT remains unchanged
- [ ] No customer mismatch logic was introduced
- [ ] No timeout simulation was introduced
- [ ] No ElevenLabs tool was configured
- [ ] No Operation/state-machine/traceability implementation was introduced
- [ ] No secrets were exposed

---

# 17. Final report

At completion report exactly this structure:

```text
SPRINT 3 / PROMPT 003 — CALLBACK SCHEDULING


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


Canonical POST result:

<HTTP status + body>


Mutation verification:

<created callback ID>

<GET verification result>


Unknown callback result:

<HTTP status + body>


Invalid phone result:

<HTTP status>


Timezone-less datetime result:

<HTTP status>


Missing-field result:

<HTTP status>


Order regression:

PASS or FAIL


Customer regression:

PASS or FAIL


Support-ticket regression:

PASS or FAIL


USMT modified:

yes/no


Secrets exposed:

yes/no


Architecture summary:

State briefly where:

- HTTP routing/validation lives
- application mediation lives
- mutable enterprise callback state lives


Mutation semantics:

State whether successful callback scheduling is observable through the
subsequent GET endpoint.


Validation semantics:

State whether invalid phone, timezone-less datetime, and missing
required fields are prevented from creating callback state.


Scope confirmation:

Explicitly confirm that no:

- ElevenLabs tool
- customer mismatch
- timeout simulation
- callback conflict policy
- Operation state machine
- traceability implementation

was added.


Finish with exactly one of:

SPRINT 3 / PROMPT 003 — PASSED

or

SPRINT 3 / PROMPT 003 — FAILED


Do not proceed to Prompt 004.
Stop after the final report.
```
