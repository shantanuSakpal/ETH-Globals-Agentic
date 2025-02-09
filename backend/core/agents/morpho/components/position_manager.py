# Position and loop execution

import logging
from typing import Dict, Any

class PositionManager:
    """
    Manages trading positions and state.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.positions = {}

    def open_position(self, position_id: str, details: Dict[str, Any]) -> None:
        """
        Open a new trading position.
        """
        self.logger.info(f"Opening position {position_id}.")
        self.positions[position_id] = details

    def close_position(self, position_id: str) -> None:
        """
        Close an existing trading position.
        """
        if position_id in self.positions:
            self.logger.info(f"Closing position {position_id}.")
            del self.positions[position_id]
        else:
            self.logger.warning(f"Attempted to close non-existent position {position_id}.")

    def get_position(self, position_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a trading position.
        """
        return self.positions.get(position_id, {})