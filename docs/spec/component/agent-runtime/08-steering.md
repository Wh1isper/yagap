# Agent Runtime Steering

## Scope

This document defines real-time steering for in-flight runs in `agent-runtime`.

Steering allows gateway (or authorized clients through gateway) to inject control messages into a running agent without restarting the run.

## Design Principles

- Steering targets `run_id` as the control identity
- Steering is runtime control-plane data, not session persistence data
- Steering is best-effort near-real-time and bounded by run lifecycle
- Steering should be consistent for sync runs and async runs

## Steering Architecture

```mermaid
flowchart LR
    subgraph Gateway[gateway]
        API[Steering API]
    end

    subgraph Runtime[agent-runtime]
        CTRL[Run Control Service]
        BRIDGE[Steering Bridge]
        BUS[SDK Message Bus]
        RUN[In-flight Agent Run]
    end

    subgraph Infra[Redis]
        SSTREAM[(runtime:steering:run_id)]
    end

    API --> CTRL
    CTRL --> SSTREAM
    SSTREAM --> BRIDGE
    BRIDGE --> BUS
    BUS --> RUN
```

## Steering Lifecycle

```mermaid
sequenceDiagram
    participant GW as gateway
    participant RT as agent-runtime
    participant RS as Redis Steering Stream
    participant AG as In-flight Agent

    GW->>RT: post steering(run_id, message)
    RT->>RS: append steering message
    RT->>RT: bridge draws pending steering messages
    RT->>AG: inject steering into next model turn
    AG-->>RT: continue run with updated guidance
```

## Steering Message Semantics

- Steering message is linked to one `run_id`
- Messages are consumed only while run is active
- Duplicate delivery is tolerated by run-side dedup strategy
- Steering stream expires after run termination plus grace window

## Boundary with Session and Events

- Steering messages are not part of session bundle
- Steering activity can emit runtime control events for observability
- Terminal run events remain the source of completion/failure truth

## Sync and Async Behavior

- Sync main-agent run: steering is consumed during long connection lifecycle
- Async run/subagent: steering is consumed while background run remains active

Both use the same `run_id` control path.

## Out of Scope

- Detailed steering payload schema
- Gateway authentication model for steering endpoint
- UX-level policy for who can steer and when
