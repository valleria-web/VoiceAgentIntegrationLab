SPRINT 3 / PROMPT 001
CUSTOMER LOOKUP

Context

You are working in the existing project:

Voice Agent Integration Lab

Current baseline:

- Python 3.13
- FastAPI
- pytest
- Existing deterministic enterprise endpoint:
  GET /orders/{order_id}

Current architecture already separates:

src/main.py
    HTTP/FastAPI boundary

src/application/order_service.py
    application mediation

src/adapters/mock_enterprise.py
    deterministic mock enterprise data/access

Existing canonical order:

GET /orders/1111

returns:

{
  "order_id": "1111",
  "status": "in_transit",
  "estimated_delivery": "2026-08-28"
}

Unknown order:

GET /orders/9999

returns:

HTTP 404

{
  "detail": "Order not found"
}

The existing order behavior and tests are the regression baseline and must remain unchanged.

The canonical document:

dev-docs/Voice Agent Integration Lab USMT v01.md

is FROZEN.

Do not modify, reinterpret, extend, or implement the USMT state machine in this ticket.


==========
OBJECTIVE
==========

Add a deterministic enterprise customer lookup capability.

New endpoint:

GET /customers/{customer_id}

This ticket implements only the backend capability.

Do NOT configure ElevenLabs tools yet.


==================
CANONICAL CUSTOMER
==================

Use this exact canonical customer:

customer_id:

2001

Expected response:

{
  "customer_id": "2001",
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "status": "active"
}

Treat customer IDs as strings.

The customer data must live in the mock enterprise adapter layer.

Do not hardcode the canonical response directly in the FastAPI route.


===================
UNKNOWN CUSTOMER
===================

Use this canonical unknown customer:

9999

GET /customers/9999

must return:

HTTP 404

{
  "detail": "Customer not found"
}



# ARCHITECTURE

Preserve the existing layer separation.

Expected responsibility flow:

FastAPI route
    ↓
Application service
    ↓
Mock enterprise adapter


Create:

src/application/customer_service.py

Add customer lookup capability to:

src/adapters/mock_enterprise.py

Modify:

src/main.py

only as required to expose the HTTP endpoint.


FastAPI must remain responsible only for the HTTP boundary and translating the application result into the appropriate HTTP response.

The application layer must mediate the lookup.

The adapter must own deterministic enterprise customer data and lookup behavior.


============
DETERMINISM
============

Customer lookup must be deterministic.

Repeated requests for customer 2001 must return exactly the same result.

No random values.

No current timestamps.

No generated IDs.

No database.

No external API.

No network dependency.


=====
TESTS
======

Add tests covering at least these three behaviors.

TEST 1 — Canonical customer

GET /customers/2001

Expected:

HTTP 200

Exact JSON:

{
  "customer_id": "2001",
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "status": "active"
}


TEST 2 — Unknown customer

GET /customers/9999

Expected:

HTTP 404

Exact JSON:

{
  "detail": "Customer not found"
}


TEST 3 — Determinism

Call:

GET /customers/2001

at least five times.

All responses must:

- return HTTP 200
- contain identical JSON
- match the canonical customer payload


Also run all existing order tests.

No regression to GET /orders/{order_id} is allowed.


============
IMPORTANT CONSTRAINTS
============

Do NOT:

- modify the frozen USMT document
- implement Operation
- implement protocol states
- implement trace_id
- implement operation_id
- implement structured logging
- add authentication
- add persistence
- add database code
- configure ElevenLabs
- create a webhook tool
- implement customer/order mismatch yet
- implement support ticket creation
- implement callback scheduling
- simulate API timeout
- add unrelated dependencies
- refactor unrelated code

This is intentionally a narrow ticket.


============
CODE QUALITY
============

Use clear Python naming and type annotations where appropriate.

Prefer simple explicit code over abstractions that are not yet necessary.

Do not introduce a generic repository framework or enterprise abstraction merely because more integrations are planned.

Preserve the current architecture and extend it minimally.


=========
EXECUTION
=========

Before modification:

1. Inspect the current repository.
2. Confirm the current branch.
3. Run the existing test suite and report the baseline.
4. Read:

   dev-docs/Voice Agent Integration Lab USMT v01.md

   only to respect its frozen boundaries.

Then implement the ticket.

After implementation:

1. Run the complete pytest suite.
2. Verify existing order tests still pass.
3. Verify the three new customer behaviors.
4. If practical, perform manual requests against the FastAPI app:

   GET /customers/2001
   GET /customers/9999

5. Inspect git diff/status.
6. Verify no secrets or generated runtime artifacts were added.


==================================================
ACCEPTANCE CRITERIA
==================================================

PASS only if all of the following are true:

[ ] GET /customers/2001 returns HTTP 200

[ ] Response is exactly:

{
  "customer_id": "2001",
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "status": "active"
}

[ ] GET /customers/9999 returns HTTP 404

[ ] Error body is exactly:

{
  "detail": "Customer not found"
}

[ ] Five repeated canonical lookups produce identical results

[ ] Customer data belongs to the mock enterprise adapter

[ ] Application mediation exists in customer_service.py

[ ] FastAPI route remains thin

[ ] Existing order behavior remains unchanged

[ ] Complete test suite passes

[ ] Frozen USMT remains unchanged

[ ] No ElevenLabs configuration is implemented

[ ] No Operation/state-machine/traceability implementation is introduced

[ ] No secrets are exposed


============
FINAL REPORT
============

At completion report:

SPRINT 3 / PROMPT 001 — CUSTOMER LOOKUP

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

Canonical customer result:
<status + body>

Unknown customer result:
<status + body>

Determinism:
<result of repeated calls>

Order regression:
<pass/fail>

USMT modified:
yes/no

Secrets exposed:
yes/no

Architecture summary:
briefly state where HTTP, application mediation,
and mock enterprise data now live.

Do not proceed to the next Sprint 3 prompt.
Stop after the final report.