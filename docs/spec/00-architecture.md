# Architecture Overview

## Scope

This document defines the high-level architecture for a stateless agent platform in `yagap`, with two runtime commands:

- `gateway`: business domain entrypoint (API, policy, scheduling/cron, and routing)
- `agent-runtime`: execution engine for agentic flows with immutable `session_id` management

The design is grounded on `ya-agent-sdk` primitives:

- `AgentContext` + `ResumableState`
- `stream_agent` lifecycle/event model
- Toolset and subagent orchestration
- Message bus and sideband events
- Resumable resources abstraction

## Design Goals

- Stateless compute nodes for both `gateway` and `agent-runtime`
- Immutable session snapshots managed only by `agent-runtime`
- Clear separation between business logic and execution logic
- Deterministic replayability for audit and debugging
- Horizontal scalability and tenant-level isolation

## Non-Goals

- UI and external API contract details
- Provider-specific model tuning
- Storage engine internals

## Responsibility Boundaries

### gateway

- Owns business identity model (`tenant_id`, `user_id`, `project_id`, and optional business keys)
- Performs authentication, authorization, and policy checks
- Resolves business context to platform execution requests
- Selects and authorizes resource grants for downstream execution
- Hosts business-side orchestration such as scheduler/cron jobs

### agent-runtime

- Owns immutable platform `session_id`
- Executes agentic runs and persists snapshot versions
- Applies runtime feature/capability toggles
- Does not own business identity semantics
- Consumes only authorized execution context from `gateway`

## Logical Components

```mermaid
flowchart LR
    Client[Client / Product API]

    subgraph Gateway[Gateway]
        API[Request API]
        BizPolicy[Business Policy\nAuthN/AuthZ]
        Scheduler[Scheduler / Cron Jobs]
        SessionResolver[Business Context Resolver]
        RuntimeClient[Runtime Client]
    end

    subgraph Runtime[Agent-Runtime]
        Orchestrator[Run Orchestrator]
        SessionMgr[Immutable Session Manager]
        FeatureFlags[Feature Toggle Evaluator]
        RuntimeBuilder[Runtime Builder\ncreate_agent/stream_agent]
        EventEmitter[Event Emitter]
    end

    subgraph Persistence[Shared Persistence]
        SessionStore[(Session Snapshot Store)]
        EventStore[(Run/Event Store)]
        ArtifactStore[(Artifacts / Files)]
    end

    Client --> API
    API --> BizPolicy --> SessionResolver --> RuntimeClient
    Scheduler --> SessionResolver
    RuntimeClient --> Orchestrator

    Orchestrator --> SessionMgr
    Orchestrator --> FeatureFlags
    Orchestrator --> RuntimeBuilder
    RuntimeBuilder --> EventEmitter

    SessionMgr <--> SessionStore
    EventEmitter --> EventStore
    Orchestrator --> ArtifactStore
```

## Session Model

`agent-runtime` manages only immutable platform sessions:

- `session_id` is platform-scoped and immutable
- snapshots are append-only versions (`v0 -> v1 -> v2 ...`)
- every run reads one base version and writes one next version

```mermaid
flowchart TB
    S0[Snapshot v0\ninitial] --> S1[Snapshot v1\nafter run-1]
    S1 --> S2[Snapshot v2\nafter run-2]
    S2 --> S3[Snapshot v3\nafter run-3]

    R1[run-1 events] --> S1
    R2[run-2 events] --> S2
    R3[run-3 events] --> S3
```

Business identity (`tenant/user/project`) is maintained in `gateway` and never becomes the ownership model of runtime sessions.

## Runtime Mapping to ya-agent-sdk

Inside each run, `agent-runtime` maps snapshots to SDK runtime:

- Snapshot -> `ResumableState`
- Rebuild `AgentContext` from environment and authorized runtime inputs
- Execute with `stream_agent`
- Export next state via `ctx.export_state()`
- Persist as next immutable snapshot version

## End-to-End Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant AR as Agent-Runtime
    participant SS as Session Store
    participant ES as Event Store

    C->>G: request(business context, input)
    G->>G: auth/policy/resource authorization
    G->>AR: execute(session_id, input, authorized_context, toggles)

    AR->>SS: load latest snapshot(session_id)
    SS-->>AR: snapshot vN

    AR->>AR: rebuild runtime + run stream_agent
    AR->>ES: append lifecycle/tool/sideband events

    AR->>SS: write snapshot vN+1
    SS-->>AR: committed

    AR-->>G: output + new_version + usage
    G-->>C: response
```

## Concurrency and Consistency

For a single `session_id`, snapshot commit uses optimistic concurrency:

- read base version `vN`
- write `vN+1` with precondition `base_version == vN`
- on conflict, reject or retry based on gateway policy

## Isolation Model

- `gateway` enforces all business-level authorization and resource grants
- `agent-runtime` validates request integrity and session version consistency
- runtime persistence is partitioned for tenant-safe operations, but without embedding business identity as runtime ownership semantics

## Event and Audit Model

Persisted event stream includes:

- run lifecycle (start/complete/fail)
- model request and tool-call phases
- sideband events (handoff, compact, subagent, bus)
- usage and cost metadata

Events are correlated by `run_id` and linked to snapshot transitions.

## Failure Handling

- if run fails before snapshot commit, no new snapshot is published
- partial execution is visible through events only
- optional recovery mode may persist crash diagnostics and usage records

## Open Discussion Topics

- boundary contract between `gateway` and `agent-runtime`
- conflict retry matrix (interactive vs scheduled runs)
- snapshot granularity (per-run vs selective checkpointing)
- event retention and compaction policies
- multi-region routing and failover strategy
