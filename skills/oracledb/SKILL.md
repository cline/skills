---
name: oracledb
description: Use these skills to manage and monitor Oracle databases by executing SQL statements, exploring schema metadata, analyzing query performance, monitoring active sessions and resource consumption, and managing storage and object health.
---

## Usage

All scripts can be executed using Node.js. Replace `<param_name>` and `<param_value>` with actual values.

**Bash:**
`node <skill_dir>/scripts/<script_name>.js '{"<param_name>": "<param_value>"}'`

**PowerShell:**
`node <skill_dir>/scripts/<script_name>.js '{\"<param_name>\": \"<param_value>\"}'`

Note: The scripts automatically load the environment variables from various .env files. Do not ask the user to set vars unless skill executions fails due to env var absence.


## Scripts


### execute_sql

Executes any SQL statement.

#### Parameters

| Name | Type | Description | Required | Default |
| :--- | :--- | :--- | :--- | :--- |
| sql | string | The SQL to execute. | Yes |  |


---

### get_query_plan

Generate a full execution plan for a single SQL statement using EXPLAIN PLAN. This can be used to analyze query performance without execution. Requires the SQL statement as input as a parameter.

#### Parameters

| Name | Type | Description | Required | Default |
| :--- | :--- | :--- | :--- | :--- |
| query | string | The SQL statement for which you want to generate plan (omit the EXPLAIN keyword). | Yes |  |


---

### list_active_sessions

List the top N (default 50) currently running database sessions (STATUS='ACTIVE'), showing SID, OS User, Program, and the current SQL statement text.



---

### list_invalid_objects

Lists all database objects that are in an invalid state, requiring recompilation (e.g., procedures, functions, views).



---

### list_tables

Lists all user tables in the connected schema, including segment size, row count, and last analyzed date. Filters by a comma-separated list of names. If names are omitted, lists all tables in the current user's schema.



---

### list_tablespace_usage

List tablespace names, total size, free space, and used percentage to monitor storage utilization.



---

### list_top_sql_by_resource

List the top N (default 5) SQL statements from the library cache based on a chosen resource metric (CPU, I/O, or Elapsed Time). Shows SQL ID, execution count, buffer gets, disk reads, CPU time, and elapsed time.



---

