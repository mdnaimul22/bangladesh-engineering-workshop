import os
import sys

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from src.config import Settings, setup_logger, exists, delete
from src.helpers.semantic import SemanticSearch

logger = setup_logger(Settings.LOG_DIR / "services.log", name="bew.services.search.trainer")

def rebuild_search_index() -> bool:
    """Rebuild search TF-IDF index and model artifacts."""
    logger.info("====================================")
    logger.info("  REBUILDING SEARCH INDEX & MODEL  ")
    logger.info("====================================")

    # 1. Clean up old artifacts
    artifacts = [
        f"{Settings.models_dir_rel}/tfidf_vectorizer.pkl",
        f"{Settings.models_dir_rel}/tfidf_matrix.pkl",
        f"{Settings.models_dir_rel}/shop_ids.pkl"
    ]

    logger.info("Scanning for old artifacts...")
    for rel_path in artifacts:
        if exists(rel_path):
            delete(rel_path)
            logger.info(f"Deleted old: {rel_path.split('/')[-1]}")
        else:
            logger.info(f"Not found (clean): {rel_path.split('/')[-1]}")

    logger.info("------------------------------")
    logger.info("Retraining Model...")

    # 2. Rebuild Index
    try:
        ss = SemanticSearch()
        db_rel_path = Settings.DATABASE_NAME
        
        if not exists(db_rel_path):
            logger.error(f"ERROR: Database not found at {db_rel_path}")
            return False
            
        ss.build_index()
        logger.info("SUCCESS: Search Index Rebuilt Successfully!")
        logger.info(f"Artifacts saved in: {Settings.MODELS_DIR}")
        return True
        
    except Exception as e:
        logger.error(f"Rebuild FAILED: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = rebuild_search_index()
    if not success:
        sys.exit(1)
