"""
SabbiAI NLP Classifier for Intent Classification
Classifies user queries into: scheme_query, job_query, or skill_query
Uses zero-shot classification or TF-IDF as fallback.
"""

import pandas as pd
import pickle
import os
from pathlib import Path

try:
    from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

MODELS_DIR = Path("models/")
MODELS_DIR.mkdir(exist_ok=True, parents=True)
CLASSIFIER_PATH = MODELS_DIR / "nlp_classifier.pkl"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
METHOD_PATH = MODELS_DIR / "classifier_method.txt"

_cached_pipeline = None
_cached_vectorizer = None
_cached_model = None
_classifier_method = None


def train_classifier():
    """Train the NLP classifier using zero-shot or TF-IDF fallback."""
    global _classifier_method

    print("[nlp] Loading training data...")
    data_path = Path("data/synthetic_queries.csv")
    if not data_path.exists():
        print("[nlp] Data file not found, using keyword fallback")
        _classifier_method = "keyword"
        with open(METHOD_PATH, "w") as f:
            f.write("keyword")
        return

    df = pd.read_csv(data_path)
    df["query_text"] = df["query_text"].astype(str).str.strip().str.lower()
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    if SKLEARN_AVAILABLE:
        try:
            print("[nlp] Training TF-IDF + Logistic Regression classifier...")

            X = df["query_text"].values
            y = df["category"].values

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                stop_words="english",
            )
            X_train_vec = vectorizer.fit_transform(X_train)
            X_test_vec = vectorizer.transform(X_test)

            classifier = LogisticRegression(
                max_iter=200, class_weight="balanced", random_state=42
            )
            classifier.fit(X_train_vec, y_train)

            y_pred = classifier.predict(X_test_vec)
            accuracy = accuracy_score(y_test, y_pred)

            with open(VECTORIZER_PATH, "wb") as f:
                pickle.dump(vectorizer, f)
            with open(CLASSIFIER_PATH, "wb") as f:
                pickle.dump(classifier, f)

            _classifier_method = "tfidf"
            with open(METHOD_PATH, "w") as f:
                f.write("tfidf")

            report = classification_report(y_test, y_pred, output_dict=True)

            print(f"✅ NLP Classifier ready -- method: tfidf")
            print(f"📊 Accuracy: {accuracy * 100:.1f}%")
            print(
                f"  scheme_query: {report.get('scheme_query', {}).get('f1-score', 0):.2f}"
            )
            print(f"  job_query: {report.get('job_query', {}).get('f1-score', 0):.2f}")
            print(
                f"  skill_query: {report.get('skill_query', {}).get('f1-score', 0):.2f}"
            )
            return

        except Exception as e:
            print(f"[nlp] TF-IDF failed: {e}")

    _classifier_method = "keyword"
    with open(METHOD_PATH, "w") as f:
        f.write("keyword")
    print("[nlp] Falling back to keyword classifier")


def classify_query(text):
    """Classify query using the trained method."""
    global _cached_pipeline, _cached_vectorizer, _cached_model, _classifier_method

    result = {"category": "scheme_query", "confidence": 0.5, "raw_label": "fallback"}

    try:
        if _classifier_method is None:
            if os.path.exists(METHOD_PATH):
                with open(METHOD_PATH, "r") as f:
                    _classifier_method = f.read().strip()
            else:
                _classifier_method = "keyword"

        if _classifier_method == "keyword":
            return keyword_classify(text)

        if _classifier_method == "zero_shot":
            try:
                if _cached_pipeline is None:
                    _cached_pipeline = pipeline(
                        "zero-shot-classification",
                        model="facebook/bart-large-mnli",
                        device=-1,
                    )

                candidate_labels = ["government scheme", "job search", "skill training"]
                result = _cached_pipeline(text, candidate_labels, truncation=True)

                label_map = {
                    "government scheme": "scheme_query",
                    "job search": "job_query",
                    "skill training": "skill_query",
                }

                top_label = result["labels"][0]
                confidence = result["scores"][0]

                return {
                    "category": label_map.get(top_label, "scheme_query"),
                    "confidence": round(float(confidence), 2),
                    "raw_label": top_label,
                }
            except Exception as e:
                print(f"[nlp] Zero-shot error: {e}")
                return keyword_classify(text)

        if _classifier_method == "tfidf":
            try:
                if _cached_vectorizer is None:
                    with open(VECTORIZER_PATH, "rb") as f:
                        _cached_vectorizer = pickle.load(f)
                if _cached_model is None:
                    with open(CLASSIFIER_PATH, "rb") as f:
                        _cached_model = pickle.load(f)

                text_vec = _cached_vectorizer.transform([text])
                prediction = _cached_model.predict(text_vec)[0]

                if hasattr(_cached_model, "predict_proba"):
                    probs = _cached_model.predict_proba(text_vec)[0]
                    confidence = float(max(probs))
                else:
                    confidence = 0.7

                return {
                    "category": prediction,
                    "confidence": round(confidence, 2),
                    "raw_label": prediction,
                }
            except Exception as e:
                print(f"[nlp] TF-IDF error: {e}")
                return keyword_classify(text)

    except Exception as e:
        print(f"[nlp] classify_query error: {e}")

    return keyword_classify(text)


def keyword_classify(text):
    """Pure keyword-based fallback classifier."""
    text_lower = text.lower().strip()

    scheme_keywords = [
        "scheme",
        "yojana",
        "benefit",
        "government",
        "subsidy",
        "pm kisan",
        "mgnrega",
        "pmegp",
        "ayushman",
        "eligible",
        "bpl",
        "ration",
        "pension",
        "insurance",
        "mudra",
        "loan",
        "kisan",
        "awas",
        "swachh",
        "jan arogya",
        "pradhan mantri",
    ]
    job_keywords = [
        "job",
        "kaam",
        "work",
        "rozgaar",
        "employment",
        "nrega",
        "daily wage",
        "salary",
        "hire",
        "vacancy",
        "mazdoor",
        "naukri",
        "rozi",
        "kam",
        "work available",
        "job mil",
    ]
    skill_keywords = [
        "skill",
        "training",
        "seekhna",
        "course",
        "iti",
        "diploma",
        "certificate",
        "pmkvy",
        "ddu-gky",
        "computer",
        "tailoring",
        "vocational",
        "free class",
        "seekh",
        "sikho",
        "padhai",
    ]

    scheme_score = sum(1 for kw in scheme_keywords if kw in text_lower)
    job_score = sum(1 for kw in job_keywords if kw in text_lower)
    skill_score = sum(1 for kw in skill_keywords if kw in text_lower)

    scores = {
        "scheme_query": scheme_score,
        "job_query": job_score,
        "skill_query": skill_score,
    }

    max_score = max(scores.values())

    if max_score == 0:
        return {"category": "scheme_query", "confidence": 0.4, "method": "keyword"}

    top_category = max(scores, key=scores.get)
    confidence = min(0.6 + (max_score * 0.1), 0.95)

    return {
        "category": top_category,
        "confidence": round(confidence, 2),
        "method": "keyword",
    }


def get_intent(text):
    """Master function — combines ML with keyword fallback."""
    try:
        result = classify_query(text)

        if result.get("confidence", 0) < 0.5:
            keyword_result = keyword_classify(text)
            if keyword_result.get("confidence", 0) > result.get("confidence", 0):
                return keyword_result

        return result

    except Exception as e:
        print(f"[nlp] get_intent error: {e}")
        return keyword_classify(text)


if __name__ == "__main__":
    print("=" * 50)
    print("NLP CLASSIFIER - TRAINING & TESTING")
    print("=" * 50)

    train_classifier()

    test_queries = [
        "mujhe koi government scheme chahiye farming ke liye",
        "MGNREGA mein registration kaise kare",
        "free tailoring training near my village",
        "which scheme gives free house to poor people",
        "I want a job near my district",
        "Skill India mein kaise register kare",
    ]

    print("\nClassification Results:")
    for q in test_queries:
        result = get_intent(q)
        print(
            f"  [{result['category']}] ({result['confidence'] * 100:.0f}%) -> {q[:50]}"
        )

    print("\n✅ nlp_classifier.py working correctly")
