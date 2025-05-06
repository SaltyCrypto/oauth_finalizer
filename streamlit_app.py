import streamlit as st
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google_auth_oauthlib.flow import InstalledAppFlow

st.set_page_config(page_title="OAuth Finalizer + Token Diagnostic", layout="centered")
st.title("🔐 Google Ads OAuth Finalizer + Diagnostic")

# 1. Validate necessary secrets
required_keys = ["developer_token", "client_id", "client_secret", "login_customer_id"]
def validate_config():
    missing = [k for k in required_keys if not st.secrets.get("google_ads", {}).get(k)]
    if missing:
        st.error(f"Missing secrets: {', '.join(missing)}")
        return False
    return True

if not validate_config():
    st.stop()

secrets = st.secrets["google_ads"]

# 2. OAuth authorization flow (if needed)
refresh_token = st.session_state.get("refresh_token") or secrets.get("refresh_token", "")
if not refresh_token:
    st.subheader("1. Authorize Application")
    oauth_config = {
        "installed": {
            "client_id": secrets["client_id"],
            "client_secret": secrets["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    flow = InstalledAppFlow.from_client_config(oauth_config, scopes=["https://www.googleapis.com/auth/adwords"])
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f"[Click here to authorize]({auth_url})")
    code = st.text_input("Enter the authorization code here:")
    if st.button("Exchange Code for Token"):
        try:
            flow.fetch_token(code=code)
            st.session_state["refresh_token"] = flow.credentials.refresh_token
            st.success("✅ Obtained refresh token. You can now run diagnostics.")
        except Exception as e:
            st.error(f"❌ Token exchange failed: {e}")
    st.stop()

# 3. Build Google Ads client
config_dict = {
    "developer_token": secrets["developer_token"],
    "client_id": secrets["client_id"],
    "client_secret": secrets["client_secret"],
    "refresh_token": refresh_token,
    "login_customer_id": secrets["login_customer_id"],
    "use_proto_plus": True
}

def get_client():
    return GoogleAdsClient.load_from_dict(config_dict)

try:
    client = get_client()
except Exception as e:
    st.error(f"❌ Client initialization error: {e}")
    st.stop()

# 4. Service selection for diagnostics
st.subheader("2. Select Service and Run Diagnostic")
service_option = st.selectbox("Choose Google Ads service:", ["CustomerService", "GoogleAdsService"])

if service_option == "CustomerService":
    if st.button("🔍 Show Accessible Customer Accounts"):
        try:
            service = client.get_service("CustomerService")
            response = service.list_accessible_customers()
            cids = [res.split("/")[-1] for res in response.resource_names]
            df = pd.DataFrame({"Customer ID": cids})
            st.dataframe(df)
            for cid in cids:
                st.text_input("Copy Customer ID", cid, key=cid)
            if secrets["login_customer_id"] in cids:
                st.success(f"🎯 ID {secrets['login_customer_id']} is accessible")
            else:
                st.warning(f"⚠️ ID {secrets['login_customer_id']} is NOT accessible")
        except Exception as e:
            st.error(f"❌ API error: {e}")

else:
    st.subheader("Enter a GAQL query for GoogleAdsService")
    default_query = "SELECT campaign.id, campaign.name FROM campaign LIMIT 5"
    query = st.text_area("GAQL Query", value=default_query)
    if st.button("🔍 Run GAQL Query"):
        try:
            ga_service = client.get_service("GoogleAdsService")
            stream = ga_service.search_stream(customer_id=secrets["login_customer_id"], query=query)
            rows = []
            for batch in stream:
                for row in batch.results:
                    rows.append({"Campaign ID": row.campaign.id, "Campaign Name": row.campaign.name})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df)
            else:
                st.info("No results returned.")
        except Exception as e:
            st.error(f"❌ Query failed: {e}")
