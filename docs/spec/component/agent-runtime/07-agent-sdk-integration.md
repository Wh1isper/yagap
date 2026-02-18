# Agent Runtime Agent SDK Integration

## Scope

This document defines the integration boundary between `agent-runtime` and `ya-agent-sdk`.

Runtime uses explicit abstractions to isolate SDK dependency:

- runtime context
- runtime state
- runtime environment
- runtime SDK adapter

## Design Principles

- Keep SDK coupling behind adapter boundary
- Keep runtime state aligned with session bundle model
- Keep abstractions extensible without business coupling
- Keep lifecycle mapping explicit and predictable

## Integration Architecture

```mermaid
flowchart LR
    subgraph Runtime[agent-runtime]
        RC[Runtime Context]
        RS[Runtime State]
        RE[Runtime Environment]
        ADP[Runtime SDK Adapter]
    end

    subgraph SDK[ya-agent-sdk]
        AC[AgentContext]
        ST[ResumableState]
        ENV[Environment]
        RUN[create_agent / stream_agent]
    end

    RC --> ADP
    RS --> ADP
    RE --> ADP

    ADP --> AC
    ADP --> ST
    ADP --> ENV
    ADP --> RUN
```

## Runtime Abstraction Responsibilities

| Abstraction         | Responsibility                                             |
| ------------------- | ---------------------------------------------------------- |
| Runtime Context     | Runtime-scoped execution context and control metadata      |
| Runtime State       | Serializable runtime state for persistence and resume      |
| Runtime Environment | Runtime environment contract for execution and tool access |
| Runtime SDK Adapter | Mapping between runtime abstractions and SDK primitives    |

## Session Bundle Alignment

```mermaid
flowchart TB
    subgraph SessionBundle[Persisted Session Bundle]
        ES[environment_state]
        CS[context_state]
        MS[message_history_state]
    end

    subgraph Runtime
        RC[Runtime Context]
        RS[Runtime State]
        RE[Runtime Environment]
    end

    ES --> RE
    CS --> RC
    MS --> RS

    RE --> ES
    RC --> CS
    RS --> MS
```

## Lifecycle Mapping

```mermaid
sequenceDiagram
    participant SS as Session Store
    participant RT as agent-runtime
    participant SDK as ya-agent-sdk

    SS-->>RT: load session bundle
    RT->>RT: build runtime context/state/environment
    RT->>SDK: map to AgentContext/ResumableState/Environment
    SDK-->>RT: stream execution and updates
    RT->>RT: export runtime context/state/environment
    RT->>SS: commit session bundle
```

## Extensibility Goals

- context schema evolution under runtime ownership
- state schema evolution under runtime ownership
- environment implementation swap with stable runtime contract
- SDK upgrade isolation through adapter layer

## Out of Scope

- concrete class signatures and implementation details
- provider-specific model tuning logic
- gateway-side business integration rules
