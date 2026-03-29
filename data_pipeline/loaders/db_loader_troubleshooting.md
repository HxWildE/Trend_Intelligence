# db_loader.py Troubleshooting Guide

If your pipeline (`cron_jobs.py`) is running fine on the surface but your PostgreSQL `reddit_trends` table remains empty (0 rows), it is highly likely that `db_loader.py` is silently failing and catching the error within its `try/except` block.

Below are the most common database silent failures and the solutions that have been applied to `db_loader.py`.

---

## 1. Silent Error: `NameError: name 'pg_df' is not defined`

**Symptoms:** The script prints `[ERROR] Postgres Load Error: name 'pg_df' is not defined`.
**Cause:** During a manual edit or update, the original `DataFrame` copy command (`pg_df = df.copy()`) was accidentally deleted or unassigned before the column renaming process began.
**Solution:** Always ensure that you initialize the Postgres-specific dataset from the raw pandas DataFrame:
```python
# Select only the columns we actually need to avoid duplication collisions when renaming
pg_df = df.copy()
```

---

## 2. Silent Error: `psycopg2.errors.DatatypeMismatch`
*(column "created_utc" is of type timestamp without time zone but expression is of type text)*

**Symptoms:** The CSV raw text data hits the Postgres database, but Postgres refuses to process the UPSERT statement because it expects a formatted date, not a string. 
**Cause:** `to_sql()` natively exports strings as `TEXT` in SQL. When appending to the temporary table, it stored `created_utc` as plain text, leading to a mismatched comparison when `db_loader.py` ran the `ON CONFLICT` query against the permanent `reddit_trends` table.
**Solution:** Explicitly cast the string column into a native Pandas datetime object before sending it to SQL:
```python
# Convert created_utc so Pandas enforces a TIMESTAMP column in SQL instead of TEXT
if 'created_utc' in pg_df.columns:
    pg_df['created_utc'] = pd.to_datetime(pg_df['created_utc'])
```

---

## 3. Silent Error: `psycopg2.errors.CardinalityViolation` 
*(ON CONFLICT DO UPDATE command cannot affect row a second time)*

**Symptoms:** The database connects fine, the data types match perfectly, but 0 rows are inserted.
**Cause:** The UPSERT logic (`ON CONFLICT (post_id) DO UPDATE...`) is rigorously precise. When the scraper (`reddit_collector.py`) searches for multiple keywords ("AI", "Nvidia") AND pulls top posts from Subreddits, a highly popular post can occasionally be scraped *twice* within the exact same hourly batch.
PostgreSQL forbids you from passing two identically Unique IDs inside a single `INSERT` statement, throwing a `CardinalityViolation` and rejecting the entire file.
**Solution:** Scrub the DataFrame for duplicate `post_id` strings and keep only the latest one prior to sending the query to the SQL engine:
```python
# Drop intra-batch duplicates so PostgreSQL doesn't try to conflict-update the same row twice in one transaction!
if 'post_id' in pg_df.columns:
    pg_df = pg_df.drop_duplicates(subset=['post_id'], keep='last')
```
