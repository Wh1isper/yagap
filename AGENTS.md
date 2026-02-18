# AGENTS.md

## Project Conventions

- Use `uv` for Python package and environment management.
- Use `Makefile` as the standard entrypoint for development commands.
- `docs/` is the MkDocs documentation source directory.
- Put all design/specification documents under `docs/spec/`.
- Documentation site is hosted at: `https://yagap.wh1isper.top/`.

### Spec Documents (`docs/spec/`)

- Use mermaid to draw diagrams.
- Keep documents concise and elegant; focus on high-level design only (architecture diagrams, flowcharts, swimlane diagrams, and pseudocode flows).
- Create UML diagrams only when necessary.
- Do not include code implementation details or code examples.
- `docs/spec/index.md` is a manual index page for all spec documents; update it whenever adding/removing spec files.

## Testing

- Framework: pytest with pytest-asyncio
- Style: **Function-based tests (no test classes)**, use fixtures for setup/teardown
- Reusable fixtures: Extract to `conftest.py` (module-level or shared)
- Config: pytest.ini (asyncio_mode=auto)

## Workflow

- Before implementing any new feature or modification, review the relevant documents under `docs/spec/` first.
- Keep implementation and specification updates in sync within the same change.
- Design documents may be refined during implementation when a better approach is identified.
- Always aim for the most elegant implementation that remains consistent with project conventions.
- Before commit, run `make check` and ensure both `pre-commit` and `pyright` pass.
