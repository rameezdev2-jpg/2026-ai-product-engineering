# Architecture and tradeoffs

Planner -> permission and approval review -> executor -> audit

The bearer-token mapping is resolved server-side before domain access. Every persisted record carries its workspace. SQL values are parameterized. SQLite WAL supports a small local workload; this is not a scale benchmark.

Implemented tool schemas, permission checks, approval gating, atomic task execution, replay protection, MCP tools and authorization evaluations.

## Boundaries

Planner, reviewer and executor are deterministic roles. No autonomous LLM agents or external business system is claimed. Local stdio inherits trusted launch credentials. Roles are per workspace in this demo; production needs per-user RBAC and separate approver identity. Audit is application-managed, not tamper-proof against database administrators.

## Interview walkthrough

Follow one request from app.py through the domain module to persistence. Explain the test that prevents cross-workspace access, the main failure mode, and the change needed for production traffic. Separate recreated career context from present implementation work.
