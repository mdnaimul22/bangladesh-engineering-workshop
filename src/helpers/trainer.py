from src.config import Settings, PROJECT_ROOT, setup_logger, exists, delete
from .semantic import SemanticSearch

logger = setup_logger(Settings.LOG_DIR / "helpers.log", name="bew.services.search.trainer")

def rebuild_index():
    logger.info("====================================")
    logger.info("  REBUILDING SEARCH INDEX & MODEL  ")
    logger.info("====================================")

    # 1. Clean up old artifacts
    artifacts = [
        str(Settings.MODELS_DIR / 'tfidf_vectorizer.pkl'),
        str(Settings.MODELS_DIR / 'tfidf_matrix.pkl'),
        str(Settings.MODELS_DIR / 'shop_ids.pkl')
    ]

    logger.info("Scanning for old artifacts...")
    for file_path in artifacts:
        if exists(file_path):
            delete(file_path)
            logger.info(f"Deleted old artifact: {file_path}")
        else:
            logger.debug(f"Artifact not found (already clean): {file_path}")

    logger.info("------------------------------")
    logger.info("Retraining Model...")

    # 2. Rebuild Index
    try:
        ss = SemanticSearch()
        db_path = str(PROJECT_ROOT / Settings.DATABASE_NAME)
        
        if not exists(db_path):
            logger.error(f"Database not found at {db_path}")
            return False
            
        ss.build_index(db_path)
        logger.info("SUCCESS: Search Index Rebuilt Successfully!")
        logger.info(f"Artifacts saved in: {Settings.MODELS_DIR}")
        return True
        
    except Exception as e:
        logger.error(f"Rebuild FAILED: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    rebuild_index()
