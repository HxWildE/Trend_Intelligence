import logging

logging.basicConfig(level=logging.INFO)

def log(msg):
    """
    Logs a message at the INFO level.
    
    Args:
        msg: The message to be logged.
    """
    logging.info(msg)