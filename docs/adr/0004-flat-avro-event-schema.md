# ADR 0004: One flat Avro schema for all app events

## Status
Accepted

## Context
Four event types share an envelope and differ in a few fields. Avro has no inheritance,
and Kafka Schema Registry works most simply with one schema per topic.

## Decision
Use a single AppEvent schema on one topic. Type-specific fields are optional (nullable
with a null default). Rules like "donation_completed needs payment_id" are enforced in
code and later in dbt tests.

## Consequences
Simple topic and schema management, and adding a field with a default stays backward
compatible. The cost is sparse nullable columns and validation rules outside Avro.
