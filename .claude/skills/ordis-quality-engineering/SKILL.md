---
name: ordis-quality-engineering
description: Use when facing test failures, performance issues, or resilience concerns - routes to specific quality engineering skills based on symptoms (flaky tests, slowness, failures under load)
---

# Ordis Quality Engineering

## Overview

**Systematic quality engineering through symptom-based skill routing.**

This hub routes you to the right quality engineering skill based on observable symptoms. Instead of scanning 11 skills, match your symptom to get the correct skill immediately.

**Core principle:** Symptoms reveal the skill you need.

**What skills provide:** Each skill gives implementation guidance (HOW to fix), not just diagnosis. Skills are complementary - use multiple skills in sequence for complete solutions.

## Quick Symptom Router

**START HERE** - Match your symptom, get your skill:

| Symptom | Route To | Why |
|---------|----------|-----|
| Tests pass alone, fail in suite | e2e-test-isolation | Shared state/resource conflicts |
| Test passed but feature broken | e2e-assertion-strategies | Assertions miss actual failures |
| Can't reproduce test failure | e2e-test-data-management | Data dependencies/drift |
| Tests fail randomly in CI | e2e-test-isolation + e2e-test-data-management | Check both isolation and data |
| "Is this slow?" | performance-baselines | Need measurable thresholds |
| Production slowness | performance-profiling-workflow | Symptom → root cause diagnosis |
| Users report slowness | performance-profiling-workflow | Same as production slowness |
| System slow under load | load-testing-patterns | Load-related bottlenecks |
| Need capacity planning | load-testing-patterns | Realistic load simulation |
| Does retry actually work? | fault-injection-testing | Verify failure handling |
| How to break this safely? | chaos-experiment-design | Safe, bounded experiments |
| Manager wants chaos testing | chaos-experiment-design | Start with safe planning |
| Does graceful degradation work? | resilience-verification | Test recovery mechanisms |
| Tests take too long | test-pyramid-balancing | Wrong test level mix |
| Why did this test fail? | test-observability | Need execution visibility |

## Decision Patterns

**Note:** Patterns show typical sequences. Reorder based on constraints (time, resources) but DON'T skip skills - accelerate or defer instead.

### Pattern 1: Flaky Tests
```
Symptom → e2e-test-isolation (find root cause) [REQUIRED]
Then → test-observability (prevent recurrence) [defer if deadline]

Under deadline: Fix root cause first, add observability later.
Don't skip isolation - observability alone won't fix flaky tests.
```

### Pattern 2: Performance Investigation
```
Unknown slowness → performance-profiling-workflow (diagnose) [REQUIRED FIRST]
Then BASED ON FINDINGS:
  → performance-baselines (if baseline drift)
  → load-testing-patterns (if load-related)

Don't skip profiling - load testing without diagnosis = guessing.
```

### Pattern 3: Resilience Testing
```
chaos-experiment-design (plan safely) [REQUIRED FIRST]
→ fault-injection-testing (execute plan)
→ resilience-verification (validate recovery)

FIXED SEQUENCE - design before execution for safety.
Each skill handles one distinct phase.
```

### Pattern 4: New Test Suite
```
Starting fresh → test-pyramid-balancing (architecture)
Then → e2e-test-isolation (setup patterns)
Then → test-observability (instrumentation)
```

## Skill Categories

**E2E Testing (Test Reliability):**
- e2e-test-isolation - Independent tests
- e2e-assertion-strategies - Robust validation
- e2e-test-data-management - Data lifecycle

**Performance (Speed & Capacity):**
- performance-baselines - Measurable targets
- load-testing-patterns - Realistic load
- performance-profiling-workflow - Root cause diagnosis

**Chaos (Resilience & Recovery):**
- fault-injection-testing - Controlled failures
- chaos-experiment-design - Safe experiments
- resilience-verification - Recovery validation

**Automation (Architecture & Visibility):**
- test-pyramid-balancing - Test level strategy
- test-observability - Execution instrumentation

## When NOT to Use This Hub

Skip the hub and go direct when:
- You already know the exact skill you need
- Implementing a specific known pattern
- Following established team conventions

## Usage Examples

**Example 1: Intermittent Test Failure**
```
You: "Tests fail randomly in CI"
Check table: "Can't reproduce" → e2e-test-data-management
If also "pass alone, fail in suite" → e2e-test-isolation
```

**Example 2: Production Performance**
```
You: "Users report slowness"
Check table: "Production slowness" → performance-profiling-workflow
After diagnosis → performance-baselines (set targets)
```

**Example 3: Manager Wants "Chaos Testing"**
```
You: "Break things to test resilience"
Check table: "How to break safely?" → chaos-experiment-design
Then → fault-injection-testing → resilience-verification
```

## Common Mistakes

**Mistake 1: Trying all skills**
- ❌ Read all 11 skills to find the right one
- ✅ Use symptom table for immediate routing

**Mistake 2: Skipping the hub**
- ❌ Guess which skill based on name
- ✅ Match symptom first, prevents wrong skill

**Mistake 3: Using skills out of order**
- ❌ Jump to fault-injection before chaos-experiment-design
- ✅ Follow decision patterns for skill sequencing

**Mistake 4: Expecting diagnosis without implementation**
- ❌ "This skill just tells me what's wrong, not how to fix it"
- ✅ Skills provide HOW to fix, with implementation patterns and examples

**Mistake 5: Skipping skills under pressure**
- ❌ "No time for profiling, just load test"
- ✅ Accelerate or defer, don't skip
- Pattern 3 sequence is FIXED (safety-critical)

## Skill Descriptions (Reference)

**E2E Testing:**
1. **e2e-test-isolation** - Test independence through setup/teardown and state isolation
2. **e2e-assertion-strategies** - Robust assertion patterns for async systems
3. **e2e-test-data-management** - Test data lifecycle for reproducible tests

**Performance:**
4. **performance-baselines** - Establish measurable performance baselines and thresholds
5. **load-testing-patterns** - Realistic load tests revealing bottlenecks
6. **performance-profiling-workflow** - Systematic profiling from symptom to root cause

**Chaos:**
7. **fault-injection-testing** - Controlled failure injection for resilience verification
8. **chaos-experiment-design** - Safe, measurable chaos experiments with rollback
9. **resilience-verification** - Systematic testing of recovery mechanisms

**Automation:**
10. **test-pyramid-balancing** - Balance unit/integration/E2E for speed and confidence
11. **test-observability** - Instrumentation and reporting for test execution

## The Bottom Line

**Don't scan skills. Match symptoms.**

Symptom table → Skill → Apply pattern → Problem solved.

When in doubt, check the symptom table first.
