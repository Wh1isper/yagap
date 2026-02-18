# Agent Runtime Async Agent

## Scope

This document defines the high-level async execution model in `agent-runtime`.

Two async types are supported:

- Async Agent: standalone background run
- Async Subagent: background run linked to a parent main-agent run/session

## Design Principles

- Reuse the same run model (`run_id`) for sync and async
- Keep async notification event-driven via Redis Stream
- Keep orchestration decisions in gateway
- Keep runtime focused on execution and status publication

## Async Identity Model

```mermaid
flowchart TB
    AR[Async Agent]
    ASR[Async Subagent]

    AR --> RID1[run_id]
    AR --> SID1[base_session_id]

    ASR --> RID2[run_id]
    ASR --> SID2[base_session_id]
    ASR --> PRID[parent_run_id]
    ASR --> PSID[parent_session_id]
```

`run_id` is generated for every run.
Main-agent run allocates `run_id` and `session_id` at start so later async linkage can reference stable identifiers.

## Async Notification Channel

```mermaid
flowchart LR
    subgraph Runtime[agent-runtime]
        EXE[Async Run Execution]
        PUB[Async Notification Publisher]
    end

    subgraph Infra[Redis]
        ASTREAM[(runtime:async:events)]
    end

    subgraph Gateway[gateway]
        CG[Consumer Group]
        ORCH[Orchestrator]
    end

    EXE --> PUB --> ASTREAM
    ASTREAM --> CG --> ORCH
```

Redis Stream is used instead of Pub/Sub because async completion is optional to consume immediately and may require delayed consumption.

## Notification Semantics

- Runtime publishes lifecycle and terminal async events to stream
- Gateway consumes with consumer group
- Gateway decides business action on completion (notify user, trigger follow-up run, ignore)

## Delivery and Idempotency

Consumer group provides delivery coordination, but business handling remains at-least-once.
Gateway should process async terminal events idempotently using event identity.

## Async Subagent Re-entry Flow

```mermaid
sequenceDiagram
    participant Main as Main Agent Run
    participant RT as agent-runtime
    participant RS as Redis Stream
    participant GW as gateway

    Main->>RT: submit async subagent (linked parent_run_id, parent_session_id)
    RT-->>Main: accepted (run_id)
    Main-->>GW: main run completed

    RT->>RS: publish async terminal event
    GW->>RS: consume event
    GW->>GW: decide re-entry policy
    GW->>RT: trigger follow-up main-agent run with async result context
```

## Open Point

Webhook callback can be added later as an optional outbound integration.
Current baseline is Redis Stream + gateway consumer group orchestration.
