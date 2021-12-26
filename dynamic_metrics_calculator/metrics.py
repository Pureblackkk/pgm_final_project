from .user_metrics import UserMetricsCalculator
from .relation_metrics import RelationMetricsCalculator

class MetricsCalculator(UserMetricsCalculator, RelationMetricsCalculator):
    def __init__(self, databaseDirectory) -> None:
        super().__init__(databaseDirectory)