import streamlit as st
from google_auth_oauthlib.flow import Flow

st.title("🔐 Google Ads OAuth Finalizer")

# -- Use secrets from Streamlit Cloud
CLIENT_ID = st.secrets["google_ads"]["client_id"]
CLIENT_SECRET = st.secrets["google_ads"]["client_secret"]
REDIRECT_URI = "https://your-app-name.streamlit.app"  # Replace this!

SCOPES = ["https://www.googleapis.com/auth/adwords"]

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

query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]
    flow.fetch_token(code=code)
    creds = flow.credentials
    st.success("✅ Refresh Token Generated!")
    st.code(creds.refresh_token, language="bash")
    st.info("Copy this into your Streamlit `st.secrets` to finalize setup.")
