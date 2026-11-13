import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

#Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

#store logs in the project root/logs directory
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True,exist_ok=True)

LOG_FILE = LOG_DIR/ "app.log"

def configure_logging():
    formatter= logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )
    
    #console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    #File Handler with automatic rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024 , #5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    #Application Logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    #Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger

logger = logging.getLogger("app")


