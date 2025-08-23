"""
@description: This is the main entry point for the smart home system.
@author: Nicola Guerra
"""

import os

from dotenv import load_dotenv

from logger.factory import get_logger, init_logging

load_dotenv(dotenv_path=os.getenv("PYTHON_APP", ".development.env"), override=True)


def main():
    init_logging()
    logger = get_logger(__name__)
    logger.error("test")
    logger.info("test")
    logger.debug("test")
    logger.warning("test")
    logger.critical("test")
    # Initialize and start the smart home system components here


if __name__ == "__main__":
    main()
