class AccelerationCalculator:

    def compute(self, prev_velocity: float, current_velocity: float) -> float:
        """
        prev_velocity: velocity in previous window
        current_velocity: current velocity
        """
        return current_velocity - prev_velocity