# DB Loader Troubleshooting Guide

This document explains the root causes of the errors encountered in the `db_loader.py` script and how they were resolved. 

## Issue 1: Terminal Encoding Error (UnicodeEncodeError)

**The Problem**  
When running the `db_loader.py` file, we encountered the following error midway through the execution:  
`UnicodeEncodeError: 'charmap' codec can't encode character...`  

This happened because the script was using emojis (`✅`, `❌`, `⚠️`) in the `print()` statements to indicate success or failure. The default Windows Command Prompt text encoding (`cp1252`) is not capable of correctly rendering these Unicode characters. As a result, the script crashed immediately after successfully loading data to MongoDB, thereby entirely skipping the PostgreSQL loading process.

**The Solution**  
We updated `db_loader.py` to replace all unsupported emojis with standard plain-text equivalents like `[SUCCESS]`, `[ERROR]`, `[WARNING]`, and `[INFO]`. This makes the console output universally compatible with all terminals and prevents character mapping crashes.

## Issue 2: PostgreSQL Table Schema Mismatch 

**The Problem**  
After resolving the print statement errors, the script reached the PostgreSQL logic but threw a database error:  
`UndefinedColumn: column "comments" of relation "reddit_trends" does not exist`  

This occurred because the DataFrames generated from the CSV file did not exactly match the strict column requirements defined in `database/postgres/schema.sql`.
Specifically:
1. The CSV contained a string column `datetime_utc`, but the Postgres schema expected a timestamp column named `created_utc`.
2. The CSV contained a `comments` column containing long blocks of joined text. However, the Postgres database only expected a single integer representing `num_comments`.

**The Solution**  
We added a small data processing block right before the PostgreSQL insertion inside `db_loader.py`:
1. Renamed `datetime_utc` to `created_utc`.
2. Automatically calculated `num_comments` by counting the split delimiter (` | `) within the text-based `comments` string to generate the expected integer count.
3. Dropped the raw text `comments` column so the DataFrame matched the destination table perfectly.

No changes were made to the MongoDB insertion logic since MongoDB relies on a schema-less design where raw text comments are perfectly acceptable.
