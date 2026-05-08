import os
import sys

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.config import Settings, PROJECT_ROOT
from .semantic import SemanticSearch

print("====================================")
print("  REBUILDING SEARCH INDEX & MODEL  ")
print("====================================")

# 1. Clean up old artifacts
artifacts = [
    str(Settings.MODELS_DIR / 'tfidf_vectorizer.pkl'),
    str(Settings.MODELS_DIR / 'tfidf_matrix.pkl'),
    str(Settings.MODELS_DIR / 'shop_ids.pkl')
]

print("Scanning for old artifacts...")
for file_path in artifacts:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted old: {os.path.basename(file_path)}")
    else:
        print(f"Not found (clean): {os.path.basename(file_path)}")

print("\n------------------------------")
print("Retraining Model...")

# 2. Rebuild Index
try:
    ss = SemanticSearch()
    db_path = str(PROJECT_ROOT / Settings.DATABASE_NAME)
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        exit(1)
        
    ss.build_index(db_path)
    print("\nSUCCESS: Search Index Rebuilt Successfully!")
    print(f"Artifacts saved in: {Settings.MODELS_DIR}")
    
except Exception as e:
    print(f"\nFAILED: {e}")
    import traceback
    traceback.print_exc()
