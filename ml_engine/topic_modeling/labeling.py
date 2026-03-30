from sklearn.feature_extraction.text import TfidfVectorizer

class TopicLabeler:

    def get_topic_labels(self, texts, labels):
        cluster_map = {}

        for i, label in enumerate(labels):
            cluster_map.setdefault(label, []).append(texts[i])

        topic_labels = {}

        for label, docs in cluster_map.items():
            vectorizer = TfidfVectorizer(stop_words='english')
            X = vectorizer.fit_transform(docs)

            scores = X.sum(axis=0).A1
            words = vectorizer.get_feature_names_out()

            ranked = sorted(zip(words, scores), key=lambda x: x[1], reverse=True)

            topic_labels[label] = [word for word, _ in ranked[:5]]

        return topic_labels