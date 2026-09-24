# ============================================================
# PhishGuard - Streamlit Application
# ============================================================

import os
import re
import joblib
import streamlit as st


# ============================================================
# 1. Email Preprocessor
# ============================================================

class EmailPreprocessor:
    """
    Cleans email text before TF-IDF feature extraction.
    """

    def clean_text(self, text):
        text = str(text).lower()

        # Replace URLs with a token
        text = re.sub(
            r"https?://\S+|www\.\S+",
            " url ",
            text
        )

        # Replace email addresses with a token
        text = re.sub(
            r"\S+@\S+",
            " email ",
            text
        )

        # Remove digits
        text = re.sub(
            r"\d+",
            " ",
            text
        )

        # Keep English letters and spaces
        text = re.sub(
            r"[^a-z\s]",
            " ",
            text
        )

        # Remove repeated whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    def clean_dataframe(
        self,
        dataframe,
        text_column="text_combined"
    ):
        dataframe = dataframe.copy()

        dataframe[text_column] = (
            dataframe[text_column]
            .fillna("")
            .astype(str)
            .apply(self.clean_text)
        )

        return dataframe


# ============================================================
# 2. File Paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(file)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "phishguard_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "tfidf_vectorizer.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    BASE_DIR,
    "preprocessor.pkl"
)


# ============================================================
# 3. Load Model Files
# ============================================================

@st.cache_resource
def load_model_files():

    model = joblib.load(
        MODEL_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    preprocessor = joblib.load(
        PREPROCESSOR_PATH
    )

    return (
        model,
        vectorizer,
        preprocessor
    )


# ============================================================
# 4. Page Configuration
# ============================================================

st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# 5. Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 45px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777777;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 6. Check Model Files
# ============================================================

required_files = [
    MODEL_PATH,
    VECTORIZER_PATH,
    PREPROCESSOR_PATH
]

missing_files = [
    file
    for file in required_files
    if not os.path.exists(file)
]

if missing_files:

    st.error(
        "Some model files are missing."
    )

    st.write(
        "Required files:"
    )

    for file in missing_files:
        st.write(
            os.path.basename(file)
        )

    st.stop()


# ============================================================
# 7. Load the Model
# ============================================================

try:

    model, vectorizer, preprocessor = (
        load_model_files()
    )
except Exception as e:

    st.error(
        "Error while loading the model files."
    )

    st.exception(e)

    st.stop()


# ============================================================
# 8. Header
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🛡️ PhishGuard
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Machine Learning Based Phishing Email Detector
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 9. Sidebar
# ============================================================

with st.sidebar:

    st.header(
        "About PhishGuard"
    )

    st.write(
        """
        PhishGuard analyzes email text
        and classifies it as:

        Phishing

        or

        Legitimate
        """
    )

    st.divider()

    st.write(
        "Machine Learning Model:"
    )

    st.write(
        "Logistic Regression"
    )

    st.write(
        "Feature Extraction:"
    )

    st.write(
        "TF-IDF"
    )

    st.write(
        "Classes:"
    )

    st.write(
        "0 = Legitimate"
    )

    st.write(
        "1 = Phishing"
    )


# ============================================================
# 10. Email Input
# ============================================================

st.subheader(
    "📧 Email Analysis"
)

email_text = st.text_area(
    "Paste the email text here:",
    height=300,
    placeholder=(
        "Paste the complete email message here..."
    )
)


# ============================================================
# 11. Analyze Button
# ============================================================

analyze_button = st.button(
    "🔍 Analyze Email",
    use_container_width=True
)


# ============================================================
# 12. Prediction
# ============================================================

if analyze_button:

    if not email_text.strip():

        st.warning(
            "Please enter an email before analyzing."
        )

    else:

        try:

            # ------------------------------------------------
            # Step 1: Clean email text
            # ------------------------------------------------

            cleaned_text = (
                preprocessor.clean_text(
                    email_text
                )
            )

            # ------------------------------------------------
            # Step 2: Convert text to TF-IDF features
            # ------------------------------------------------

            features = (
                vectorizer.transform(
                    [cleaned_text]
                )
            )

            # ------------------------------------------------
            # Step 3: Predict class
            # ------------------------------------------------

            prediction = int(
                model.predict(
                    features
                )[0]
            )

            # ------------------------------------------------
            # Step 4: Get probabilities
            # ------------------------------------------------

            probabilities = (
                model.predict_proba(
                    features
                )[0]
            )

            legitimate_probability = (
                float(
                    probabilities[0]
                )
            )

            phishing_probability = (
                float(
                    probabilities[1]
                )
            )

            # ------------------------------------------------
            # Step 5: Display result
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "📊 Analysis Result"
            )

            if prediction == 1:

                st.error(
                    "🚨 PHISHING EMAIL"
                )
                st.write(
                    f"Phishing Probability: "
                    f"{phishing_probability:.2%}"
                )

            else:

                st.success(
                    "✅ LEGITIMATE EMAIL"
                )

                st.write(
                    f"Legitimate Probability: "
                    f"{legitimate_probability:.2%}"
                )

            # ------------------------------------------------
            # Probability metrics
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Legitimate",
                    f"{legitimate_probability:.2%}"
                )

            with col2:

                st.metric(
                    "Phishing",
                    f"{phishing_probability:.2%}"
                )

            # ------------------------------------------------
            # Probability bars
            # ------------------------------------------------

            st.write(
                "### Probability"
            )

            st.write(
                "Legitimate"
            )

            st.progress(
                legitimate_probability
            )

            st.write(
                "Phishing"
            )

            st.progress(
                phishing_probability
            )

        except Exception as e:

            st.error(
                "An error occurred during email analysis."
            )

            st.exception(e)


# ============================================================
# 13. Footer
# ============================================================

st.divider()

st.caption(
    "PhishGuard — Machine Learning Based "
    "Phishing Email Detection System"
)
