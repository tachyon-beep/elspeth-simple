# Axiom Data Engineering Skill Pack - Implementation Plan

## Overview

**Pack Name:** axiom-data-engineering
**Category:** development
**Skill Count:** 12
**Focus Areas:** Pipelines, ETL, Airflow, SQL optimization, warehousing, streaming
**Alignment:** Axiom's mission to make data accessible

This skill pack provides comprehensive guidance for building robust, maintainable data engineering systems with focus on pipeline orchestration, data quality, and operational excellence.

## Design Philosophy

### Core Principles

1. **Auditable by default** - Aligns with elspeth-simple's official-sensitive environment focus
2. **Production-ready patterns** - Retry logic, checkpointing, monitoring (mirrors elspeth SDA architecture)
3. **Cost-conscious** - Track and optimize resource usage
4. **Quality-first** - Data validation and testing throughout
5. **Progressive disclosure** - Start simple, scale to complex workflows

### Relationship to Elspeth-Simple

The elspeth-simple project is a data orchestration framework following Sense/Decide/Act pattern. Many data engineering patterns apply directly:

- **Pipeline orchestration** ↔ SDAOrchestrator patterns
- **Error handling** ↔ Retry logic and checkpoint management
- **Data quality** ↔ Transform plugins and validation
- **Incremental loading** ↔ Checkpoint-based resumption
- **Cost tracking** ↔ Token/cost tracking systems

## The 12 Skills

### 1. pipeline-orchestration

**Name:** `pipeline-orchestration`

**Description:** Use when designing multi-step data workflows, coordinating dependencies between tasks, or deciding between orchestration tools (Airflow, Prefect, Dagster) - provides patterns for DAG design, task dependencies, idempotency, and failure recovery

**Type:** Technique + Pattern

**Core Content:**
- Orchestration tool selection criteria (Airflow vs Prefect vs Dagster vs custom)
- DAG design patterns (linear, fan-out/fan-in, diamond, conditional)
- Idempotency patterns (dedupe strategies, upsert patterns)
- Task dependency management (explicit deps, dynamic task generation)
- Scheduling strategies (cron, interval, event-driven, sensor-based)
- Backfill patterns and historical data loading
- Cross-DAG dependencies and coordination

**Links to Existing Skills:**
- **writing-plans** - For planning complex pipeline implementations
- **systematic-debugging** - When pipelines fail unexpectedly
- **test-driven-development** - Testing DAGs before deployment

**Links to Elspeth:**
- Mirrors `StandardOrchestrator` and `ExperimentalOrchestrator` patterns
- Suite execution model (multi-cycle orchestration)
- Configuration-driven orchestration approach

**Progressive Disclosure:**
```
pipeline-orchestration/
  SKILL.md              # Overview, basic patterns, when to use
  airflow-reference.md  # Airflow-specific operators and patterns
  prefect-reference.md  # Prefect flows and tasks
  examples/
    linear-pipeline.py
    fan-out-fan-in.py
    conditional-dag.py
```

---

### 2. etl-patterns

**Name:** `etl-patterns`

**Description:** Use when extracting data from sources, transforming data structures, or loading into destinations - covers ELT vs ETL tradeoffs, incremental vs full loads, slowly changing dimensions (SCD), data deduplication, and schema evolution handling

**Type:** Pattern + Reference

**Core Content:**
- ETL vs ELT decision framework (when to transform early vs late)
- Extraction patterns:
  - Full table extraction
  - Incremental extraction (timestamp, sequence, CDC)
  - API pagination strategies
  - Database replication patterns
- Transformation patterns:
  - Type casting and validation
  - Deduplication strategies (row hash, composite keys)
  - Denormalization patterns
  - Slowly changing dimensions (SCD Type 1, 2, 3)
- Load patterns:
  - Insert-only (append)
  - Upsert (merge)
  - Replace (truncate-insert)
  - Soft deletes

**Links to Existing Skills:**
- **condition-based-waiting** - For polling APIs and waiting for data availability
- **defense-in-depth** - Multiple validation layers in transformation

**Links to Elspeth:**
- Datasource protocols (`DataSource.load()`)
- Transform plugins (`TransformPlugin.transform()`)
- ResultSink patterns (`write()` methods)
- Sense/Decide/Act mapping to Extract/Transform/Load

**Examples:**
- SCD Type 2 implementation
- CDC with Debezium pattern
- API to warehouse pipeline

---

### 3. airflow-dags

**Name:** `airflow-dags`

**Description:** Use when writing Apache Airflow DAGs, debugging task failures, handling XComs, or managing connections and variables - provides DAG authoring best practices, common operators, testing patterns, and troubleshooting workflows

**Type:** Technique + Reference

**Core Content:**
- DAG authoring best practices:
  - Task naming conventions
  - Default args configuration
  - Catchup and backfill settings
  - SLA and timeout configuration
- Common operators:
  - PythonOperator patterns
  - BashOperator usage
  - SQL operators (Postgres, BigQuery, Snowflake)
  - Sensor operators (S3, HTTP, SQL)
- XCom usage patterns and limitations
- Connection management (secrets backend, environment variables)
- Variables and macros (`{{ ds }}`, `{{ execution_date }}`)
- Testing DAGs locally
- Debugging failed tasks (logs, retries, task instance states)
- Airflow CLI common commands

**Links to Existing Skills:**
- **test-driven-development** - Testing DAGs before deployment
- **root-cause-tracing** - Debugging failed Airflow tasks
- **systematic-debugging** - When Airflow scheduler issues occur

**Links to Elspeth:**
- Similar to elspeth CLI patterns
- Configuration-driven execution
- Retry logic patterns match elspeth's retry_config

**Progressive Disclosure:**
```
airflow-dags/
  SKILL.md              # Overview, basic DAG structure
  operators.md          # Comprehensive operator reference
  sensors.md            # Sensor patterns and examples
  debugging.md          # Troubleshooting workflows
  examples/
    basic-dag.py
    sensor-dag.py
    branching-dag.py
```

---

### 4. sql-optimization

**Name:** `sql-optimization`

**Description:** Use when queries are slow, databases are resource-constrained, or analyzing query execution plans - covers indexing strategies, query rewriting, partitioning, statistics, and warehouse-specific optimizations (BigQuery, Snowflake, Redshift)

**Type:** Technique + Reference

**Core Content:**
- Query analysis workflow:
  - Reading EXPLAIN plans
  - Identifying bottlenecks (scans, joins, sorts)
  - Cost estimation
- Indexing strategies:
  - When to index (selectivity analysis)
  - Index types (B-tree, hash, bitmap)
  - Composite indexes
  - Index maintenance overhead
- Query rewriting patterns:
  - JOIN optimization (order, type selection)
  - Subquery to CTE conversion
  - Window function optimization
  - Predicate pushdown
- Partitioning strategies:
  - Range, hash, list partitioning
  - Partition pruning
  - Dynamic vs static partitioning
- Warehouse-specific optimizations:
  - BigQuery: clustering, partitioning, materialized views
  - Snowflake: clustering keys, search optimization
  - Redshift: distribution keys, sort keys, VACUUM/ANALYZE

**Links to Existing Skills:**
- **root-cause-tracing** - Finding the root cause of slow queries
- **systematic-debugging** - When optimization doesn't improve performance

**Links to Elspeth:**
- Relevant to datasource plugins that query databases
- Performance considerations for LLM processing of large datasets

**Examples:**
- Before/after query optimization
- EXPLAIN plan analysis
- Warehouse-specific optimization scripts

---

### 5. data-warehousing

**Name:** `data-warehousing`

**Description:** Use when designing warehouse schemas, choosing modeling approaches (Kimball vs Inmon), implementing star/snowflake schemas, or planning fact/dimension tables - covers dimensional modeling, data vault, slowly changing dimensions, and analytical query patterns

**Type:** Pattern + Reference

**Core Content:**
- Warehouse modeling approaches:
  - Kimball (dimensional modeling)
  - Inmon (normalized enterprise warehouse)
  - Data Vault 2.0
  - Hybrid approaches
- Schema patterns:
  - Star schema design
  - Snowflake schema tradeoffs
  - Fact table types (transactional, periodic snapshot, accumulating snapshot)
  - Dimension table design
  - Conformed dimensions
- SCD implementation in warehouse context
- Surrogate keys vs natural keys
- Aggregate tables and rollups
- Partition strategy for large fact tables
- Analytical query patterns (drill-down, roll-up, slice-dice)

**Links to Existing Skills:**
- **writing-plans** - Planning warehouse schema migrations
- **brainstorming** - Schema design sessions

**Links to Elspeth:**
- Output sinks could write to warehouse tables
- Schema design for results storage

**Progressive Disclosure:**
```
data-warehousing/
  SKILL.md              # Overview, when to use each approach
  kimball.md            # Dimensional modeling deep dive
  data-vault.md         # Data vault patterns
  examples/
    star-schema.sql
    scd-type2.sql
```

---

### 6. streaming-processing

**Name:** `streaming-processing`

**Description:** Use when processing real-time event streams, choosing streaming frameworks (Kafka, Kinesis, Flink, Spark Streaming), handling late-arriving data, or implementing windowing operations - covers stream vs batch tradeoffs, exactly-once semantics, and backpressure handling

**Type:** Technique + Pattern

**Core Content:**
- Streaming vs batch decision framework
- Streaming platforms:
  - Kafka: topics, partitions, consumer groups
  - Kinesis: streams, shards, enhanced fan-out
  - Pub/Sub: topics, subscriptions
- Processing frameworks:
  - Spark Streaming (micro-batch)
  - Flink (true streaming)
  - Kafka Streams
- Stream processing patterns:
  - Windowing (tumbling, sliding, session)
  - Watermarks and late-arriving data
  - Stateful processing (aggregations, joins)
  - Exactly-once semantics
- Schema evolution in streams (Avro, Protobuf)
- Backpressure handling
- Stream-to-warehouse patterns

**Links to Existing Skills:**
- **defense-in-depth** - Multiple validation layers for streaming data
- **condition-based-waiting** - Patterns for waiting on stream readiness

**Links to Elspeth:**
- Could extend elspeth to support streaming datasources
- Real-time LLM processing patterns

**Examples:**
- Kafka consumer with Avro
- Flink windowing operation
- Stream to BigQuery pipeline

---

### 7. data-quality-checks

**Name:** `data-quality-checks`

**Description:** Use when implementing data validation, detecting data anomalies, setting up quality gates, or defining SLAs for data freshness and completeness - covers Great Expectations, Soda, dbt tests, custom validation frameworks, and alerting strategies

**Type:** Technique + Pattern

**Core Content:**
- Data quality dimensions:
  - Completeness (null checks, required fields)
  - Accuracy (range checks, format validation)
  - Consistency (referential integrity, cross-field validation)
  - Timeliness (freshness checks, latency SLAs)
  - Uniqueness (duplicate detection)
- Testing frameworks:
  - Great Expectations (expectations, data docs)
  - Soda Core (checks as YAML)
  - dbt tests (schema, data tests)
  - Custom validation in Python
- Quality gate patterns:
  - Pre-load validation
  - Post-load validation
  - Quarantine tables for bad data
- Alerting strategies:
  - Quality metrics dashboards
  - Alert fatigue prevention
  - SLA breach notifications
- Continuous monitoring patterns

**Links to Existing Skills:**
- **test-driven-development** - Writing tests for data quality
- **testing-anti-patterns** - Avoiding common pitfalls in data testing
- **verification-before-completion** - Always verify data quality before marking complete

**Links to Elspeth:**
- Transform plugins for validation (`early_stop` plugin pattern)
- Quality gates before ACT phase
- Metrics plugins for tracking quality

**Progressive Disclosure:**
```
data-quality-checks/
  SKILL.md                      # Overview, quality dimensions
  great-expectations.md         # GX patterns and examples
  dbt-tests.md                  # dbt testing patterns
  custom-validation.md          # Python validation frameworks
  examples/
    ge-suite.py
    dbt-test.sql
```

---

### 8. incremental-loading

**Name:** `incremental-loading`

**Description:** Use when loading only new/changed data instead of full refreshes, implementing CDC (Change Data Capture), tracking high-water marks, or handling deletions in source systems - covers timestamp-based, log-based CDC, and merge strategies for efficient incremental updates

**Type:** Technique

**Core Content:**
- Incremental strategies:
  - Timestamp-based (updated_at, created_at)
  - Sequence-based (auto-increment IDs)
  - Log-based CDC (database logs, Debezium)
  - File-based (tracking processed files)
- High-water mark patterns:
  - State management (database table, file, Airflow Variable)
  - Atomic state updates
  - Recovery from failures
- Handling edge cases:
  - Late-arriving updates
  - Deletions in source (soft deletes, tombstone records)
  - Time zone handling
  - Clock skew
- Merge strategies:
  - MERGE/UPSERT SQL
  - Delete + Insert pattern
  - Staging table approach
- Full refresh fallback (when to do it)

**Links to Existing Skills:**
- **defense-in-depth** - Multiple layers to ensure no data loss
- **verification-before-completion** - Verify incremental loads are complete

**Links to Elspeth:**
- Checkpoint patterns (`CheckpointManager`)
- Resume processing from last checkpoint
- Field-based tracking (similar to checkpoint field)

**Examples:**
- Timestamp-based incremental load
- CDC with Debezium
- High-water mark state management

---

### 9. error-handling-pipelines

**Name:** `error-handling-pipelines`

**Description:** Use when pipelines fail unexpectedly, implementing retry logic with exponential backoff, designing dead letter queues, or ensuring data consistency during failures - covers transactional patterns, compensating transactions, circuit breakers, and alert escalation

**Type:** Technique + Pattern

**Core Content:**
- Failure modes in pipelines:
  - Transient failures (network, rate limits)
  - Data quality failures
  - Schema changes
  - Resource exhaustion
- Retry patterns:
  - Exponential backoff
  - Jitter to prevent thundering herd
  - Max retry limits
  - Idempotent operations
- Dead letter queues:
  - When to use DLQ
  - DLQ processing strategies
  - Manual intervention workflows
- Transactional patterns:
  - Database transactions
  - Two-phase commit
  - Compensating transactions
  - Saga pattern
- Circuit breakers:
  - When to open circuit
  - Recovery detection
  - Fallback strategies
- Monitoring and alerting:
  - Pipeline health metrics
  - Error rate tracking
  - Alert escalation policies

**Links to Existing Skills:**
- **systematic-debugging** - Debugging pipeline failures
- **root-cause-tracing** - Finding root cause of failures
- **defense-in-depth** - Multiple error handling layers

**Links to Elspeth:**
- Direct mapping to `retry_config` patterns
- Checkpoint-based recovery
- `EarlyStopCoordinator` patterns
- Robust error handling in SDARunner

**Examples:**
- Exponential backoff implementation
- DLQ with manual review workflow
- Circuit breaker pattern in Python

---

### 10. cost-optimization-data

**Name:** `cost-optimization-data`

**Description:** Use when cloud data warehouse costs are high, optimizing query performance for cost reduction, choosing between compute/storage tradeoffs, or implementing budget alerts - covers BigQuery, Snowflake, Redshift cost models, query optimization for cost, partitioning/clustering strategies, and resource monitoring

**Type:** Technique + Pattern

**Core Content:**
- Cloud warehouse cost models:
  - BigQuery: slots, on-demand vs flat-rate
  - Snowflake: credits, warehouse sizing, auto-suspend
  - Redshift: node types, reserved instances, pause/resume
- Query cost optimization:
  - Partition pruning (reduce data scanned)
  - Projection pushdown (SELECT only needed columns)
  - Materialized views for expensive queries
  - Query result caching
- Storage optimization:
  - Compression (codec selection)
  - Partitioning strategies
  - Data lifecycle policies (archival, deletion)
  - Table clustering
- Compute optimization:
  - Warehouse sizing (right-sizing)
  - Auto-suspend/auto-resume
  - Query queuing vs scaling out
  - Spot/preemptible instances
- Monitoring and budgets:
  - Cost dashboards
  - Budget alerts
  - Query cost attribution (tagging, labeling)
- Development cost controls:
  - Query preview limits
  - Dev/staging resource caps

**Links to Existing Skills:**
- **sql-optimization** - Optimizing queries reduces cost
- **verification-before-completion** - Verify cost impact before deploying

**Links to Elspeth:**
- Cost tracking patterns (`CostTracker` interface)
- Token usage monitoring similar to warehouse cost monitoring
- Budget gates (`early_stop` based on cost)

**Examples:**
- BigQuery cost reduction workflow
- Snowflake warehouse auto-suspend
- Cost monitoring dashboard queries

---

### 11. data-lineage-tracking

**Name:** `data-lineage-tracking`

**Description:** Use when tracking data origins, understanding downstream impacts of changes, implementing compliance requirements (GDPR, CCPA), or debugging data quality issues - covers lineage tools (OpenLineage, DataHub, Marquez), column-level lineage, impact analysis, and metadata management

**Type:** Technique + Reference

**Core Content:**
- Why lineage matters:
  - Impact analysis (upstream/downstream)
  - Root cause analysis for data quality
  - Compliance requirements
  - Documentation and knowledge sharing
- Lineage levels:
  - Dataset-level (table to table)
  - Column-level (field to field)
  - Job-level (which process produced what)
- Lineage tools:
  - OpenLineage standard
  - DataHub (LinkedIn)
  - Marquez (WeWork)
  - dbt docs
  - Cloud vendor tools (BigQuery lineage, AWS Glue)
- Capturing lineage:
  - Automatic extraction (SQL parsing)
  - Instrumentation (Airflow OpenLineage integration)
  - Manual annotation
- Lineage queries:
  - "What tables does this job depend on?"
  - "Which jobs will break if I change this table?"
  - "Where did this value come from?"
- Metadata management:
  - Business glossary
  - Data catalog
  - Data quality metrics

**Links to Existing Skills:**
- **root-cause-tracing** - Using lineage for debugging
- **systematic-debugging** - When lineage tools fail

**Links to Elspeth:**
- Could extend elspeth with OpenLineage integration
- Tracking LLM processing lineage
- ConfigurationMerger precedence similar to lineage tracking

**Progressive Disclosure:**
```
data-lineage-tracking/
  SKILL.md              # Overview, why lineage matters
  openlineage.md        # OpenLineage standard
  tools-comparison.md   # Tool selection guide
  examples/
    airflow-openlineage.py
    dbt-lineage-query.sql
```

---

### 12. testing-data-pipelines

**Name:** `testing-data-pipelines`

**Description:** Use when writing tests for data pipelines, validating transformations, mocking external dependencies, or setting up CI/CD for data workflows - covers unit tests for transformations, integration tests for pipelines, data quality tests, and test data generation strategies

**Type:** Technique

**Core Content:**
- Testing pyramid for data pipelines:
  - Unit tests (transformation logic)
  - Integration tests (full pipeline)
  - Data quality tests (validation rules)
- Unit testing patterns:
  - Testing SQL transformations (dbt tests, SQLMesh)
  - Testing Python transformations (pytest)
  - Mocking external dependencies (databases, APIs)
  - Test data fixtures
- Integration testing:
  - Local pipeline execution
  - Docker-based testing (database containers)
  - Airflow DAG testing
  - End-to-end tests
- Data quality testing:
  - Schema validation
  - Data contract testing
  - Statistical tests (distribution checks)
  - Regression tests (golden datasets)
- Test data strategies:
  - Synthetic data generation
  - Sampling production data
  - Anonymization/masking
  - Snapshot testing
- CI/CD for data pipelines:
  - Pre-commit hooks (linting SQL, Python)
  - CI pipeline (test execution, deployment)
  - Environment promotion (dev → staging → prod)
  - Blue/green deployments

**Links to Existing Skills:**
- **test-driven-development** - Core TDD principles for data pipelines
- **testing-anti-patterns** - Avoiding common pitfalls
- **testing-skills-with-subagents** - Testing skill implementations
- **condition-based-waiting** - Waiting for test environments

**Links to Elspeth:**
- Testing patterns for elspeth plugins
- Test structure in `tests/` directory
- pytest fixtures and markers
- Integration test patterns

**Examples:**
- dbt unit test
- Airflow DAG test
- Mocking database connections
- CI/CD pipeline configuration

---

## Skill Pack Organization

### Directory Structure

```
.claude/skills/
├── axiom-data-engineering/
│   ├── PACK.md                     # Pack overview, skill index
│   ├── pipeline-orchestration/
│   │   ├── SKILL.md
│   │   ├── airflow-reference.md
│   │   ├── prefect-reference.md
│   │   └── examples/
│   ├── etl-patterns/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── airflow-dags/
│   │   ├── SKILL.md
│   │   ├── operators.md
│   │   ├── sensors.md
│   │   ├── debugging.md
│   │   └── examples/
│   ├── sql-optimization/
│   │   ├── SKILL.md
│   │   ├── explain-plans.md
│   │   └── warehouse-specifics.md
│   ├── data-warehousing/
│   │   ├── SKILL.md
│   │   ├── kimball.md
│   │   ├── data-vault.md
│   │   └── examples/
│   ├── streaming-processing/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── data-quality-checks/
│   │   ├── SKILL.md
│   │   ├── great-expectations.md
│   │   ├── dbt-tests.md
│   │   └── examples/
│   ├── incremental-loading/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── error-handling-pipelines/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── cost-optimization-data/
│   │   ├── SKILL.md
│   │   └── warehouse-specifics.md
│   ├── data-lineage-tracking/
│   │   ├── SKILL.md
│   │   ├── openlineage.md
│   │   ├── tools-comparison.md
│   │   └── examples/
│   └── testing-data-pipelines/
│       ├── SKILL.md
│       └── examples/
```

### Pack Overview File (PACK.md)

The `PACK.md` file serves as the entry point:

```markdown
---
name: Axiom Data Engineering
description: Comprehensive data engineering skill pack covering pipelines, ETL, Airflow, SQL optimization, warehousing, and streaming
category: development
---

# Axiom Data Engineering Skill Pack

12 skills for building production-grade data pipelines.

## Quick Reference

**Pipeline orchestration & workflow:**
- pipeline-orchestration - DAG design, task dependencies, scheduling
- airflow-dags - Airflow-specific patterns and debugging
- error-handling-pipelines - Retry logic, DLQ, circuit breakers

**Data movement & transformation:**
- etl-patterns - Extract, transform, load patterns
- incremental-loading - CDC, high-water marks, merge strategies
- streaming-processing - Real-time event processing

**Data storage & modeling:**
- data-warehousing - Schema design, dimensional modeling
- sql-optimization - Query performance and indexing

**Quality & observability:**
- data-quality-checks - Validation, testing frameworks
- data-lineage-tracking - Tracking data origins and impacts
- testing-data-pipelines - Unit, integration, quality tests

**Operations:**
- cost-optimization-data - Cloud warehouse cost management
```

## Cross-Skill Dependencies

### Strong Dependencies (MUST understand first)

1. **pipeline-orchestration** depends on:
   - superpowers:**test-driven-development** (testing DAGs)
   - superpowers:**systematic-debugging** (debugging orchestrator)

2. **error-handling-pipelines** depends on:
   - superpowers:**defense-in-depth** (multiple error handling layers)
   - axiom:**pipeline-orchestration** (understanding orchestration first)

3. **testing-data-pipelines** depends on:
   - superpowers:**test-driven-development** (core TDD principles)
   - superpowers:**testing-anti-patterns** (avoiding pitfalls)
   - axiom:**pipeline-orchestration** (what you're testing)

4. **data-lineage-tracking** depends on:
   - superpowers:**root-cause-tracing** (using lineage for debugging)
   - axiom:**pipeline-orchestration** (understanding pipeline structure)

### Soft Dependencies (helpful but not required)

- **sql-optimization** ↔ **cost-optimization-data** (optimization reduces cost)
- **data-quality-checks** ↔ **testing-data-pipelines** (quality tests are a form of testing)
- **incremental-loading** ↔ **etl-patterns** (incremental is an ETL pattern)
- **streaming-processing** ↔ **etl-patterns** (streaming is an alternative to batch ETL)

## Implementation Priority

### Phase 1: Foundation (Critical for any data work)

1. **pipeline-orchestration** - Core orchestration patterns
2. **etl-patterns** - Basic data movement patterns
3. **error-handling-pipelines** - Robust error handling
4. **testing-data-pipelines** - Testing approach

**Rationale:** These 4 skills provide foundation for building any data pipeline.

### Phase 2: Operational Excellence

5. **data-quality-checks** - Ensure data correctness
6. **incremental-loading** - Efficient updates
7. **sql-optimization** - Query performance
8. **cost-optimization-data** - Cost management

**Rationale:** Production-ready systems need quality, performance, and cost controls.

### Phase 3: Advanced Patterns

9. **airflow-dags** - Tool-specific patterns (if using Airflow)
10. **data-warehousing** - Schema modeling (if building warehouse)
11. **streaming-processing** - Real-time patterns (if needed)
12. **data-lineage-tracking** - Metadata and impact analysis

**Rationale:** Advanced skills for specific use cases or mature organizations.

## Testing Strategy (Following writing-skills Methodology)

### RED Phase - Baseline Testing

For each skill, run pressure scenarios WITHOUT the skill:

**Example - pipeline-orchestration skill:**
1. Ask agent to design a pipeline with complex dependencies
2. Observe: Do they create DAG with circular dependencies?
3. Observe: Do they handle idempotency?
4. Document exact failures

**Example - error-handling-pipelines skill:**
1. Ask agent to implement retry logic
2. Apply pressure: "This is urgent, just get it working"
3. Observe: Do they skip exponential backoff?
4. Observe: Do they forget jitter?
5. Document rationalizations used

### GREEN Phase - Minimal Skill

Write skill addressing specific failures from RED phase.

### REFACTOR Phase - Close Loopholes

Agent finds workaround? Add explicit counter. Re-test.

**Required for each skill:**
- [ ] 3+ pressure scenarios documented
- [ ] Baseline behavior captured (verbatim rationalizations)
- [ ] Skill addresses specific failures
- [ ] Re-tested with skill present
- [ ] Loopholes identified and closed

## Integration with Elspeth-Simple

### Direct Application Areas

1. **Pipeline patterns apply to SDA orchestration:**
   - StandardOrchestrator ↔ Sequential DAG patterns
   - ExperimentalOrchestrator ↔ Parallel execution patterns
   - Suite execution ↔ DAG of DAGs

2. **Error handling mirrors elspeth patterns:**
   - retry_config ↔ Retry with exponential backoff
   - CheckpointManager ↔ High-water mark patterns
   - EarlyStopCoordinator ↔ Circuit breaker patterns

3. **Data quality aligns with transform plugins:**
   - Quality checks ↔ Transform validation plugins
   - Metrics tracking ↔ Metrics plugins

4. **Testing patterns apply to plugin testing:**
   - Unit tests ↔ Plugin unit tests
   - Integration tests ↔ Full SDA cycle tests
   - Fixtures ↔ pytest fixtures in tests/

### Extension Opportunities

Could extend elspeth with concepts from skill pack:

1. **Streaming datasource plugin** (from streaming-processing)
2. **OpenLineage integration** (from data-lineage-tracking)
3. **Cost-based early stopping** (from cost-optimization-data)
4. **Data quality transform plugins** (from data-quality-checks)

## Success Metrics

Track skill pack effectiveness:

1. **Discovery rate:** Are skills being loaded when relevant?
2. **Compliance rate:** Do agents follow patterns under pressure?
3. **Error reduction:** Fewer pipeline failures after using skills?
4. **Time savings:** Faster implementation with skills vs without?
5. **Quality improvement:** Better data quality with quality skills?

## Next Steps

1. **Review and refine this plan** with stakeholders
2. **Prioritize first 4 skills** (Phase 1: Foundation)
3. **Create baseline test scenarios** for each skill (RED phase)
4. **Write first skill** following writing-skills methodology
5. **Test with subagents** before considering it "done"
6. **Iterate** based on real usage

---

**Document Version:** 1.0
**Created:** 2025-11-14
**Author:** Claude (following writing-skills skill methodology)
**Status:** Planning - awaiting review
