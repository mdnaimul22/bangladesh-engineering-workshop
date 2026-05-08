import sqlite3
import pandas as pd
from src.config import Settings, PROJECT_ROOT, ensure_dir, setup_logger, exists, read_pickle, write_pickle
from .engine import tokenize, custom_tokenizer, DOMAIN_MAP

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = setup_logger(Settings.LOG_DIR / "helpers.log", name="bew.helpers.semantic")


class SemanticSearch:
    def __init__(self, vectorizer_path=None, matrix_path=None, shop_ids_path=None):
        self.vectorizer_path = vectorizer_path or str(Settings.MODELS_DIR / "tfidf_vectorizer.pkl")
        self.matrix_path = matrix_path or str(Settings.MODELS_DIR / "tfidf_matrix.pkl")
        self.shop_ids_path = shop_ids_path or str(Settings.MODELS_DIR / "shop_ids.pkl")

        self.vectorizer = None
        self.tfidf_matrix = None
        self.shop_ids = None

    def get_data_from_db(self, db_path=None):
        db_path = db_path or str(PROJECT_ROOT / Settings.DATABASE_NAME)
        conn = sqlite3.connect(db_path)
        query = """
            SELECT 
                s.id as shop_id,
                s.name as shop_name, 
                s.products as shop_products,
                GROUP_CONCAT(t.name, ' ') as tag_names,
                GROUP_CONCAT(t.name_bn, ' ') as tag_names_bn
            FROM shops s
            LEFT JOIN shop_tags st ON s.id = st.shop_id
            LEFT JOIN tags t ON st.tag_id = t.id
            GROUP BY s.id
        """
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error reading from DB: {e}")
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

    def prepare_data(self, df):
        df['text'] = (
            df['shop_name'].fillna('') + " " +
            df['shop_products'].fillna('') + " " +
            df['tag_names'].fillna('') + " " +
            df['tag_names_bn'].fillna('')
        )
        df = df[df['text'].str.strip() != ""]
        return df

    def build_index(self, db_path=None):
        db_path = db_path or str(PROJECT_ROOT / Settings.DATABASE_NAME)
        logger.info(f"Fetching data from live database ({db_path}) for semantic index...")
        df = self.get_data_from_db(db_path)

        if df.empty:
            logger.warning("No data found to build index.")
            return

        df_clean = self.prepare_data(df)
        X_text = df_clean['text'].tolist()
        self.shop_ids = df_clean['shop_id'].tolist()

        logger.info(f"Indexing {len(X_text)} shops...")

        self.vectorizer = TfidfVectorizer(
            tokenizer=custom_tokenizer,
            token_pattern=None,
            ngram_range=(1, 1),
            max_features=10000
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(X_text)

        logger.info("Indexing complete.")
        self.save()

    def search(self, query, top_k=20):
        """Returns list of dicts: {'shop_id': id, 'score': similarity_score}"""
        if self.tfidf_matrix is None or self.vectorizer is None or self.shop_ids is None:
            self.load()
            if self.tfidf_matrix is None:
                return []

        query_vec = self.vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        related_docs_indices = cosine_similarities.argsort()[:-top_k:-1]

        results = []
        for idx in related_docs_indices:
            score = cosine_similarities[idx]
            if score > 0.001:
                results.append({
                    "shop_id": self.shop_ids[idx],
                    "score": round(float(score), 4)
                })

        return results

    def save(self):
        ensure_dir(Settings.MODELS_DIR)

        write_pickle(self.vectorizer, self.vectorizer_path)
        write_pickle(self.tfidf_matrix, self.matrix_path)
        write_pickle(self.shop_ids, self.shop_ids_path)
        logger.info(f"Semantic Search Index saved to {Settings.MODELS_DIR}")

    def load(self):
        try:
            self.vectorizer = read_pickle(self.vectorizer_path)
            self.tfidf_matrix = read_pickle(self.matrix_path)
            self.shop_ids = read_pickle(self.shop_ids_path)
        except Exception:
            pass


if __name__ == "__main__":
    ss = SemanticSearch()
    ss.build_index()
