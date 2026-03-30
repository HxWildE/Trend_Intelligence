# ML Engine Data Flow Documentation

This document outlines the entire data flow lifecycle of the `ml_engine` pipeline: from how it ingests data, how it processes that data, to what it ultimately outputs.

## 1. Input: From Where and In What Format?

**Source Location:**
Currently, the `ml_engine` does **not automatically** fetch its own data. It expects to be manually instantiated and fed data by an external caller (such as a database loader, a batch script, or a test file like `test.py`).

**Expected Data Format:**
The top-level entryway (e.g., `RegionTrendPipeline.run`) expects raw, unstructured text in a basic Python list, alongside an optional filter criterion (like `target_state`).

```python
# Example Format
texts = [
    "Heavy rain in Chennai causing floods",
    "Huge traffic jam in Bangalore today",
    "IPL match in mumbai stadium"
]
target_state = "tamil nadu"

# Feeding the model
pipeline = RegionTrendPipeline()
results = pipeline.run(texts, target_state)
```

- **`raw_texts`**: `list[str]` - A list of text strings (e.g., Tweets, Reddit post bodies + titles combined).
- **`target_state`**: `str` - A geographical region to filter the trends down to.

---

## 2. Processing Flow: What Happens Inside?

Once the `ml_engine` receives the list of strings, the data undergoes several sequential transformations:

1. **Region Detection (`RegionService`)**: 
   - Uses **SpaCy Named Entity Recognition** (`en_core_web_sm`) to scan each text for locations, cities, or states.
   - Standardizes slang (e.g., converts "blr" to "bangalore" and then to "karnataka").
   - Filters out any strings that do not belong to the requested `target_state`.
2. **Text Preprocessing (`PreprocessingPipeline`)**: 
   - Converts the text to lowercase.
   - Clears out URLs, punctuation, and non-alphabetical symbols.
3. **Sentiment Analysis (`SentimentInference`)**: 
   - Uses **NLTK Vader** to score the emotional tone of every single text string individually (Negative to Positive).
4. **Sentence Embeddings (`EmbeddingModel`)**: 
   - Converts the cleaned text strings into mathematical floating-point vectors using the `sentence-transformers/all-MiniLM-L6-v2` AI model.
5. **Topic Clustering (`ClusterModel`)**: 
   - Groups mathematically similar sentence vectors together using **KMeans clustering**, essentially finding the hidden "Topics" among thousands of posts.
6. **Topic Labeling (`TopicLabeler`)**: 
   - Uses **TF-IDF** (Term Frequency-Inverse Document Frequency) to extract the 5 most defining words (keywords) for each clustered topic.
7. **Trend Scoring (`TrendScorer`)**: 
   - Calculates the **Volume** (how many posts are in the cluster), **Velocity** (growth rate), **Acceleration**, and applies the average **Sentiment**.
   - Spits out a final consolidated `"score"`.

---

## 3. Output: To Where and In What Format?

**Destination:**
The data is returned directly back to the script that initially called `pipeline.run()`. (It does not automatically save to a database; your `data_pipeline/loaders/db_loader.py` or FastAPI backend must take this output and commit it to SQL).

**Output Data Format:**
It outputs a sorted Python generic `list` containing `dict` objects. Each dictionary represents a single "Trend" or "Topic", automatically sorted by the highest `score`.

```json
[
  {
    "topic_id": 0,
    "keywords": ["chennai", "heavy", "floods", "rain"],
    "volume": 120,
    "velocity": 5.4,
    "acceleration": 1.2,
    "sentiment": -0.85,
    "score": 85.4
  },
  {
    "topic_id": 1,
    "keywords": ["bangalore", "traffic", "jam", "today"],
    "volume": 80,
    "velocity": 2.1,
    "acceleration": 0.5,
    "sentiment": -0.30,
    "score": 62.1
  }
]
```

### Breakdown of the Output Fields:
- **`topic_id`** (`int`): The integer group ID created by KMeans clustering.
- **`keywords`** (`list[str]`): The top 5 defining words describing this exact trend.
- **`volume`** (`int`): The total number of posts that talked about this topic in the current batch.
- **`velocity`** (`float`): The rate at which mentions are increasing compared to a previous batch.
- **`acceleration`** (`float`): The rate at which the velocity is changing (momentum).
- **`sentiment`** (`float`): The average emotional score of all posts in this topic (negative to positive ratio).
- **`score`** (`float`): The master score used to sort the trends from most important to least important.
