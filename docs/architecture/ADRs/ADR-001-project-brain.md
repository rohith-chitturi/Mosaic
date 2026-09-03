# ADR-001: Project Brain Architecture

**Date:** 2026-09-03
**Status:** Accepted

## Context
MOSAIC requires long-term memory across multiple disparate engineering sessions (or AI autonomous agent sessions). Standard contextual memory evaporates between sessions.

## Decision
Establish `.brain/` within the repository itself as the definitive source of truth for Project State, Architecture State, Decisions, and Phase progression. The `.brain/` is a first-class component of the engineering workflow.

## Consequences
- Requires strict updates before merging any PR.
- Ensures absolute context recovery regardless of the executing agent or engineer.
