class VelocityCalculator:

    def compute(self, prev_count: int, current_count: int) -> float:
        """
        prev_count: mentions in previous time window
        current_count: mentions now
        """
        return current_count - prev_count