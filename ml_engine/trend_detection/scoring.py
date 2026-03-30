class TrendScorer:

    def compute_score(
        self,
        volume: int,
        velocity: float,
        acceleration: float,
        sentiment: float
    ) -> float:
        """
        Combines all signals into a trend score
        """

        # Normalize (basic scaling)
        volume_score = volume
        velocity_score = velocity
        acceleration_score = acceleration
        sentiment_score = sentiment * 10   # amplify sentiment

        score = (
            0.35 * volume_score +
            0.30 * velocity_score +
            0.20 * acceleration_score +
            0.15 * sentiment_score
        )

        return score
    
#  Reason of weights:    
# Volume	baseline popularity
# Velocity	trending speed 🔥
# Acceleration	hype growth 🚀
# Sentiment	positive/negative signal