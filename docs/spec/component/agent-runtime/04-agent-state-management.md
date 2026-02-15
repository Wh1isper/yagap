# Agent Runtime Agent State Management

## Scope

This document defines how `agent-runtime` manages agent state across one run lifecycle.

State management focuses on three persisted session parts:

- `environment_state`
- `context_state`
- `message_history_state` (main agent)

These three parts are restored together and committed together as one session bundle.

## Design Principles

- Keep persisted state minimal and execution-oriented
- Keep state boundaries explicit by concern
- Keep commit atomic across all persisted session parts
- Keep run control data separate from persisted session data

## State Boundary Model

```mermaid
flowchart TB
    subgraph PersistedSessionBundle[Persisted Session Bundle]
        ES[environment_state]
        CS[context_state]
        MS[message_history_state]
        PS[parent_session_id]
    end

    subgraph RuntimeEphemeralState[Runtime Ephemeral State]
        RI[run_id]
        RS[run_status]
        SC[stream_cursor / delivery state]
    end
```

Persisted session bundle is durable and immutable.
Runtime ephemeral state is execution-time control data.

## Run Lifecycle State Flow

```mermaid
sequenceDiagram
    participant GW as Gateway
    participant RT as agent-runtime
    participant SS as Session Store

    GW->>RT: execute(base_session_id, input)
    RT->>RT: allocate run_id and session_id

    RT->>SS: load_bundle(base_session_id)
    SS-->>RT: environment_state + context_state + message_history_state

    RT->>RT: restore runtime from bundle
    RT->>RT: execute agent stream
    RT->>RT: export updated states

    RT->>SS: commit_bundle(session_id, parent=base_session_id)
    SS-->>RT: committed

    RT-->>GW: result + run_id + session_id
```

## Runtime Identity in State Management

- `run_id` identifies one execution instance for control operations
- `session_id` is allocated at run start and used as commit target
- `base_session_id` is the immutable input snapshot reference

This allows downstream references to be stable during execution while preserving immutable session semantics.

## Sync and Async State Handling

```mermaid
flowchart LR
    subgraph SyncRun[Sync Main Agent Run]
        S1[Long-lived gateway connection]
        S2[No durable run-status store required]
    end

    subgraph AsyncRun[Async Agent Run]
        A1[Shared run status in Redis]
        A2[Durable session bundle in Session Store]
    end
```

Both sync and async runs use the same persisted session bundle model.
Only async runs require shared runtime status for later consumption/control.

## Failure Semantics

- If execution fails before commit, no new session bundle is published
- Persisted bundle is all-or-nothing
- Runtime control state can end in failed/cancelled without mutating existing sessions
