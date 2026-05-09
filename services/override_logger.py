import os
import json
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)

LOG_FILE = "override_log.json"

def log_override(candidate_name: str, dimension: str, original_score: int, new_score: int, reason: str, original_rec: str, new_rec: str):
    """Appends an HR override event to the JSON log file."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "candidate_name": candidate_name,
        "dimension": dimension,
        "original_score": original_score,
        "new_score": new_score,
        "reason": reason,
        "original_recommendation": original_rec,
        "new_recommendation": new_rec
    }
    
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read override log: {e}")
            
    data.append(entry)
    
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Logged override for {candidate_name} on {dimension}.")
    except Exception as e:
        logger.error(f"Failed to write override log: {e}")

def get_override_log() -> list:
    """Returns the list of all logged overrides."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read override log: {e}")
    return []
