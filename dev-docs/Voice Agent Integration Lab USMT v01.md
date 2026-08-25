# Voice Agent Integration Lab — USMT v0.1

## Sprint 0 — System Modeling

**Mission:** construir uma integração demonstrável entre um agente de voz ElevenLabs e sistemas empresariais simulados por meio de um backend Python/FastAPI, com execução observável, rastreável e verificável.

## 1. 🔬 Phenomenon description

Um usuário interage por voz com um agente ElevenLabs e solicita uma operação que depende de dados ou ações externas.

O agente identifica que precisa utilizar uma ferramenta e envia uma chamada estruturada ao backend Python.

O backend:

```text
receives
→ validates
→ executes
→ observes
→ returns
```

a operação contra um sistema empresarial simulado.

O resultado retorna ao agente, que o transforma em uma resposta de voz para o usuário.

### Fenômeno:

```text
User intent
   ↓
Voice
   ↓
ElevenLabs Agent
   ↓
Tool Invocation
   ↓
Python Integration
   ↓
Enterprise System
   ↓
Structured Result
   ↓
ElevenLabs Agent
   ↓
Voice Response
```

O objeto principal de observação será uma tool-backed operation individual.

## 2. 📏 Phenomenon delimitation

### Dentro do sistema investigado

- ElevenLabs Agent configuration relevant to the operation
- tool invocation
- Python/FastAPI endpoint
- request validation
- application logic
- external-system adapter
- mock enterprise APIs/data
- returned tool result
- trace/correlation data
- observed agent response
- tests and evaluation evidence

### Fora do escopo inicial

- funcionamento interno dos modelos de voz da ElevenLabs
- treinamento/inferência dos foundational models
- telecom infrastructure
- speech recognition internals
- billing
- authentication enterprise real
- produção multi-tenant
- real customer data
- CRM real
- payment systems
- high availability/disaster recovery

### Boundary operacional

A operação formal começa quando:

> ElevenLabs Agent emits an authorized tool invocation.

E termina quando ocorre exatamente um terminal outcome:

- Completed
- Rejected
- Failed

A fala anterior do usuário fornece contexto, mas não pertence ao estado formal da integração Python até existir um ToolInvocationReceived.

## 3. ⏳ State Enumeration

### Primeiro corte:

```text
Ready
   ↓
Received
   ↓
Validated
   ↓
Executing
   ↓
ResultAvailable
   ↓
Returned
   ↓
Completed
```

### Estados terminais alternativos:

- Rejected
- Failed

### Significado

#### Ready

Integração apta a receber nova operação.

#### Received

Uma tool invocation chegou ao backend e recebeu identidade de execução.

#### Validated

Tool, payload e pré-condições foram aceitos.

#### Executing

A integração está realizando a operação externa.

#### ResultAvailable

Existe resultado estruturado proveniente do sistema empresarial.

#### Returned

O resultado foi entregue novamente ao ElevenLabs Agent.

#### Completed

Foi observada conclusão bem-sucedida da operação end-to-end.

#### Rejected

A operação foi recusada antes da execução externa por não satisfazer pré-condições.

#### Failed

Uma operação válida começou, mas não conseguiu ser concluída corretamente.

## 4. ⚡ Event Enumeration

### Eventos iniciais:

- ToolInvocationReceived
- InvocationValidated
- InvocationRejected

- EnterpriseRequestDispatched
- EnterpriseResponseReceived
- EnterpriseRequestFailed
- EnterpriseRequestTimedOut

- ToolResultReturned
- AgentResponseObserved

- OperationCompleted
- OperationFailed

Podemos depois especializar eventos por tool:

- OrderLookupRequested
- CustomerLookupRequested
- SupportTicketRequested

mas não na v0.1.

Primeiro preservamos eventos de protocolo genéricos.

## 5. 🟢 Allowed transitions

```text
Ready
  → Received
    by ToolInvocationReceived
Received
  → Validated
    by InvocationValidated
```

ou:

```text
Received
  → Rejected
    by InvocationRejected
```

Depois:

```text
Validated
  → Executing
    by EnterpriseRequestDispatched
Executing
  → ResultAvailable
    by EnterpriseResponseReceived
```

ou:

```text
Executing
  → Failed
    by EnterpriseRequestFailed
Executing
  → Failed
    by EnterpriseRequestTimedOut
```

Depois:

```text
ResultAvailable
  → Returned
    by ToolResultReturned
Returned
  → Completed
    by AgentResponseObserved
```

### Happy path

```text
Ready
→ Received
→ Validated
→ Executing
→ ResultAvailable
→ Returned
→ Completed
```

## 6. 🚫 Forbidden transitions

Exemplos canônicos:

`Ready → Executing`

Forbidden because no tool invocation exists.

`Received → Executing`

Forbidden because validation was skipped.

`Rejected → Executing`

Forbidden because Rejected is terminal.

`Failed → Completed`

Forbidden inside the same operation.

`Executing → Completed`

Forbidden because external result and agent return have not been established.

`ResultAvailable → Completed`

Forbidden because successful external execution alone does not prove that the result reached the agent.

E:

```text
Completed → *
Rejected  → *
Failed    → *
```

All terminal states are terminal.

## 7. 🛑 Invalidation Conditions

A operação deve ser rejeitada antes de tocar o sistema empresarial se houver:

- unknown tool;
- unauthorized tool;
- malformed JSON;
- payload incompatible with schema;
- missing required field;
- invalid identifier;
- unsupported operation;
- inability to establish operation identity/correlation;
- unsafe or ambiguous parameters for a mutating operation.

Uma operação já validada deve resultar em Failed, e não Rejected, quando ocorrer:

- external API timeout;
- external system unavailable;
- unexpected integration exception;
- incompatible external response;
- failure returning the tool result;
- required downstream operation cannot complete.

**Importante:**

`Rejected ≠ Failed`

Rejected: execução não deveria começar.

Failed: execução poderia começar, mas não terminou corretamente.

## 8. 🏁 Termination Guarantee

Toda operação deve terminar em exatamente um destes estados:

- Completed
- Rejected
- Failed

Nenhuma operação pode permanecer indefinidamente em:

- Received
- Validated
- Executing
- ResultAvailable
- Returned

External calls devem possuir timeout explícito.

Em caso de timeout:

```text
Executing
→ Failed
```

Toda execução deve produzir um terminal record.

## 9. 💎 Invariants

Aqui está o coração da USMT.

### I1 — Every operation has identity

Antes de qualquer external call:

```text
operation_id != null
trace_id != null
```

### I2 — No execution without validation

```text
EnterpriseRequestDispatched
requires
state == Validated
```

### I3 — No false success

Uma operação jamais pode ser comunicada como bem-sucedida se a integração não possuir evidência de sucesso.

```text
reported_success
requires
verified_external_success
```

### I4 — Terminal uniqueness

Cada operação possui exatamente um terminal outcome:

`Completed XOR Rejected XOR Failed`

### I5 — Trace completeness

Toda transição relevante deve ser correlacionável ao mesmo:

- operation_id
- trace_id

### I6 — External system isolation

ElevenLabs Agent não acessa diretamente persistência ou database.

Sempre:

```text
Agent
→ Integration API
→ Application
→ Adapter
→ Enterprise System
```

### I7 — Secrets never become payload evidence

API keys, credentials e secrets:

**MUST NOT**

aparecer em:

- logs públicos;
- trace records;
- GitHub;
- test fixtures;
- agent responses.

### I8 — Failure remains failure

Uma falha downstream não pode ser reinterpretada como sucesso na apresentação.

```text
Failed execution
≠
successful voice response
```

Mesmo que o agent seja capaz de produzir uma frase elegante explicando o erro.

## 10. 🥪 Layer separation

Primeiro modelo:

```text
┌────────────────────────────┐
│ User / Voice               │
├────────────────────────────┤
│ ElevenLabs Agent           │
├────────────────────────────┤
│ Tool Contract              │
├────────────────────────────┤
│ FastAPI Interface          │
├────────────────────────────┤
│ Application Services       │
├────────────────────────────┤
│ Enterprise Adapter         │
├────────────────────────────┤
│ Mock Enterprise System     │
├────────────────────────────┤
│ Data / Persistence         │
└────────────────────────────┘
```

Observability atravessa as camadas:

```text
          Trace / Evidence
                │
                ▼
Agent → API → Application → Adapter → System
```

### Authority

#### ElevenLabs Agent

decide quando solicitar uma tool.

#### FastAPI/interface

recebe e valida contrato.

#### Application layer

decide qual operação executar.

#### Adapter

traduz para o sistema externo.

#### Enterprise system

é autoridade sobre seus próprios dados.

#### Observability

observa; não decide domínio.

Essa última separação é importantíssima:

`trace ≠ authority`

## 11. 📊 Verifiable metrics

Para o MVP, eu definiria métricas extremamente verificáveis.

### Protocol correctness

**Target:**

- 100% allowed transitions accepted
- 100% forbidden transitions rejected

### Trace completeness

Para toda operação executada:

- operation_id present
- trace_id present
- initial state recorded
- terminal state recorded

**Target:**

100%

### No false success

Casos onde external system falha mas operação aparece como sucesso:

0

### Test coverage by behavior

No mínimo:

- happy path
- invalid payload
- unknown tool
- order not found
- external failure
- timeout
- successful mutation

### Integration success

**Demo principal:**

```text
User asks for order
→ Agent calls tool
→ Python retrieves order
→ result returns
→ Agent answers correctly
```

**Repeatable:**

3/3 consecutive executions

antes de declararmos MVP demonstrável.

### Latency

Mediremos:

- tool_received_at
- external_request_at
- external_result_at
- tool_returned_at

Sem definir ainda um SLA arbitrário.

Primeiro:

measure.

Depois:

establish target.

## 12. 📜 Spec — Voice Agent Integration Lab v0.1

### System

The Voice Agent Integration Lab SHALL demonstrate a traceable integration between an ElevenLabs voice agent and a Python-based enterprise integration service.

### Operation

A formal operation SHALL begin when an authorized ElevenLabs tool invocation is received by the integration service.

### Identity

Every operation SHALL receive a unique operation_id and trace_id before external execution.

### Validation

No enterprise request SHALL be executed before the tool invocation and payload have been validated.

### Execution

Valid operations MAY interact with enterprise systems only through defined application services and adapters.

### Result

An external success SHALL NOT be considered end-to-end completion until the structured result has been returned to the agent and a corresponding agent response has been observed.

### Failure

Invalid requests SHALL terminate as Rejected.

Valid requests that cannot complete SHALL terminate as Failed.

### Termination

Every operation SHALL terminate as exactly one of:

- Completed
- Rejected
- Failed

### Evidence

Every relevant transition SHALL be observable and correlated through the same operation identity.

### Security

Secrets and credentials SHALL NOT be included in trace evidence, repository content, or user-facing responses.

### Architecture

Agent orchestration, integration logic, enterprise adapters, persistence, and observability SHALL remain separate concerns.

## USMT v0.1 — State Machine

Nosso primeiro objeto inteiro cabe aqui:

```text
                         ┌────────────┐
                         │   Ready    │
                         └─────┬──────┘
                               │ ToolInvocationReceived
                               ▼
                         ┌────────────┐
                         │  Received  │
                         └─────┬──────┘
                              / \
             rejected        /   \ validated
                            ▼     ▼
                     ┌──────────┐ ┌───────────┐
                     │ Rejected │ │ Validated │
                     └──────────┘ └─────┬─────┘
                                        │
                                        ▼
                                  ┌───────────┐
                                  │ Executing │
                                  └─────┬─────┘
                                       / \
                               failure/   \success
                                     ▼     ▼
                              ┌────────┐ ┌─────────────────┐
                              │ Failed │ │ ResultAvailable │
                              └────────┘ └────────┬────────┘
                                                 │
                                                 ▼
                                           ┌──────────┐
                                           │ Returned │
                                           └────┬─────┘
                                                │
                                                ▼
                                         ┌───────────┐
                                         │ Completed │
                                         └───────────┘
```

## Sprint 0 status

Eu diria que já temos uma USMT v0.1 candidata, mas antes de congelá-la quero que nós validemos quatro decisões, porque elas alteram o sistema de verdade:

### Completed exige observar a resposta final do agente?

Minha recomendação: sim. Caso contrário estamos verificando somente integração backend, não a experiência end-to-end.

### Queremos três estados terminais (Completed / Rejected / Failed)?

Minha recomendação: sim. Essa separação ficou muito limpa.

### O objeto central chama-se Operation, Run ou Interaction?

Minha recomendação: Operation. Conversation é mais amplo; Run eu preservaria para protocolos/investigações.

### Primeiro business case = order lookup + support ticket?

Minha recomendação:

- primeira operação: get_order;
- segunda operação: create_support_ticket.

Se você me disser “aprovo os quatro”, eu considero:

> Sprint 0 / USMT v0.1 → FROZEN
