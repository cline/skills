---
name: cosmosdb-best-practices
license: MIT
description: |
  Azure Cosmos DB performance optimization and best practices guidelines for NoSQL,
  partitioning, queries, SDK usage, and vector search. Use when writing, reviewing,
  or refactoring code that interacts with Azure Cosmos DB, designing data models,
  optimizing queries, or implementing high-performance database operations.
metadata:
  author: cosmosdb-agent-kit
  version: "1.0.0"
---

# Azure Cosmos DB Best Practices

Comprehensive performance optimization guide for Azure Cosmos DB applications, containing
73+ rules across 10 categories, prioritized by impact to guide automated
refactoring and code generation.

73 individual rule files are in the [rules/](./rules/) directory, one file per rule,
synced from the [AzureCosmosDB/cosmosdb-agent-kit](https://github.com/AzureCosmosDB/cosmosdb-agent-kit).
Load only the relevant rule file(s) when answering a question — do NOT load all files at once.

## When to Apply

Reference these guidelines when:
- Designing data models for Cosmos DB
- Choosing partition keys
- Writing or optimizing queries
- Implementing SDK patterns
- Reviewing code for performance issues
- Configuring throughput and scaling
- Building globally distributed applications
- Implementing vector search and RAG patterns

## Rule Index

Rules are grouped by category prefix. For a given question, load files matching
the relevant prefix (e.g., `model-*.md` for data modeling, `sdk-*.md` for SDK usage).
See [rules/_sections.md](rules/_sections.md) for category descriptions.

### 1. Data Modeling — CRITICAL (prefix: `model-`)

- [model-embed-related.md](rules/model-embed-related.md) — Embed related data retrieved together
- [model-reference-large.md](rules/model-reference-large.md) — Reference data when items grow large
- [model-avoid-2mb-limit.md](rules/model-avoid-2mb-limit.md) — Keep items well under 2MB limit
- [model-id-constraints.md](rules/model-id-constraints.md) — Follow ID value length and character constraints
- [model-nesting-depth.md](rules/model-nesting-depth.md) — Stay within 128-level nesting depth limit
- [model-numeric-precision.md](rules/model-numeric-precision.md) — Understand IEEE 754 numeric precision limits
- [model-denormalize-reads.md](rules/model-denormalize-reads.md) — Denormalize for read-heavy workloads
- [model-schema-versioning.md](rules/model-schema-versioning.md) — Version your document schemas
- [model-type-discriminator.md](rules/model-type-discriminator.md) — Use type discriminators for polymorphic data
- [model-json-serialization.md](rules/model-json-serialization.md) — Handle JSON serialization correctly
- [model-relationship-references.md](rules/model-relationship-references.md) — Use ID references with transient hydration

### 2. Partition Key Design — CRITICAL (prefix: `partition-`)

- [partition-high-cardinality.md](rules/partition-high-cardinality.md) — Choose high-cardinality partition keys
- [partition-avoid-hotspots.md](rules/partition-avoid-hotspots.md) — Distribute writes evenly
- [partition-hierarchical.md](rules/partition-hierarchical.md) — Use hierarchical partition keys for flexibility
- [partition-query-patterns.md](rules/partition-query-patterns.md) — Align partition key with query patterns
- [partition-synthetic-keys.md](rules/partition-synthetic-keys.md) — Create synthetic keys when needed
- [partition-key-length.md](rules/partition-key-length.md) — Respect partition key value length limits
- [partition-20gb-limit.md](rules/partition-20gb-limit.md) — Plan for 20GB logical partition limit

### 3. Query Optimization — HIGH (prefix: `query-`)

- [query-avoid-cross-partition.md](rules/query-avoid-cross-partition.md) — Minimize cross-partition queries
- [query-use-projections.md](rules/query-use-projections.md) — Project only needed fields
- [query-pagination.md](rules/query-pagination.md) — Use continuation tokens for pagination
- [query-avoid-scans.md](rules/query-avoid-scans.md) — Avoid full container scans
- [query-parameterize.md](rules/query-parameterize.md) — Use parameterized queries
- [query-order-filters.md](rules/query-order-filters.md) — Order filters by selectivity

### 4. SDK Best Practices — HIGH (prefix: `sdk-`)

- [sdk-singleton-client.md](rules/sdk-singleton-client.md) — Reuse CosmosClient as singleton
- [sdk-async-api.md](rules/sdk-async-api.md) — Use async APIs for throughput
- [sdk-retry-429.md](rules/sdk-retry-429.md) — Handle 429s with retry-after
- [sdk-connection-mode.md](rules/sdk-connection-mode.md) — Use Direct mode for production
- [sdk-preferred-regions.md](rules/sdk-preferred-regions.md) — Configure preferred regions
- [sdk-excluded-regions.md](rules/sdk-excluded-regions.md) — Exclude regions experiencing issues
- [sdk-availability-strategy.md](rules/sdk-availability-strategy.md) — Configure availability strategy for resilience
- [sdk-circuit-breaker.md](rules/sdk-circuit-breaker.md) — Use circuit breaker for fault tolerance
- [sdk-diagnostics.md](rules/sdk-diagnostics.md) — Log diagnostics for troubleshooting
- [sdk-serialization-enums.md](rules/sdk-serialization-enums.md) — Serialize enums as strings not integers
- [sdk-emulator-ssl.md](rules/sdk-emulator-ssl.md) — Configure SSL and connection mode for Cosmos DB Emulator
- [sdk-etag-concurrency.md](rules/sdk-etag-concurrency.md) — Use ETags for optimistic concurrency
- [sdk-java-content-response.md](rules/sdk-java-content-response.md) — Enable content response on write operations (Java)
- [sdk-java-cosmos-config.md](rules/sdk-java-cosmos-config.md) — Configure Cosmos DB in Spring Boot with dependent beans
- [sdk-java-spring-boot-versions.md](rules/sdk-java-spring-boot-versions.md) — Match Java version to Spring Boot requirements
- [sdk-local-dev-config.md](rules/sdk-local-dev-config.md) — Configure local development to avoid cloud conflicts
- [sdk-newtonsoft-dependency.md](rules/sdk-newtonsoft-dependency.md) — Explicitly reference Newtonsoft.Json package (.NET)
- [sdk-spring-data-annotations.md](rules/sdk-spring-data-annotations.md) — Annotate entities for Spring Data Cosmos
- [sdk-spring-data-repository.md](rules/sdk-spring-data-repository.md) — Use CosmosRepository correctly

### 5. Indexing Strategies — MEDIUM-HIGH (prefix: `index-`)

- [index-exclude-unused.md](rules/index-exclude-unused.md) — Exclude paths never queried
- [index-composite.md](rules/index-composite.md) — Use composite indexes for ORDER BY
- [index-spatial.md](rules/index-spatial.md) — Add spatial indexes for geo queries
- [index-range-vs-hash.md](rules/index-range-vs-hash.md) — Choose appropriate index types
- [index-lazy-consistent.md](rules/index-lazy-consistent.md) — Understand indexing modes

### 6. Throughput & Scaling — MEDIUM (prefix: `throughput-`)

- [throughput-autoscale.md](rules/throughput-autoscale.md) — Use autoscale for variable workloads
- [throughput-right-size.md](rules/throughput-right-size.md) — Right-size provisioned throughput
- [throughput-serverless.md](rules/throughput-serverless.md) — Consider serverless for dev/test
- [throughput-burst.md](rules/throughput-burst.md) — Understand burst capacity
- [throughput-container-vs-database.md](rules/throughput-container-vs-database.md) — Choose allocation level wisely

### 7. Global Distribution — MEDIUM (prefix: `global-`)

- [global-multi-region.md](rules/global-multi-region.md) — Configure multi-region writes
- [global-consistency.md](rules/global-consistency.md) — Choose appropriate consistency level
- [global-conflict-resolution.md](rules/global-conflict-resolution.md) — Implement conflict resolution
- [global-failover.md](rules/global-failover.md) — Configure automatic failover
- [global-read-regions.md](rules/global-read-regions.md) — Add read regions near users
- [global-zone-redundancy.md](rules/global-zone-redundancy.md) — Enable zone redundancy for HA

### 8. Monitoring & Diagnostics — LOW-MEDIUM (prefix: `monitoring-`)

- [monitoring-ru-consumption.md](rules/monitoring-ru-consumption.md) — Track RU consumption
- [monitoring-latency.md](rules/monitoring-latency.md) — Monitor P99 latency
- [monitoring-throttling.md](rules/monitoring-throttling.md) — Alert on throttling
- [monitoring-azure-monitor.md](rules/monitoring-azure-monitor.md) — Integrate Azure Monitor
- [monitoring-diagnostic-logs.md](rules/monitoring-diagnostic-logs.md) — Enable diagnostic logging

### 9. Design Patterns — HIGH (prefix: `pattern-`)

- [pattern-change-feed-materialized-views.md](rules/pattern-change-feed-materialized-views.md) — Use Change Feed for materialized views
- [pattern-efficient-ranking.md](rules/pattern-efficient-ranking.md) — Use count-based or cached approaches for ranking
- [pattern-service-layer-relationships.md](rules/pattern-service-layer-relationships.md) — Use a service layer to hydrate document references

### 10. Vector Search — HIGH (prefix: `vector-`)

- [vector-enable-feature.md](rules/vector-enable-feature.md) — Enable vector search feature on account
- [vector-embedding-policy.md](rules/vector-embedding-policy.md) — Define vector embedding policy on container
- [vector-index-type.md](rules/vector-index-type.md) — Configure vector indexes (QuantizedFlat or DiskANN)
- [vector-distance-query.md](rules/vector-distance-query.md) — Use VectorDistance() for similarity search
- [vector-normalize-embeddings.md](rules/vector-normalize-embeddings.md) — Normalize embeddings for cosine similarity
- [vector-repository-pattern.md](rules/vector-repository-pattern.md) — Implement repository pattern for vector search

## How to Use

Each rule is a separate file under [rules/](./rules/). When answering a Cosmos DB question,
read only the relevant rule file(s) based on the prefix matching the topic:

- Data modeling question → read `rules/model-*.md` files
- Partition key question → read `rules/partition-*.md` files
- SDK/client question → read `rules/sdk-*.md` files
- etc.

Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

Source: [AzureCosmosDB/cosmosdb-agent-kit](https://github.com/AzureCosmosDB/cosmosdb-agent-kit/tree/main/skills/cosmosdb-best-practices/rules)
