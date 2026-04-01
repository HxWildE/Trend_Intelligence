from sklearn.cluster import KMeans, AgglomerativeClustering
import numpy as np

class ClusterModel:

    def __init__(self, distance_threshold=1.25): 
        # 1.25 is a tight threshold for normalized embeddings (0-2 range where ~0.5 is very close)
        # This forces the algorithm to generate tightly-knit, highly specific topics
        # instead of throwing vaguely related things into a huge bucket.
        self.distance_threshold = distance_threshold

    def fit(self, embeddings):
        n = len(embeddings)

        if n == 0:
            return []
        if n <= 2:
            return [0] * n

        # We set n_clusters=None to activate dynamic semantic clustering.
        # It creates as many topics as needed based on semantic diversity.
        model = AgglomerativeClustering(
            n_clusters=None, 
            distance_threshold=self.distance_threshold,
            metric='euclidean',
            linkage='ward'
        )
        
        try:
            labels = model.fit_predict(embeddings)
        except Exception as e:
            # Extreme Edge Cases (e.g. perfectly identical data points blocking variance scaling)
            fallback = KMeans(n_clusters=min(8, n), n_init='auto', random_state=42)
            labels = fallback.fit_predict(embeddings)

        return labels.tolist()