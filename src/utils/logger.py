import logging
import os

def get_logger(name: str):
  logger = logging.getLogger(name)

  if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Prevent the logger from propagating to the root logger
    logger.propagate = False

    # Check if the logger already has handlers, if so, clear them
    if logger.hasHandlers():
      logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(f"logs/{name}.log")

    # Create console handler
    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

  return logger
