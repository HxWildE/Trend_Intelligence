import pandas as pd
from sqlalchemy import create_engine, text
from pymongo import MongoClient, UpdateOne
import os
import sys

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

class DataLoader:
    def __init__(self):
        self.pg_url = config.SQLALCHEMY_DATABASE_URI
        self.mongo_url = config.MONGO_URI
        self.mongo_db_name = config.MONGO_DB_NAME

    def load_to_postgres(self, df, table_name):
        """Upserts a pandas DataFrame into a Postgres table using a temp table."""
        try:
            engine = create_engine(self.pg_url)
            temp_table = f"temp_{table_name}"

            # 1. Load data to a temporary table
            df.to_sql(temp_table, engine, if_exists='replace', index=False)
            
            # 2. Execute Upsert: Insert new rows, or update 'ups' and 'num_comments' on conflict
            # This matches the 'post_id' UNIQUE constraint in your schema
            upsert_query = f"""
                INSERT INTO {table_name} (post_id, title, content, ups, num_comments, subreddit, created_utc)
                SELECT post_id, title, content, ups, num_comments, subreddit, created_utc
                FROM {temp_table}
                ON CONFLICT (post_id) DO UPDATE SET
                    ups = EXCLUDED.ups,
                    num_comments = EXCLUDED.num_comments,
                    content = EXCLUDED.content,
                    processed_at = CURRENT_TIMESTAMP;
            """
            
            with engine.connect() as conn:
                conn.execute(text(upsert_query))
                conn.execute(text(f"DROP TABLE {temp_table}"))
                conn.commit()
                
            print(f"[SUCCESS] Postgres '{table_name}': Upserted {len(df)} rows.")
        except Exception as e:
            print(f"[ERROR] Postgres Load Error: {e}")

    def load_to_mongodb(self, df, collection_name):
        """Upserts a pandas DataFrame as JSON documents into MongoDB."""
        try:
            with MongoClient(self.mongo_url) as client:
                db = client[self.mongo_db_name]
                collection = db[collection_name]
                
                data_dict = df.to_dict(orient='records')
                
                if data_dict:
                    # Using bulk_write for efficiency and upsert to avoid duplicates in Mongo
                    operations = [
                        UpdateOne({'post_id': row.get('post_id')}, {'$set': row}, upsert=True)
                        for row in data_dict
                    ]
                    result = collection.bulk_write(operations)
                    print(f"[SUCCESS] MongoDB '{collection_name}': {result.upserted_count} new, {result.modified_count} updated.")
                else:
                    print("[WARNING] No data found for MongoDB.")
        except Exception as e:
            print(f"[ERROR] MongoDB Load Error: {e}")

if __name__ == "__main__":
    loader = DataLoader()
    data_file = config.CLEAN_DATA_PATH # Ensure this is 'reddit_data.csv' or your cleaned file
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)

        # Select only the columns we actually need to avoid duplication collisions when renaming
        pg_df = df.copy()
        
        # Drop intra-batch duplicates so PostgreSQL doesn't try to conflict-update the same row twice in one transaction!
        if 'post_id' in pg_df.columns:
            pg_df = pg_df.drop_duplicates(subset=['post_id'], keep='last')
            
        cols_to_keep = ['post_id', 'title_clean', 'text_clean', 'score', 'comments_clean', 'subreddit', 'datetime_utc']
        pg_df = pg_df[[c for c in cols_to_keep if c in pg_df.columns]]
        
        rename_map = {
            'title_clean': 'title',
            'text_clean': 'content',
            'score': 'ups',
            'datetime_utc': 'created_utc'
        }
        pg_df = pg_df.rename(columns=rename_map)
        
        # Convert created_utc to datetime so Pandas enforces a TIMESTAMP column in SQL instead of TEXT
        if 'created_utc' in pg_df.columns:
            pg_df['created_utc'] = pd.to_datetime(pg_df['created_utc'])

        # Calculate num_comments
        if 'comments_clean' in pg_df.columns:
            pg_df['num_comments'] = pg_df['comments_clean'].apply(
                lambda x: 0 if pd.isna(x) or str(x).lower() == 'no comments' else str(x).count(' | ') + 1
            )
            pg_df = pg_df.drop(columns=['comments_clean'])

        # Final Filter: Keep ONLY the columns defined in your Postgres schema
        required_cols = ['post_id', 'title', 'content', 'ups', 'num_comments', 'subreddit', 'created_utc']
        existing_cols = [c for c in required_cols if c in pg_df.columns]
        pg_df = pg_df[existing_cols]
            
        # Execute Loads
        loader.load_to_mongodb(df, "raw_reddit_posts")
        loader.load_to_postgres(pg_df, "reddit_trends")
        
    else:
        print(f"[ERROR] CSV not found at: {data_file}")