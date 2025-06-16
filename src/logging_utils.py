import logging
from typing import Any, Dict, Optional
from datetime import datetime
import json
import os

class GraphLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"graph_generation_{timestamp}.log")
        
        # Configure logging
        self.logger = logging.getLogger("GraphGenerator")
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

    def log_ticket_processing(self, ticket_id: str, nodes_count: int, 
                            edges_count: int) -> None:
        """Log information about processed ticket tree"""
        self.logger.info(
            f"Processed ticket {ticket_id}: {nodes_count} nodes, {edges_count} edges"
        )

    def log_connection(self, from_id: str, to_id: str, 
                      connection_type: str, metadata: Optional[Dict] = None) -> None:
        """Log information about detected connections"""
        msg = f"Found {connection_type} connection: {from_id} -> {to_id}"
        if metadata:
            msg += f" (metadata: {json.dumps(metadata)})"
        self.logger.info(msg)

    def log_similarity(self, ticket1_id: str, ticket2_id: str, 
                      score: float) -> None:
        """Log similarity calculation results"""
        self.logger.debug(
            f"Similarity between {ticket1_id} and {ticket2_id}: {score:.4f}"
        )

    def log_error(self, context: str, error: Exception, 
                  data: Optional[Dict[str, Any]] = None) -> None:
        """Log error information with context"""
        msg = f"Error in {context}: {str(error)}"
        if data:
            msg += f"\nContext data: {json.dumps(data, default=str)}"
        self.logger.error(msg)