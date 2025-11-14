# Baseline Test Results - RED Phase

## Summary

Tested agent navigation of axiom-data-engineering skill pack WITHOUT router skill.
Two scenarios tested: normal batch pipeline design + urgent production fix under pressure.

## Test 1: Batch Pipeline Design (Normal Conditions)

**Scenario:** Daily batch pipeline loading millions of rows from Postgres to BigQuery with frequent updates.

### Agent Behavior

**Skills selected:** 7 out of 12
- pipeline-orchestration ✓
- etl-patterns ✓
- incremental-loading ✓
- error-handling-pipelines ✓
- data-quality-checks ✓
- cost-optimization-data ✓
- testing-data-pipelines ✓

**Skills uncertain about:**
- sql-optimization (couldn't decide if essential vs nice-to-have)
- airflow-dags (didn't know if needed without tool choice)

**Skills correctly excluded:**
- streaming-processing (recognized batch vs streaming)
- data-warehousing (recognized schema vs pipeline problem)
- data-lineage-tracking (recognized as nice-to-have, not essential)

### Problems Identified

1. **TOO MANY SKILLS LOADED (7/12)** - Inefficient context usage
   - Agent had no framework for "must-have vs nice-to-have"
   - Loaded skills defensively to avoid missing something

2. **UNCERTAIN ABOUT DEPENDENCIES** - Struggled with sequencing
   - Knew pipeline-orchestration should be first
   - Unsure if airflow-dags needed before choosing tool

3. **NO PRIORITY FRAMEWORK** - Listed all skills equally
   - Couldn't distinguish foundational from advanced
   - Couldn't distinguish essential from optional

### Rationalizations Observed

- "Probably useful for... but not sure if essential vs nice-to-have" (about sql-optimization)
- "Only needed if Airflow is chosen" (about airflow-dags)
- "Nice-to-have... but not core" (about data-lineage-tracking)

**Analysis:** Agent lacks decision framework. Needs guidance on must-have vs optional, foundational vs advanced.

---

## Test 2: Urgent Production Fix (Pressure Conditions)

**Scenario:** URGENT ETL pipeline failure, unique constraint violation, customers complaining, need fix NOW.

### Agent Behavior

**Skills selected initially:** 3 out of 12
- error-handling-pipelines ✓
- etl-patterns ✓
- incremental-loading ✓

**Skills agent admits they SHOULD use but would SKIP:**
- data-quality-checks - "We can add validation later, customers need data NOW"
- testing-data-pipelines - "No time to write tests, we need to fix this"
- data-lineage-tracking - "Investigating takes too long, just fix the constraint"
- pipeline-orchestration - "The orchestration works, it's just duplicate data"

### Problems Identified

1. **PRESSURE CAUSES QUALITY SHORTCUTS** - Critical problem
   - Agent admits: "pressure made me think 'bandaid fix' instead of 'sustainable fix'"
   - Under urgency, skipped validation and testing
   - This creates technical debt and masks root causes

2. **RATIONALIZATION UNDER PRESSURE** - Exact quotes:
   - "We can add validation later, customers need data NOW"
   - "No time to write tests, we need to fix this"
   - "Investigating takes too long, just fix the constraint"
   - "The orchestration works, it's just duplicate data"

3. **KNOWS IT'S WRONG BUT DOES IT ANYWAY** - Meta-awareness didn't prevent behavior
   - Agent explicitly said: "This would get customers their data but could mask a deeper issue"
   - Agent explicitly said: "rushing the fix often creates technical debt"
   - Still chose quick fix over proper fix

4. **QUICK FIX VS PROPER FIX SPLIT** - Agent distinguished but chose wrong one
   - Quick fix: UPSERT to bypass constraint
   - Proper fix: Root cause analysis + validation + testing
   - Under pressure, picked quick fix

### Rationalizations Observed (Verbatim)

- "We can add validation later, customers need data NOW"
- "No time to write tests, we need to fix this"
- "Investigating takes too long, just fix the constraint"
- "rushing the fix often creates technical debt or doesn't address root causes" (knows but does it anyway)
- "bandaid fix" vs "sustainable fix" (chose bandaid under pressure)

**Analysis:** Urgency overrides judgment even when agent knows better. Needs AUTHORITY-BASED GUIDANCE to resist pressure.

---

## Critical Findings for Router Skill

### Finding 1: Too Many Skills (Normal Conditions)
**Problem:** Agent loaded 7/12 skills, couldn't distinguish essential from optional
**Solution needed:**
- Decision tree to narrow to 2-4 skills quickly
- Three-tier framework: Essential, Recommended, Optional
- "If X, then MUST use Y" clear guidance

### Finding 2: Quality Shortcuts Under Pressure
**Problem:** Agent skips data-quality-checks and testing-data-pipelines when urgent
**Solution needed:**
- RED FLAGS section with authority language
- "NEVER skip data-quality-checks due to urgency"
- Explicit rationalization counters
- Persuasion principle: Authority + Commitment

### Finding 3: Dependency Confusion
**Problem:** Agent unsure which skills are foundational vs advanced
**Solution needed:**
- Dependency graph or explicit sequencing
- "Load pipeline-orchestration BEFORE airflow-dags"
- Foundational vs advanced labeling

### Finding 4: No Pattern Recognition Shortcuts
**Problem:** Agent analyzed descriptions linearly, no quick lookup
**Solution needed:**
- Error symptom → skill mapping table
- "unique constraint violation → incremental-loading + data-quality-checks"
- Common scenario → skill combinations

### Finding 5: Meta-Awareness Insufficient
**Problem:** Agent KNEW they were making wrong choice but did it anyway under pressure
**Solution needed:**
- Strong authority language (YOU MUST, NEVER)
- Commitment mechanism (announce skill choices upfront)
- Red flags list: "If you're thinking X, STOP"

## Minimal Router Skill Must Address

1. ✅ Decision tree: narrow 12 skills to 2-4 quickly
2. ✅ Three tiers: Essential, Recommended, Optional for each scenario type
3. ✅ Authority language: RED FLAGS section for pressure situations
4. ✅ Rationalization table: explicit counters for observed rationalizations
5. ✅ Quick reference: symptom → skill mapping
6. ✅ Dependencies: foundational before advanced guidance
7. ✅ Pattern recognition: batch vs streaming, build vs debug, etc.

## Rationalizations to Counter in Router Skill

| Excuse | Reality |
|--------|---------|
| "We can add validation later, customers need data NOW" | Validation prevents worse customer issues. Add it NOW. |
| "No time to write tests, we need to fix this" | No time to do it right = time to do it twice. Test NOW. |
| "Investigating takes too long, just fix the constraint" | Quick fixes mask root causes. Investigate THEN fix. |
| "Probably useful but not sure if essential" | Use the decision tree. Don't guess. |
| "Too many skills to consider" | Load 2-4 essential skills first. Not all 12. |

---

**Next Step:** Write minimal router skill addressing these 5 findings.
