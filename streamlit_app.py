import streamlit as st
from google_auth_oauthlib.flow import Flow

st.set_page_config(page_title="Google Ads OAuth Finalizer", layout="centered")
st.title("🔐 Google Ads OAuth Finalizer")

# ✅ Replace this with your actual Streamlit Cloud app URL
REDIRECT_URI = "https://oappfinalizer-uax2d6ijwttkmj57ybnomg.streamlit.app"

# ✅ Load credentials from Streamlit Secrets
CLIENT_ID = st.secrets["google_ads"]["client_id"]
CLIENT_SECRET = st.secrets["google_ads"]["client_secret"]

SCOPES = ["https://www.googleapis.com/auth/adwords"]

# Set up OAuth flow
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    },
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

auth_url, _ = flow.authorization_url(
    prompt="consent",
    access_type="offline",
    include_granted_scopes="true"
)

st.markdown(f"[👉 Click here to authorize with Google]({auth_url})")

# ✅ Use new query param API (replaces deprecated one)
query_params = st.query_params

if "code" in query_params:
    code = query_params["code"]
    flow.fetch_token(code=code)
    creds = flow.credentials
    st.success("✅ Refresh Token Generated!")
    st.code(creds.refresh_token, language="bash")
    st.info("Copy this token into your main app’s `st.secrets` or `google-ads.yaml`.")
