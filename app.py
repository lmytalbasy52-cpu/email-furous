# ============================================================
# PhishGuard - Phishing Email Detection
# ============================================================

import os
import re
import joblib
import streamlit as st


# ============================================================
# 1. Email Preprocessor Class
# ============================================================

class EmailPreprocessor:
    """
    Preprocesses email text before applying TF-IDF.
    """

    def clean_text(self, text):

        # Convert to string and lowercase
        text = str(text).lower()

        # Replace URLs
        text = re.sub(
            r"https?://\S+|www\.\S+",
            " url ",
            text
        )

        # Replace email addresses
        text = re.sub(
            r"\S+@\S+",
            " email ",
            text
        )

        # Remove numbers
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

        # Remove extra spaces
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
# 2. Page Configuration
# ============================================================

st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# 3. File Paths
# ============================================================

# IMPORTANT:
# file refers to the current app.py file.
# This works correctly on Streamlit Cloud.

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
# 4. Check Required Files
# ============================================================

required_files = {
    "phishguard_model.pkl": MODEL_PATH,
    "tfidf_vectorizer.pkl": VECTORIZER_PATH,
    "preprocessor.pkl": PREPROCESSOR_PATH
}


missing_files = []

for file_name, file_path in required_files.items():

    if not os.path.exists(file_path):

        missing_files.append(
            file_name
        )


if missing_files:

    st.error(
        "❌ Required model files are missing."
    )

    st.write(
        "The following files were not found:"
    )

    for file_name in missing_files:

        st.write(
            f"- {file_name}"
        )

    st.stop()


# ============================================================
# 5. Load Model, Vectorizer and Preprocessor
# ============================================================

@st.cache_resource
def load_files():

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


try:

    model, vectorizer, preprocessor = (
        load_files()
    )

except Exception as e:

    st.error(
        "❌ Error while loading the model files."
    )

    st.exception(e)

    st.stop()


# ============================================================
# 6. Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    .title {
        text-align: center;
        font-size: 45px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 7. Application Header
# ============================================================

st.markdown(
    """
    <div class="title">
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
# 8. Sidebar
# ============================================================

with st.sidebar:

    st.header(
        "🛡️ PhishGuard"
    )

    st.write(
        """
        This system uses Machine Learning
        to detect phishing emails.
        """
    )

    st.divider()

    st.subheader(
        "Model Information"
    )

    st.write(
        "Algorithm: Logistic Regression"
    )

    st.write(
        "Feature Extraction: TF-IDF"
    )

    st.write(
        "Classification: Binary"
    )

    st.write(
        "0 = Legitimate"
    )

    st.write(
        "1 = Phishing"
    )


# ============================================================
# 9. Email Input
# ============================================================

st.subheader(
    "📧 Enter Email Text"
)


email_text = st.text_area(
    "Paste the email message below:",
    height=300,
    placeholder=(
        "Paste the complete email message here..."
    )
)


# ============================================================
# 10. Analyze Button
# ============================================================

analyze = st.button(
    "🔍 Analyze Email",
    use_container_width=True
)


# ============================================================
# 11. Prediction
# ============================================================

if analyze:

    # --------------------------------------------------------
    # Check empty input
    # --------------------------------------------------------

    if not email_text.strip():

        st.warning(
            "⚠️ Please enter an email message first."
        )

    else:

        try:

            # ------------------------------------------------
            # Step 1: Clean the email
            # ------------------------------------------------

            cleaned_text = (
                preprocessor.clean_text(
                    email_text
                )
            )


            # ------------------------------------------------
            # Step 2: Convert text into TF-IDF features
            # ------------------------------------------------

            features = (
                vectorizer.transform(
                    [cleaned_text]
                )
            )


            # ------------------------------------------------
            # Step 3: Predict
            # ------------------------------------------------

            prediction = int(
                model.predict(
                    features
                )[0]
            )


            # ------------------------------------------------
            # Step 4: Probability
            # ------------------------------------------------

            probabilities = (
                model.predict_proba(
                    features
                )[0]
            )


            legitimate_probability = float(
                probabilities[0]
            )


            phishing_probability = float(
                probabilities[1]
            )


            # ------------------------------------------------
            # Step 5: Display results
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "📊 Analysis Result"
            )


            # =================================================
            # PHISHING
            # =================================================
            if prediction == 1:

                st.error(
                    "🚨 PHISHING EMAIL"
                )

                st.write(
                    "The model classified this email as "
                    "Phishing."
                )


            # =================================================
            # LEGITIMATE
            # =================================================

            else:

                st.success(
                    "✅ LEGITIMATE EMAIL"
                )

                st.write(
                    "The model classified this email as "
                    "Legitimate."
                )


            # ------------------------------------------------
            # Probability Metrics
            # ------------------------------------------------

            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Legitimate Probability",
                    f"{legitimate_probability:.2%}"
                )


            with col2:

                st.metric(
                    "Phishing Probability",
                    f"{phishing_probability:.2%}"
                )


            # ------------------------------------------------
            # Probability Bars
            # ------------------------------------------------

            st.subheader(
                "Prediction Probabilities"
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
                "❌ An error occurred during prediction."
            )

            st.exception(e)


# ============================================================
# 12. Footer
# ============================================================

st.divider()

st.caption(
    "PhishGuard | Machine Learning Based "
    "Phishing Email Detection System"
)