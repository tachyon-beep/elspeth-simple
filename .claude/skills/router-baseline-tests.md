# Baseline Test Scenarios for data-engineering-router Skill

## Purpose

Test whether agents can navigate the axiom-data-engineering skill pack WITHOUT a router skill.
This is the RED phase of TDD for skill creation.

## Test Methodology

For each scenario:
1. Create subagent with access to all 12 individual skill descriptions
2. Do NOT provide router/hub skill
3. Ask the question/present the problem
4. Observe which skills they choose (or fail to choose)
5. Document exact behavior and rationalizations

## Scenarios

### Scenario 1: Batch Pipeline Design
**Query:** "I need to build a daily batch pipeline that loads customer data from a Postgres database into BigQuery. The source table has millions of rows and gets frequent updates. How should I approach this?"

**Expected skills needed:**
- pipeline-orchestration (overall workflow design)
- etl-patterns (extraction, transformation, loading patterns)
- incremental-loading (efficient updates, CDC)
- data-quality-checks (validation)

**Testing for:**
- Do they recognize this as a pipeline orchestration problem?
- Do they consider incremental loading or suggest full refresh?
- Do they think about data quality?

**Baseline hypothesis:** Agent may pick etl-patterns but miss incremental-loading and orchestration strategy.

---

### Scenario 2: Airflow Failure Debugging
**Query:** "Our Airflow DAG keeps failing with 'ConnectionTimeout' errors when calling an external API. Sometimes it works, sometimes it doesn't. The task fails after 3 retries. What should I do?"

**Expected skills needed:**
- airflow-dags (Airflow-specific debugging)
- error-handling-pipelines (retry logic, exponential backoff, transient failures)

**Testing for:**
- Do they recognize transient failure pattern?
- Do they know to look at retry configuration?
- Do they consider exponential backoff and jitter?

**Baseline hypothesis:** Agent may suggest generic debugging but miss structured retry patterns and Airflow-specific configuration.

---

### Scenario 3: High BigQuery Costs
**Query:** "Our BigQuery bill is $10k/month and growing. Most queries scan entire tables. Analysts complain queries are slow. What's the best way to reduce costs?"

**Expected skills needed:**
- sql-optimization (query rewriting, EXPLAIN plans)
- cost-optimization-data (BigQuery cost model, partitioning/clustering)
- data-warehousing (schema design considerations)

**Testing for:**
- Do they prioritize cost optimization or just performance?
- Do they understand BigQuery-specific optimization (partitioning)?
- Do they consider both query and schema changes?

**Baseline hypothesis:** Agent may suggest generic SQL optimization but miss BigQuery-specific cost strategies.

---

### Scenario 4: Real-time Event Processing
**Query:** "We need to process clickstream events in real-time (100k events/sec) and write aggregated metrics to a dashboard every 5 minutes. What architecture should we use?"

**Expected skills needed:**
- streaming-processing (Kafka, Flink, windowing)
- data-quality-checks (validation for streaming data)
- error-handling-pipelines (handling failures in streams)

**Testing for:**
- Do they recognize this as a streaming problem (not batch)?
- Do they consider windowing operations?
- Do they think about data quality in real-time?

**Baseline hypothesis:** Agent may suggest batch solutions or miss windowing patterns.

---

### Scenario 5: Testing dbt Transformations
**Query:** "We have 50 dbt models transforming data in Snowflake. How do we test these to ensure they don't break when we make changes?"

**Expected skills needed:**
- testing-data-pipelines (testing strategy, dbt tests)
- data-quality-checks (validation rules, dbt tests specifically)
- data-warehousing (understanding of transformation context)

**Testing for:**
- Do they distinguish between unit tests and data quality tests?
- Do they know dbt-specific testing approaches?
- Do they consider regression testing?

**Baseline hypothesis:** Agent may suggest generic testing but miss dbt-specific patterns and data quality testing.

---

### Scenario 6: Impact Analysis for Schema Change
**Query:** "We need to add a new column to the 'orders' table. How do we know which downstream pipelines and dashboards will be affected?"

**Expected skills needed:**
- data-lineage-tracking (impact analysis, column-level lineage)
- data-warehousing (schema evolution understanding)
- testing-data-pipelines (testing downstream impacts)

**Testing for:**
- Do they recognize this as a lineage problem?
- Do they know about lineage tools vs manual checking?
- Do they consider both pipeline and BI tool impacts?

**Baseline hypothesis:** Agent may suggest manual code search but miss lineage tooling and systematic impact analysis.

---

### Scenario 7: Urgent Production Fix (Pressure Test)
**Query:** "URGENT: Our main ETL pipeline failed overnight. Customers are complaining about stale data. The error message says 'unique constraint violation'. We need to fix this NOW and get data flowing again. What do I do?"

**Apply pressures:**
- Time pressure (URGENT, NOW)
- Authority pressure (customers complaining)
- Sunk cost (pipeline has been working until now)

**Expected skills needed:**
- error-handling-pipelines (systematic debugging, not panic fixes)
- systematic-debugging (root cause analysis)
- airflow-dags or pipeline-orchestration (depending on tool)

**Testing for:**
- Under pressure, do they skip systematic debugging?
- Do they suggest quick hacks vs proper fixes?
- Do they consider data quality implications?

**Baseline hypothesis:** Under time pressure, agent may suggest "delete the constraint" or "skip validation" instead of finding root cause.

---

## Documentation Template for Each Test

For each scenario, document:

1. **Skills mentioned by agent:**
   - List which skills they suggested using
   - Note if they missed critical skills

2. **Approach taken:**
   - What was their strategy?
   - Did they have a systematic approach or ad-hoc?

3. **Rationalizations observed:**
   - Quote exact phrases justifying their approach
   - Note any shortcuts or workarounds suggested

4. **Quality of navigation:**
   - Did they find the right skills quickly?
   - Did they load too many skills (inefficient)?
   - Did they struggle to decide which skill applies?

5. **Missing guidance:**
   - What would have helped them navigate better?
   - What decision points were unclear?

## Success Criteria for Router Skill

After implementing the router skill, agents should:

1. **Quickly identify** which 2-3 skills apply to a scenario (not all 12)
2. **Recognize patterns** (batch vs streaming, debugging vs building, optimization vs testing)
3. **Use decision trees** for ambiguous cases
4. **Load skills in order** (foundational before advanced)
5. **Know when to combine** multiple skills

---

**Next Step:** Run these scenarios with subagents and document baseline behavior.
