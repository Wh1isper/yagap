# Agent Runtime Architecture

## Scope

This document defines the high-level architecture of `agent-runtime` in YAGAP.

`agent-runtime` focuses on three core capabilities:

- Runtime management for in-flight agent runs
- Custom runtime event system and SSE streaming
- Immutable session snapshot persistence

The runtime is built on `ya-agent-sdk` (a fork of `pai-agent-sdk`).

## Design Principles

- Keep runtime minimal and execution-focused
- Keep pipeline explicit but lightweight for future extension
- Keep session state immutable with versioned snapshots
- Keep infrastructure simple: Redis + S3/Local object storage
- Keep boundary clean: gateway owns business policy, runtime owns execution lifecycle

## Relationship with Other Services

```mermaid
flowchart LR
    subgraph Clients[Clients]
        U1[HTTP Client]
        U2[Discord/Telegram via Gateway Bridge]
    end

    subgraph Gateway[Gateway Service]
        GAPI[HTTP API]
        GBIZ[Business Policy and API Override]
        GJOB[Cronjob Trigger]
    end

    subgraph Runtime[Agent Runtime Service]
        RAPI[Runtime API]
        RCORE[Run Lifecycle and Pipeline]
        REVT[Event System and SSE]
        RSES[Session Snapshot Manager]
    end

    subgraph Infra[Infrastructure]
        REDIS[(Redis)]
        OBJ[(S3 / Local Object Storage)]
    end

    subgraph External[External Dependencies]
        LLM[LLM Providers]
    end

    U1 --> GAPI
    U2 --> GAPI

    GAPI --> GBIZ
    GJOB --> GBIZ
    GBIZ --> RAPI

    RAPI --> RCORE
    RCORE --> REVT
    RCORE --> RSES

    REVT <--> REDIS
    RSES <--> OBJ
    RCORE --> LLM
```

## Runtime Component Model

```mermaid
flowchart LR
    API[Runtime API Layer] --> PM[Pipeline Manager]
    PM --> ARM[Agent Run Manager]

    ARM --> SDK[ya-agent-sdk Adapter]
    ARM --> ASM[Agent State Manager]
    ASM --> SSM[Session Snapshot Manager]

    ARM --> EBUS[Event Bus]
    EBUS --> SSE[SSE Stream Adapter]

    EBUS <--> REDIS[(Redis)]
    SSM <--> OBJ[(S3 / Local Object Storage)]
```

## Internal Responsibilities

| Component                | Responsibility                                                            |
| ------------------------ | ------------------------------------------------------------------------- |
| Runtime API Layer        | Accept run/stream/control requests from gateway                           |
| Pipeline Manager         | Execute minimal pipeline stages in fixed order                            |
| Agent Run Manager        | Manage run lifecycle (`created -> running -> completed/failed/cancelled`) |
| Agent State Manager      | Map runtime state to/from SDK resumable state                             |
| Session Snapshot Manager | Load base snapshot and persist next immutable snapshot                    |
| Event Bus                | Normalize runtime events and distribute to consumers                      |
| SSE Stream Adapter       | Convert internal events into SSE stream contract                          |
| ya-agent-sdk Adapter     | Encapsulate integration with `create_agent` / `stream_agent`              |

## Minimal Pipeline Shape

```mermaid
flowchart LR
    A[Stage 1 Prepare Run Context] --> B[Stage 2 Execute Agent Stream]
    B --> C[Stage 3 Emit Runtime Events]
    C --> D[Stage 4 Commit Session Snapshot]
    D --> E[Stage 5 Finalize Run]
```

## Runtime-Gateway Boundary

Gateway responsibilities:

- Authentication and authorization
- Business identity and policy enforcement
- API-level override decisions

Runtime responsibilities:

- Execute run with resolved inputs
- Manage run lifecycle and in-flight control
- Manage event production and SSE output
- Persist immutable session snapshots

## Storage Assumptions

- Redis stores transient runtime data and event-distribution buffers
- S3/Local object storage stores immutable session snapshots
- No database dependency in current phase

## Out of Scope

- A/B testing and experiment routing
- Git/business workspace operations
- Complex multi-pipeline orchestration
- Multi-region routing and failover design
