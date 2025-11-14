# Available Data Engineering Skills (Descriptions Only)

These are the 12 available skills in the axiom-data-engineering pack:

1. **pipeline-orchestration**: Use when designing multi-step data workflows, coordinating dependencies between tasks, or deciding between orchestration tools (Airflow, Prefect, Dagster) - provides patterns for DAG design, task dependencies, idempotency, and failure recovery

2. **etl-patterns**: Use when extracting data from sources, transforming data structures, or loading into destinations - covers ELT vs ETL tradeoffs, incremental vs full loads, slowly changing dimensions (SCD), data deduplication, and schema evolution handling

3. **airflow-dags**: Use when writing Apache Airflow DAGs, debugging task failures, handling XComs, or managing connections and variables - provides DAG authoring best practices, common operators, testing patterns, and troubleshooting workflows

4. **sql-optimization**: Use when queries are slow, databases are resource-constrained, or analyzing query execution plans - covers indexing strategies, query rewriting, partitioning, statistics, and warehouse-specific optimizations (BigQuery, Snowflake, Redshift)

5. **data-warehousing**: Use when designing warehouse schemas, choosing modeling approaches (Kimball vs Inmon), implementing star/snowflake schemas, or planning fact/dimension tables - covers dimensional modeling, data vault, slowly changing dimensions, and analytical query patterns

6. **streaming-processing**: Use when processing real-time event streams, choosing streaming frameworks (Kafka, Kinesis, Flink, Spark Streaming), handling late-arriving data, or implementing windowing operations - covers stream vs batch tradeoffs, exactly-once semantics, and backpressure handling

7. **data-quality-checks**: Use when implementing data validation, detecting data anomalies, setting up quality gates, or defining SLAs for data freshness and completeness - covers Great Expectations, Soda, dbt tests, custom validation frameworks, and alerting strategies

8. **incremental-loading**: Use when loading only new/changed data instead of full refreshes, implementing CDC (Change Data Capture), tracking high-water marks, or handling deletions in source systems - covers timestamp-based, log-based CDC, and merge strategies for efficient incremental updates

9. **error-handling-pipelines**: Use when pipelines fail unexpectedly, implementing retry logic with exponential backoff, designing dead letter queues, or ensuring data consistency during failures - covers transactional patterns, compensating transactions, circuit breakers, and alert escalation

10. **cost-optimization-data**: Use when cloud data warehouse costs are high, optimizing query performance for cost reduction, choosing between compute/storage tradeoffs, or implementing budget alerts - covers BigQuery, Snowflake, Redshift cost models, query optimization for cost, partitioning/clustering strategies, and resource monitoring

11. **data-lineage-tracking**: Use when tracking data origins, understanding downstream impacts of changes, implementing compliance requirements (GDPR, CCPA), or debugging data quality issues - covers lineage tools (OpenLineage, DataHub, Marquez), column-level lineage, impact analysis, and metadata management

12. **testing-data-pipelines**: Use when writing tests for data pipelines, validating transformations, mocking external dependencies, or setting up CI/CD for data workflows - covers unit tests for transformations, integration tests for pipelines, data quality tests, and test data generation strategies
