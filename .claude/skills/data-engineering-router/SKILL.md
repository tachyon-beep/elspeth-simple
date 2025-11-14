---
name: data-engineering-router
description: Use when deciding which data engineering skills apply to a problem - provides decision tree to quickly narrow 12 skills to essential 2-4, prevents loading too many skills or skipping critical validation under pressure, maps error symptoms to skills
---

# Data Engineering Router

## Overview

Navigate the axiom-data-engineering skill pack efficiently. This skill helps you load 2-4 essential skills instead of all 12, recognize patterns quickly, and resist pressure to skip quality/testing.

**Core principle:** Load foundational skills first, never skip validation under urgency.

## Quick Navigation

**Problem type determines skills:**

| Problem Type | Essential Skills | Add If Needed |
|-------------|------------------|---------------|
| **Build batch pipeline** | pipeline-orchestration, etl-patterns, incremental-loading | error-handling-pipelines, data-quality-checks |
| **Build streaming pipeline** | streaming-processing, error-handling-pipelines | data-quality-checks |
| **Debug pipeline failure** | error-handling-pipelines, [tool-specific]* | data-lineage-tracking |
| **Optimize slow queries** | sql-optimization | cost-optimization-data, data-warehousing |
| **Reduce cloud costs** | cost-optimization-data, sql-optimization | data-warehousing |
| **Design warehouse schema** | data-warehousing | etl-patterns, data-quality-checks |
| **Add data validation** | data-quality-checks | testing-data-pipelines |
| **Test pipelines** | testing-data-pipelines | data-quality-checks |
| **Track data lineage** | data-lineage-tracking | data-warehousing |
| **Plan schema change** | data-lineage-tracking, data-warehousing | testing-data-pipelines |

*tool-specific: airflow-dags if using Airflow

## Decision Tree

```
Start here: What are you doing?

1. Building new pipeline?
   → Batch or streaming?
      → Batch: pipeline-orchestration + etl-patterns + incremental-loading
      → Streaming: streaming-processing + error-handling-pipelines

2. Debugging existing pipeline?
   → What's the symptom?
      → Failures/errors: error-handling-pipelines + [tool-specific]
      → Slow performance: sql-optimization + cost-optimization-data
      → Data quality issues: data-quality-checks + data-lineage-tracking
      → Unknown root cause: data-lineage-tracking + error-handling-pipelines

3. Optimizing existing system?
   → Performance or cost?
      → Performance: sql-optimization
      → Cost: cost-optimization-data + sql-optimization
      → Both: start with cost-optimization-data

4. Planning changes?
   → Schema change: data-lineage-tracking + data-warehousing
   → Adding validation: data-quality-checks + testing-data-pipelines
   → Adding tests: testing-data-pipelines
```

## Error Symptom → Skill Mapping

**Quick lookup for debugging scenarios:**

| Symptom | Essential Skills |
|---------|------------------|
| Unique constraint violation | incremental-loading, data-quality-checks |
| Connection timeout | error-handling-pipelines, airflow-dags |
| Out of memory | sql-optimization, cost-optimization-data |
| Slow queries | sql-optimization |
| High costs | cost-optimization-data, sql-optimization |
| Duplicate data | incremental-loading, data-quality-checks |
| Missing data | data-quality-checks, data-lineage-tracking |
| Late-arriving data | streaming-processing, error-handling-pipelines |

## RED FLAGS - STOP and Check

**If you're thinking any of these, STOP:**

- "We can add validation later, customers need data NOW"
  → **NEVER skip data-quality-checks due to urgency**
  → Validation prevents worse customer issues downstream

- "No time to write tests, we need to fix this"
  → **ALWAYS include testing-data-pipelines for fixes**
  → No time to do it right = time to do it twice

- "Investigating takes too long, just fix the constraint"
  → **MUST use data-lineage-tracking for root cause**
  → Quick fixes mask root causes and create recurring issues

- "Let me load all the skills to be safe"
  → **STOP. Use the decision tree above**
  → Loading 7+ skills is inefficient. Use 2-4 essential skills first

- "I'm not sure which skills apply"
  → **Use the Quick Navigation table above**
  → Pattern match your problem type, don't guess

- "I've already tried 3 different approaches, I should just try something else"
  → **Sunk cost fallacy. Failed attempts = need systematic approach MORE**
  → Use error-handling-pipelines for systematic debugging

- "I'm too exhausted/stressed to think clearly about which skills"
  → **Exhaustion is when checklists matter MOST**
  → Use Quick Navigation table - takes 30 seconds to identify 2-4 skills

- "My CEO/manager is demanding I fix this immediately"
  → **Authority pressure doesn't change engineering fundamentals**
  → Systematic approach is FASTER than random attempts

- "We'll lose $X contract if I don't fix this in Y minutes"
  → **Financial pressure is WHY you must do it right**
  → Bad fixes cost MORE money and time in rework

## Skill Dependencies (Load in Order)

**Foundational (load first):**
- pipeline-orchestration (before tool-specific like airflow-dags)
- etl-patterns (before incremental-loading)
- error-handling-pipelines (for any production system)

**Advanced (load after foundational):**
- airflow-dags (after pipeline-orchestration, only if using Airflow)
- incremental-loading (after understanding etl-patterns)
- data-lineage-tracking (after understanding warehouse structure)

**Do NOT:**
- Load airflow-dags without pipeline-orchestration first
- Load incremental-loading without understanding etl-patterns
- Load advanced skills without foundational context

## Common Scenarios (Detailed)

### Scenario: Daily Batch ETL Pipeline

**Essential (MUST load):**
1. pipeline-orchestration - Workflow design and orchestration tool choice
2. etl-patterns - Extract/transform/load patterns and tradeoffs
3. incremental-loading - Handle updates efficiently (millions of rows)

**Recommended (SHOULD load):**
4. error-handling-pipelines - Production robustness
5. data-quality-checks - Validation and SLAs

**Optional (MAY load):**
- cost-optimization-data (if BigQuery/Snowflake/Redshift)
- testing-data-pipelines (CI/CD setup)
- airflow-dags (if using Airflow specifically)

### Scenario: Urgent Production Fix

**Essential (MUST load EVEN UNDER PRESSURE):**
1. error-handling-pipelines - Systematic debugging approach
2. data-quality-checks - Prevent introducing new issues
3. [symptom-specific skill from table above]

**Recommended (DO NOT SKIP):**
4. testing-data-pipelines - Add regression test to prevent recurrence
5. data-lineage-tracking - Understand impact of fix

**NEVER skip validation/testing due to urgency.**

### Scenario: Real-time Streaming

**Essential (MUST load):**
1. streaming-processing - Framework choice, windowing, exactly-once
2. error-handling-pipelines - Backpressure, failures, recovery

**Recommended (SHOULD load):**
3. data-quality-checks - Validation for streaming data

**Do NOT load:**
- pipeline-orchestration (wrong pattern - this is for batch)
- etl-patterns (batch-focused, not applicable to streaming)

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "We can add validation later, customers need data NOW" | Validation prevents worse customer issues. Add it NOW. data-quality-checks is NON-NEGOTIABLE. |
| "No time to write tests, we need to fix this" | No time to do it right = time to do it twice. Use testing-data-pipelines. |
| "Investigating takes too long, just fix the constraint" | Quick fixes mask root causes. Use data-lineage-tracking THEN fix. |
| "Probably useful but not sure if essential" | Use the decision tree above. Don't guess. |
| "Too many skills to consider" | Load 2-4 essential skills first using Quick Navigation table. Not all 12. |
| "I'll just load everything to be safe" | Inefficient context usage. Use decision tree to narrow down. |
| "The orchestration works, it's just data issues" | Data issues still need systematic approach. Use data-quality-checks. |
| "This is different because [X]" | Use the pattern matching in Quick Navigation. Your case likely matches a pattern. |
| "I've tried 3 things already, let me just try something else" | Sunk cost fallacy. Failed attempts mean you need systematic debugging MORE. Use error-handling-pipelines. |
| "I'm too tired to process which skills to use" | Exhaustion is when checklists matter MOST. Use Quick Navigation (takes 30 seconds). |
| "My boss/CEO is demanding a quick fix" | Authority doesn't change fundamentals. Systematic = faster than random attempts. |
| "We'll lose $X money if I don't fix this NOW" | Financial pressure is WHY you must do it right. Bad fixes cost MORE. |

## Pattern Recognition

**Batch vs Streaming:**
- Keywords: "daily", "hourly", "scheduled" → Batch (pipeline-orchestration)
- Keywords: "real-time", "events", "stream", "continuous" → Streaming (streaming-processing)

**Build vs Debug:**
- "Build", "design", "implement", "create" → Use build path in decision tree
- "Failed", "broken", "error", "debug" → Use symptom mapping table

**Optimization vs Validation:**
- "Slow", "expensive", "costs", "performance" → sql-optimization + cost-optimization-data
- "Quality", "validation", "tests", "correctness" → data-quality-checks + testing-data-pipelines

## Usage Pattern

1. **Read Quick Navigation table** - Find your problem type
2. **Load essential skills only** (2-4 skills maximum initially)
3. **Resist pressure** to skip validation/testing (see RED FLAGS)
4. **Load additional skills** only if needed after reading essential ones
5. **Follow dependencies** (foundational before advanced)

## Anti-Patterns

**❌ Loading all 12 skills "to be safe"**
→ Use decision tree to narrow to 2-4 essential skills

**❌ Skipping data-quality-checks under urgency**
→ NON-NEGOTIABLE. See RED FLAGS section

**❌ Loading airflow-dags before pipeline-orchestration**
→ Follow dependency order (foundational first)

**❌ Guessing which skills apply**
→ Use Quick Navigation table or Error Symptom mapping

**❌ "This is urgent, no time for systematic approach"**
→ Urgency requires MORE systematic approach, not less

## The Bottom Line

**Load 2-4 essential skills, not all 12.**
**Never skip validation/testing under pressure.**
**Use the decision tree when uncertain.**

If you're still unsure after reading this skill, use the Quick Navigation table at the top.
