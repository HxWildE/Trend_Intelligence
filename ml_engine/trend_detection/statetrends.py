from collections import Counter
class StateTrendAggregator:

    def __init__(self):
        pass

    def aggregate(self, posts, target_state):

        # filter posts for that state
        state_posts = [
            post for post in posts
            if target_state in post["regions"]
        ]

        if not state_posts:
            return {
                "state": target_state,
                "top_trends": []
            }

        # count topics
        topic_counter = Counter()

        for post in state_posts:
            for topic in post["topics"]:
                topic_counter[topic] += 1

        # top 10
        top = topic_counter.most_common(10)

        return {
            "state": target_state,
            "top_trends": [
                {"topic": t, "score": c}
                for t, c in top
            ]
        }