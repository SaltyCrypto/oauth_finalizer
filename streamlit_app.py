import streamlit as st
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.config import load_from_dict

st.set_page_config(page_title="OAuth Finalizer + Token Diagnostic", layout="centered")
st.title("🔐 Google Ads OAuth Finalizer + Diagnostic")

config_dict = {
    "developer_token": st.secrets["google_ads"]["developer_token"],
    "client_id": st.secrets["google_ads"]["client_id"],
    "client_secret": st.secrets["google_ads"]["client_secret"],
    "refresh_token": st.secrets["google_ads"]["refresh_token"],
    "login_customer_id": st.secrets["google_ads"]["login_customer_id"],
    "use_proto_plus": True
}

try:
    client = GoogleAdsClient.load_from_dict(config_dict)
    service = client.get_service("CustomerService")

    if st.button("🔍 Show Accessible Customer Accounts"):
        response = service.list_accessible_customers()
        customer_ids = [res.split("/")[-1] for res in response.resource_names]
        st.success("✅ Token is valid and connected.")
        st.write("Accessible Customer IDs:")
        for cid in customer_ids:
            st.code(cid)
        if "3627831893" in customer_ids:
            st.success("🎯 ID 362-783-1893 is accessible ✅")
        else:
            st.warning("⚠️ ID 362-783-1893 is NOT accessible with this token.")

except Exception as e:
    st.error(f"❌ Google Ads error: {e}")