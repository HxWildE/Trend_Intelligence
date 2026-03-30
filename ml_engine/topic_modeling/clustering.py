from sklearn.cluster import KMeans

class ClusterModel:

    def __init__(self, n_clusters=5):
        self.max_clusters = n_clusters

    def fit(self, embeddings):
        n = len(embeddings)

        if n == 0:
            return []

        if n == 1:
            return [0]

        # 🔥 dynamic cluster count
        k = min(self.max_clusters, n)

        model = KMeans(n_clusters=k, random_state=42)
        labels = model.fit_predict(embeddings)

        return labels