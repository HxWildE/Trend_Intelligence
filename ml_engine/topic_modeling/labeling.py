from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS) + [
    "wants", "knows", "says", "did", "does", "doing", "just", "like", 
    "make", "get", "got", "good", "bad", "new", "really", "want",
    "need", "think", "people", "time", "day", "way", "going", "know"
]

class TopicLabeler:

    def get_topic_labels(self, texts, labels):
        cluster_map = {}

        for i, label in enumerate(labels):
            cluster_map.setdefault(label, []).append(texts[i])

        topic_labels = {}

        for label, docs in cluster_map.items():
            # Extract single, double, and triple-word phrases for richer human context.
            vectorizer = TfidfVectorizer(
                stop_words=CUSTOM_STOP_WORDS, 
                ngram_range=(1, 3), 
                max_df=0.9,
                min_df=1
            )
            
            try:
                X = vectorizer.fit_transform(docs)
                scores = X.sum(axis=0).A1
                words = vectorizer.get_feature_names_out()

                # Rank by TF-IDF score
                ranked = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)
                
                # Filter out numbers and highly generic stopwords 
                # (Scikit learn sometimes misses structural English noise)
                filtered_labels = []
                for word, score in ranked:
                    if word.isdigit() or len(word) < 3:
                        continue
                        
                    # Stop grouping if the phrase is mostly composed of numbers "10 500"
                    if any(c.isdigit() for c in word):
                        # only include if it feels like tech (e.g. "ps5", "chatgpt 4")
                        if not any(c.isalpha() for c in word):
                            continue

                    filtered_labels.append(word)
                    
                    if len(filtered_labels) >= 5:
                        break
                        
                topic_labels[label] = filtered_labels if filtered_labels else [w for w, _ in ranked[:5]]
            except Exception:
                topic_labels[label] = ["Emerging Trend"]

        return topic_labels