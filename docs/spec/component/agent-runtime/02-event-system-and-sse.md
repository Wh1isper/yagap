# Agent Runtime Event System and SSE

## Scope

This document defines the high-level event architecture of `agent-runtime`.

The design uses two event layers:

- SDK Event Layer: native events produced by `ya-agent-sdk`
- Runtime Event Layer: runtime-specific events added by `agent-runtime`

SSE exposes a unified transport protocol so external applications only consume one stable event contract.

## Design Principles

- Reuse SDK-native event semantics as the execution foundation
- Add runtime events only for lifecycle, control, and platform observability
- Keep external protocol stable even if internal event models evolve
- Keep transport concerns separate from execution concerns

## Two-Layer Event Architecture

```mermaid
flowchart LR
    subgraph SDK[ya-agent-sdk]
        SE[SDK Events]
    end

    subgraph Runtime[agent-runtime]
        RE[Runtime Events]
        NORM[Event Normalizer]
        BUS[Unified Runtime Event Bus]
    end

    subgraph Transport[SSE Transport]
        ADP[SSE Protocol Adapter]
        STREAM[Unified SSE Stream]
    end

    subgraph Consumer[External Applications]
        APP[Gateway / Client / Bridge]
    end

    SE --> NORM
    RE --> NORM
    NORM --> BUS
    BUS --> ADP
    ADP --> STREAM
    STREAM --> APP
```

## Event Layer Responsibilities

| Layer                     | Responsibility                                                |
| ------------------------- | ------------------------------------------------------------- |
| SDK Event Layer           | Provide agent execution events from `ya-agent-sdk`            |
| Runtime Event Layer       | Add runtime lifecycle and control-domain events               |
| Unified Runtime Event Bus | Merge, normalize, and order events into one runtime stream    |
| SSE Protocol Adapter      | Convert unified runtime events into transport protocol frames |

## Event Categories

```mermaid
flowchart TB
    ROOT[Unified Runtime Events]

    ROOT --> A[Agent Execution Events]
    ROOT --> B[Runtime Lifecycle Events]
    ROOT --> C[Runtime Control Events]
    ROOT --> D[Terminal Events]

    A --> A1[message_start / content_delta / tool_call / message_end]
    B --> B1[run_created / run_started / snapshot_committed]
    C --> C1[run_interrupt_requested / run_cancelled]
    D --> D1[run_completed / run_failed]
```

## Event Flow (Conceptual)

```mermaid
sequenceDiagram
    participant SDK as ya-agent-sdk
    participant RT as Runtime Event Layer
    participant BUS as Unified Event Bus
    participant SSE as SSE Adapter
    participant APP as External Application

    SDK-->>BUS: SDK execution events
    RT-->>BUS: runtime lifecycle/control events
    BUS->>SSE: normalized unified events
    SSE-->>APP: unified SSE protocol stream
    APP-->>APP: handle protocol only
```

## Unified SSE Protocol Contract

The SSE stream is defined as a transport contract over unified runtime events.

Contract goals:

- Single protocol for all upstream clients and bridges
- Consistent event envelope across SDK-origin and runtime-origin events
- Predictable terminal semantics for completion and failure

External applications are protocol consumers. They do not need to understand internal SDK/runtime event source differences.

## Ordering and Consistency Model

- Events are emitted as a single ordered stream per run
- Terminal events are final for that run stream
- Snapshot commit visibility is represented as explicit runtime events

## Boundary and Evolution

- Internal event taxonomy can evolve by layer
- SSE contract remains stable as the external compatibility surface
- New internal events are introduced through normalization before transport exposure

## Out of Scope

- Protocol field-level schema details
- Reconnect/replay mechanics
- Storage-level event retention policy
