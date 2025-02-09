# Metrics and performance tracking

import logging
from typing import Dict, Any

class PerformanceMonitor:
    """
    Tracks metrics and performance of the trading agent.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = {}

    def record_metric(self, name: str, value: Any) -> None:
        """
        Record a performance metric.
        """
        self.logger.info(f"Recording metric '{name}': {value}")
        self.metrics[name] = value

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retrieve recorded metrics.
        """
        return self.metrics