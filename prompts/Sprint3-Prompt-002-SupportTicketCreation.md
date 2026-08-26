SPRINT 3 / PROMPT 002
SUPPORT TICKET CREATION

Project:

Voice Agent Integration Lab

Expected working branch:

sprint-3


==================================================
1. CURRENT BASELINE
==================================================

The current repository already contains two deterministic enterprise
lookup capabilities:

GET /orders/{order_id}

Canonical order:

GET /orders/1111

HTTP 200

{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}


GET /customers/{customer_id}

Canonical customer:

GET /customers/2001

HTTP 200

{
  "customer_id": "2001",
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "status": "active"
}


Unknown customer:

GET /customers/9999

HTTP 404

{
  "detail": "Customer not found"
}


Current test baseline:

6 passed
0 failed


Current architecture separates:

src/main.py
    HTTP / FastAPI interface

src/application/
    application services

src/adapters/mock_enterprise.py
    deterministic mock enterprise behavior/data


The canonical document:

dev-docs/Voice Agent Integration Lab USMT v01.md

is FROZEN.

Read it before implementation only to respect its boundaries.

Do NOT modify, reinterpret, extend, or implement the USMT state machine
during this ticket.


==================================================
2. OBJECTIVE
==================================================

Add the first MUTATING enterprise capability:

POST /support-tickets

A successful request must create a support ticket inside the mock
enterprise system.

The created ticket must then be observable through:

GET /support-tickets/{ticket_id}


This ticket must prove:

request
→ HTTP validation
→ application service
→ mock enterprise mutation
→ structured result
→ subsequent retrieval of the created resource


This is still backend-only.

Do NOT configure ElevenLabs tools in this ticket.


==================================================
3. CANONICAL SUPPORT TICKET REQUEST
==================================================

Use this exact canonical request:

POST /support-tickets

Content-Type:

application/json

Body:

{
  "customer_id": "2001",
  "order_id": "1111",
  "issue": "Delivery status follow-up"
}


All IDs must remain strings.


==================================================
4. CANONICAL SUCCESS RESULT
==================================================

The first successfully created ticket in a fresh runtime must receive:

ticket_id:

TCK-3001


Expected HTTP response:

201 Created


Expected body:

{
  "ticket_id": "TCK-3001",
  "customer_id": "2001",
  "order_id": "1111",
  "issue": "Delivery status follow-up",
  "status": "open"
}


Do NOT add:

- timestamps
- random UUIDs
- random values
- external identifiers
- generated metadata

The mock behavior should remain easy to reason about and verify.


==================================================
5. MUTATION REQUIREMENT
==================================================

Returning a successful JSON response is NOT sufficient.

The mock enterprise adapter must actually retain the created ticket
in runtime memory.

After:

POST /support-tickets

returns successfully, this request:

GET /support-tickets/TCK-3001

must return:

HTTP 200

{
  "ticket_id": "TCK-3001",
  "customer_id": "2001",
  "order_id": "1111",
  "issue": "Delivery status follow-up",
  "status": "open"
}


The ticket store may be process-local/in-memory.

Persistence across process restarts is NOT required.

Do NOT add a database.


==================================================
6. UNKNOWN SUPPORT TICKET
==================================================

Use this canonical unknown ticket:

TCK-9999


GET /support-tickets/TCK-9999

must return:

HTTP 404

{
  "detail": "Support ticket not found"
}


==================================================
7. REQUEST VALIDATION
==================================================

The POST request must require:

customer_id
order_id
issue


Each must be a string.

Empty values must not be accepted as a successful ticket creation.


Malformed or incomplete request payloads must produce an HTTP
validation error and MUST NOT be represented as successful creation.


Use FastAPI/Pydantic validation in the simplest appropriate way.

Do not build a custom validation framework.


==================================================
8. ARCHITECTURE
==================================================

Preserve the established layer separation:

HTTP interface
    ↓
Application service
    ↓
Mock enterprise adapter


Create:

src/application/support_ticket_service.py


Extend:

src/adapters/mock_enterprise.py


Modify:

src/main.py

only as required to expose:

POST /support-tickets

GET /support-tickets/{ticket_id}


Responsibilities:

src/main.py

- HTTP routing
- request/response boundary
- HTTP status translation
- request schema validation


src/application/support_ticket_service.py

- application mediation
- call the enterprise adapter
- expose creation and retrieval behavior to the HTTP layer


src/adapters/mock_enterprise.py

- own support-ticket runtime state
- generate deterministic mock ticket identifiers
- store created support tickets
- retrieve stored support tickets


Do NOT hardcode the canonical success response directly inside the
FastAPI route.


==================================================
9. TICKET IDENTIFIERS
==================================================

Use deterministic sequential mock identifiers beginning with:

TCK-3001


For example, within one runtime:

first ticket  → TCK-3001
second ticket → TCK-3002


Do not use:

uuid.uuid4()
random
timestamps
external APIs


The exact internal implementation is up to you as long as behavior
remains simple and deterministic.


==================================================
10. IMPORTANT DOMAIN BOUNDARY
==================================================

Do NOT implement customer/order ownership validation yet.

Specifically, do NOT implement:

customer mismatch

during this ticket.


The canonical request uses:

customer_id = 2001
order_id = 1111

but this ticket does not yet establish or enforce a formal ownership
relationship between them.


That failure mode belongs to a later Sprint 3 ticket.


==================================================
11. TESTS
==================================================

Add automated tests covering at least the following behaviors.


TEST 1 — Successful support ticket creation

POST /support-tickets

with:

{
  "customer_id": "2001",
  "order_id": "1111",
  "issue": "Delivery status follow-up"
}

Expected:

HTTP 201

and the canonical support-ticket structure.


--------------------------------------------------

TEST 2 — Mutation is observable

Create a support ticket.

Then retrieve it using:

GET /support-tickets/{returned_ticket_id}

Expected:

HTTP 200

and the retrieved resource must equal the resource returned by the
successful POST.


This test is important.

It demonstrates that the mock enterprise state actually changed.


--------------------------------------------------

TEST 3 — Unknown ticket

GET /support-tickets/TCK-9999

Expected:

HTTP 404

{
  "detail": "Support ticket not found"
}


--------------------------------------------------

TEST 4 — Invalid request

Send a POST missing at least one required field.

Expected:

HTTP validation failure.

The request must NOT produce HTTP 201.


--------------------------------------------------

REGRESSION

Run the complete existing test suite.

All existing:

order tests
customer tests

must continue to pass.


==================================================
12. NO FALSE SUCCESS
==================================================

A support ticket may only be reported as successfully created when
the mock enterprise adapter has actually accepted and stored it.

The HTTP layer must not manufacture a successful ticket result
without enterprise mutation.

This ticket does NOT implement the USMT invariant as a runtime state
machine.

It merely preserves the behavioral principle:

reported success requires verified enterprise success.


==================================================
13. EXPLICITLY OUT OF SCOPE
==================================================

Do NOT implement:

- ElevenLabs webhook configuration
- create_support_ticket Agent tool
- customer mismatch
- API timeout simulation
- callback scheduling
- operation_id
- trace_id
- structured logging
- observability framework
- Operation object
- USMT states
- state-machine transitions
- authentication
- authorization
- database persistence
- external APIs
- frontend
- deployment
- Docker
- generic repository framework
- generic enterprise abstraction
- unrelated refactoring


Do NOT modify:

dev-docs/Voice Agent Integration Lab USMT v01.md


==================================================
14. IMPLEMENTATION STYLE
==================================================

Keep the implementation small and explicit.

Use type annotations where appropriate.

Prefer the existing project conventions.

Do not introduce abstraction merely because additional enterprise
operations are planned.

This ticket should remain understandable by directly following:

HTTP
→ application service
→ mock enterprise adapter


==================================================
15. EXECUTION PROCEDURE
==================================================

Before modifying code:

1. Confirm current branch.

Expected:

sprint-3


2. Inspect the current repository structure.


3. Run the complete test suite.

Expected baseline:

6 passed
0 failed


4. Read:

dev-docs/Voice Agent Integration Lab USMT v01.md

only to preserve its frozen boundaries.


Then implement the ticket.


After implementation:

1. Run the complete pytest suite.

2. Confirm all existing order tests pass.

3. Confirm all existing customer tests pass.

4. Confirm all new support-ticket tests pass.

5. If practical, start FastAPI manually and verify:

POST /support-tickets

GET /support-tickets/TCK-3001

GET /support-tickets/TCK-9999


6. Inspect git diff.

7. Inspect git status.

8. Confirm the USMT was not modified.

9. Confirm no secret/runtime artifact was added.


Do not commit automatically.


==================================================
16. ACCEPTANCE CRITERIA
==================================================

PASS only if all of the following are true:


[ ] POST /support-tickets exists


[ ] Canonical request returns HTTP 201


[ ] First ticket in a fresh runtime is TCK-3001


[ ] Successful response contains exactly:

{
  "ticket_id": "TCK-3001",
  "customer_id": "2001",
  "order_id": "1111",
  "issue": "Delivery status follow-up",
  "status": "open"
}


[ ] Successful creation causes real in-memory mock enterprise mutation


[ ] GET /support-tickets/TCK-3001 can observe the created ticket


[ ] GET /support-tickets/TCK-9999 returns HTTP 404


[ ] Unknown-ticket error body is exactly:

{
  "detail": "Support ticket not found"
}


[ ] Missing/invalid required input cannot produce HTTP 201


[ ] HTTP interface remains thin


[ ] support_ticket_service.py mediates application behavior


[ ] mock_enterprise.py owns mutable ticket state


[ ] Existing order behavior remains unchanged


[ ] Existing customer behavior remains unchanged


[ ] Complete pytest suite passes


[ ] Frozen USMT remains unchanged


[ ] No customer mismatch logic was introduced


[ ] No ElevenLabs tool was configured


[ ] No Operation/state-machine/traceability implementation was introduced


[ ] No secrets were exposed


==================================================
17. FINAL REPORT
==================================================

At completion report exactly this structure:


SPRINT 3 / PROMPT 002 — SUPPORT TICKET CREATION


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

<created ticket ID>

<GET verification result>


Unknown ticket result:

<HTTP status + body>


Invalid request result:

<HTTP status>


Order regression:

PASS or FAIL


Customer regression:

PASS or FAIL


USMT modified:

yes/no


Secrets exposed:

yes/no


Architecture summary:

State briefly where:

- HTTP routing/validation lives
- application mediation lives
- mutable enterprise ticket state lives


Mutation semantics:

State whether successful ticket creation is observable through the
subsequent GET endpoint.


Scope confirmation:

Explicitly confirm that no:

- ElevenLabs tool
- customer mismatch
- timeout simulation
- callback scheduling
- Operation state machine
- traceability implementation

was added.


Finish with exactly one of:

SPRINT 3 / PROMPT 002 — PASSED

or

SPRINT 3 / PROMPT 002 — FAILED


Do not proceed to Prompt 003.
Stop after the final report.