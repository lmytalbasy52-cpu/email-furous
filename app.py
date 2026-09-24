# ============================================================
# PhishGuard - Phishing Email Detection
# Streamlit Application
# ============================================================

import os
import re
import pickle
import streamlit as st


# ============================================================
# 1. Page Configuration
# ============================================================

st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# 2. File Paths
# ============================================================

# IMPORTANT:
# file refers to the current app.py file.
# This works correctly on Streamlit Cloud.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "phishguard_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "tfidf_vectorizer.pkl"
)


# ============================================================
# 3. Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666666;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
        border: 1px solid #dddddd;
    }

    .safe {
        background-color: #eaf7ee;
    }

    .danger {
        background-color: #fdecec;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. Load Model
# ============================================================

@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    return model


# ============================================================
# 5. Load TF-IDF Vectorizer
# ============================================================

@st.cache_resource
def load_vectorizer():

    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError(
            f"Vectorizer file not found: {VECTORIZER_PATH}"
        )

    with open(VECTORIZER_PATH, "rb") as file:
        vectorizer = pickle.load(file)

    return vectorizer


# ============================================================
# 6. Text Preprocessing
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " URL ",
        text
    )

    # Remove email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        " EMAIL ",
        text
    )

    # Keep letters and numbers
    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 7. Prediction Function
# ============================================================

def predict_email(email_text, model, vectorizer):

    cleaned_text = clean_text(email_text)

    if not cleaned_text:
        raise ValueError(
            "Please enter an email message."
        )

    # Convert text to TF-IDF features
    features = vectorizer.transform(
        [cleaned_text]
    )

    # Prediction
    prediction = model.predict(features)
    result = prediction[0]

    # Probability if supported by the model
    probability = None

    if hasattr(model, "predict_proba"):

        try:

            probabilities = model.predict_proba(
                features
            )

            probability = float(
                max(probabilities[0])
            )

        except Exception:
            probability = None

    return result, probability


# ============================================================
# 8. Convert Model Output to Human Readable Result
# ============================================================

def interpret_result(result):

    value = str(result).lower().strip()

    # Common phishing labels
    phishing_values = {
        "1",
        "phishing",
        "phish",
        "malicious",
        "spam",
        "fraud",
        "danger",
        "dangerous",
        "suspicious",
        "true"
    }

    safe_values = {
        "0",
        "safe",
        "legitimate",
        "ham",
        "benign",
        "normal",
        "false"
    }

    if value in phishing_values:
        return "phishing"

    if value in safe_values:
        return "safe"

    # Numeric fallback
    try:

        number = float(value)

        if number == 1:
            return "phishing"

        if number == 0:
            return "safe"

    except Exception:
        pass

    # If the model has another label,
    # display it as suspicious rather than crashing.
    return value


# ============================================================
# 9. Header
# ============================================================

st.markdown(
    '<div class="main-title">🛡️ PhishGuard/>')
