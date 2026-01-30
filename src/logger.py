import logging
from datetime import datetime

def setup_logger():
    logging.basicConfig(
        filename=f"logs/run_{datetime.now().strftime('%Y-%m-%d')}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
