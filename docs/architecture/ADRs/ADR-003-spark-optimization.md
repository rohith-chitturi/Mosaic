# ADR-003: Targeted Spark Processing

**Date:** 2026-09-03
**Status:** Accepted

## Context
Profiling every column against every column is an O(N²) problem. Pure Spark jobs over the entire enterprise data lake fail to scale.

## Decision
Utilize a two-tier Candidate Engine. Cheap Python/SQL blocking heuristics reduce candidates. Spark is invoked only on plausible candidates, utilizing aggressive optimization strategies (AQE, broadcast joins, column pruning, skew detection) rather than naive caching.

## Consequences
- Reduces computational overhead drastically.
- Requires maintaining dual implementations for simple filtering vs deep Spark comparison.
