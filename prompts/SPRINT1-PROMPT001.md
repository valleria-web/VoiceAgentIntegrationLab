# SPRINT 1 — PROMPT 001

## Python First Contact with ElevenLabs

### Project

**Voice Agent Integration Lab**

### Branch

Expected working branch:

```text
sprint-1
```

Do not create or switch branches unless necessary. First confirm the current branch.

---

# 1. Canonical reference

Before modifying any code, read:

```text
dev-docs/Voice Agent Integration Lab USMT v01.md
```

This document is the frozen **USMT v0.1** and is the architectural authority for the project.

Do **not** modify, reinterpret, expand, or refactor the USMT during this task.

The USMT defines the future system around a tool-backed `Operation`:

```text
ElevenLabs Agent
→ Tool Invocation
→ Python Integration
→ Enterprise System
→ Structured Result
→ ElevenLabs Agent
```

However, **Sprint 1 does not implement that operation lifecycle yet**.

This sprint exists only to establish the first authenticated technical contact between Python and ElevenLabs.

---

# 2. Sprint 1 objective

Establish and verify:

```text
Python
→ ElevenLabs API
→ authenticated request
→ voice/model discovery if needed
→ Text-to-Speech request
→ generated audio file
```

The success condition for this ticket is:

> A Python script running inside the project virtual environment successfully authenticates with ElevenLabs, performs a real Text-to-Speech request, and writes a non-empty audio file locally.

Nothing beyond this scope should be implemented.

---

# 3. Existing project baseline

Current structure approximately:

```text
Voice Agent Integration Lab/
│
├── .git/
├── .env
├── .gitignore
│
├── dev-docs/
│   └── Voice Agent Integration Lab USMT v01.md
│
├── prompts/
│   └── sprint-1/
│
├── venv/
│
└── diagram.txt
```

Python environment:

```text
Python 3.13
```

The project already has:

```text
ELEVENLABS_API_KEY=
```

inside the root `.env`.

The actual value is local and confidential.

---

# 4. Security constraints

The USMT invariant regarding secrets applies immediately.

The ElevenLabs API key MUST NOT:

* be hardcoded;
* be printed;
* appear in logs;
* appear in exceptions;
* appear in generated documentation;
* appear in tests;
* be committed to Git;
* be copied into `.env.example`.

Read the key only from:

```text
ELEVENLABS_API_KEY
```

in the root `.env`.

Before proceeding, inspect the root `.gitignore` and confirm that at minimum it excludes:

```text
.env
venv/
__pycache__/
*.pyc
```

If any of those entries are missing, add them.

Do not inspect or modify files inside `venv/`.

---

# 5. Implementation scope

Create only the minimum project structure required for the first contact.

Preferred result:

```text
Voice Agent Integration Lab/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
│
├── src/
│   └── first_contact.py
│
├── output/
│   └── first-contact.mp3        # generated locally, not committed
│
├── dev-docs/
│   └── Voice Agent Integration Lab USMT v01.md
│
└── prompts/
    └── sprint-1/
```

If the current repository structure suggests an equally simple Python convention, explain the choice before deviating.

---

# 6. Dependencies

Use the official ElevenLabs Python SDK.

Add only dependencies genuinely required for this ticket.

Expected dependencies will likely include:

```text
elevenlabs
python-dotenv
```

Do not add:

* FastAPI;
* Pydantic application models;
* databases;
* ORMs;
* web servers;
* agent frameworks;
* observability frameworks;
* unnecessary helper libraries.

Record dependencies in:

```text
requirements.txt
```

Do not manually edit anything inside `venv/Lib`.

---

# 7. `.env.example`

Create:

```text
.env.example
```

containing only:

```text
ELEVENLABS_API_KEY=
```

No real secret.

If additional configuration becomes strictly necessary for the first-contact script, keep it minimal and explain why.

---

# 8. First-contact script

Create:

```text
src/first_contact.py
```

The script should:

1. load environment variables from the root `.env`;
2. verify that `ELEVENLABS_API_KEY` exists;
3. fail clearly if it does not exist;
4. initialize the official ElevenLabs client;
5. perform only the discovery necessary to make a valid TTS request;
6. make one real Text-to-Speech request;
7. write the returned audio to:

```text
output/first-contact.mp3
```

8. confirm success without exposing secrets.

Use a short test sentence such as:

```text
Voice Agent Integration Lab. Python first contact successful.
```

Do not embed application/domain behavior in this script.

---

# 9. Voice/model handling

Do not hardcode undocumented assumptions.

Use the current ElevenLabs SDK/API behavior available in the installed package.

If a voice identifier is required:

* use the permitted Voices API to discover an available voice; or
* use another minimal, documented mechanism supported by the SDK.

If a model identifier is required:

* use a currently supported Text-to-Speech model;
* document which model was selected and why.

Do not build custom voice-selection abstractions during this sprint.

This is a connectivity experiment, not product architecture.

---

# 10. Output handling

Generated audio is runtime evidence, not source code.

Create:

```text
output/
```

and ensure generated audio files are ignored by Git.

For example:

```gitignore
output/*.mp3
```

The folder itself may be preserved with a `.gitkeep` only if useful.

Do not commit generated speech artifacts unless explicitly requested later for portfolio evidence.

---

# 11. Error behavior

Handle only meaningful first-contact failures.

At minimum, distinguish clearly between:

```text
missing local API key
authentication/API failure
TTS generation failure
file write failure
```

Do not create a complex exception hierarchy.

Never include the API key in error output.

---

# 12. USMT boundaries for this sprint

Do NOT implement the USMT states:

```text
Ready
Received
Validated
Executing
ResultAvailable
Returned
Completed
Rejected
Failed
```

Do NOT implement:

```text
Operation
operation_id
trace_id
state machine
transition records
enterprise adapters
enterprise systems
tool invocation
agent orchestration
```

Those belong to later sprints.

The formal USMT `Operation` begins with an authorized ElevenLabs tool invocation.

Sprint 1 happens **before that boundary**.

Therefore this script is infrastructure validation, not a canonical protocol execution.

---

# 13. Explicitly out of scope

Do NOT implement:

* ElevenAgents;
* webhook tools;
* FastAPI;
* `get_order`;
* `create_support_ticket`;
* enterprise mock APIs;
* state-machine classes;
* USMT runtime enforcement;
* tracing architecture;
* databases;
* frontend;
* deployment;
* Docker;
* authentication beyond the ElevenLabs API key;
* architecture refactoring;
* unrelated documentation.

Do not modify the frozen USMT.

---

# 14. Verification

Run the project using the active project virtual environment.

Verify:

```text
python --version
```

and report the detected version.

Install dependencies using the project environment.

Then execute:

```text
python src/first_contact.py
```

Successful verification requires:

```text
API authentication succeeds
TTS request succeeds
output/first-contact.mp3 exists
audio file size > 0 bytes
no secret is printed
```

If the API call cannot execute because of account permissions, quota, SDK incompatibility, or another external condition:

* stop;
* report the exact non-sensitive failure;
* do not invent a workaround;
* do not broaden the ticket.

---

# 15. Git safety verification

Before finishing, run:

```text
git status
```

Confirm specifically that:

```text
.env
venv/
generated audio
```

are not staged or tracked.

If `.env` is already tracked from an earlier commit, stop and report this before proceeding further.

Do not commit anything automatically.

---

# 16. Acceptance criteria

Prompt 001 is complete only if:

* the frozen USMT was read before implementation;
* the USMT was not modified;
* Python runs from the project virtual environment;
* the official ElevenLabs Python SDK is installed;
* `.env` remains private;
* `.env.example` contains no secret;
* the ElevenLabs client authenticates successfully;
* one real TTS request succeeds;
* one non-empty local audio file is produced;
* no FastAPI/Agents/domain architecture was introduced;
* `git status` confirms sensitive/runtime artifacts are ignored.

---

# 17. Final report

After execution, provide a concise implementation report containing:

### Files created

List every created file.

### Files modified

List every modified file.

### Dependencies

List installed project dependencies and versions.

### Runtime

Report:

```text
Python version
ElevenLabs SDK version
```

### API interaction

Report:

* whether authentication succeeded;
* voice used;
* TTS model used;
* whether generation succeeded.

Do not report API keys or secret values.

### Evidence

Report:

```text
output file path
output file size
```

### Git safety

Confirm whether:

```text
.env ignored
venv ignored
generated audio ignored
```

### Scope confirmation

Explicitly confirm that no:

```text
FastAPI
ElevenAgents
tool invocation
enterprise integration
Operation state machine
```

was implemented.

### Result

Conclude with exactly one of:

```text
SPRINT 1 / PROMPT 001 — PASSED
```

or

```text
SPRINT 1 / PROMPT 001 — BLOCKED
```

If blocked, explain only the evidence-backed blocker.
