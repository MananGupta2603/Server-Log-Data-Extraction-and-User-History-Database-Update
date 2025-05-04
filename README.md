# Server Log Data Extraction and User History Database Update

## Project Overview

This ETL (Extract, Transform, Load) pipeline automates the processing of server email logs (`.mbox` files), storing clean and structured data in both MongoDB Atlas and a local SQLite database. It provides a simple CLI for running ad-hoc SQL queries and viewing insights.

## Objectives

* **Automate Extraction**: Parse `.mbox` log files to extract email addresses and timestamps.
* **Clean & Standardize**: Normalize dates to `YYYY-MM-DD HH:MM:SS` format and validate email entries.
* **Config-Driven Pipeline**: Use `config.ini` for file paths, database URIs, and collection/table names.
* **Dual-Stage Storage**:

  * MongoDB Atlas for scalable, schemaless staging.
  * SQLite for lightweight local analysis.
* **Interactive Analysis**: Menu-driven CLI to run key queries (unique emails, volume by day, domain counts, etc.).

## Technology Stack

* **Python 3.8+**
* **MongoDB Atlas** (NoSQL)
* **SQLite** (Relational)
* Libraries: `pymongo`, `sqlite3`, `dateutil`, `configparser`, `re`

## Repository Structure

```
├── config.ini          # Config file for paths & URIs
├── main.py             # Core ETL and CLI script
├── mbox.txt            # Sample email log data
├── user_history.db     # SQLite database (generated)
├── README.md           # Project documentation
```

## Prerequisites

* Python 3.8 or higher installed and on PATH
* A running MongoDB Atlas cluster (or local mongod at `localhost:27017`)
* Network access (whitelisted IP) to your Atlas cluster


### Available Queries

1. Unique Emails
2. Emails Per Day
3. First and Last Dates per Email
4. Count by Domain
5. Exit


## Exploring the SQLite DB

* **Using Python**: `python -m sqlite3 user_history.db`
* **In CLI**:

  ```sql
  .tables
  .schema user_history
  SELECT * FROM user_history LIMIT 5;
  ```



