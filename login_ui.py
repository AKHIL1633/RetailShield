import streamlit as st
import requests

API_URL = "http://localhost:5000"

st.set_page_config(page_title="RetailShield Login (MFA)", layout="centered")

st.title("🔒 RetailShield Login (MFA) Demo")

if "email" not in st.session_state:
    st.session_state.email = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "mfa_stage" not in st.session_state:
    st.session_state.mfa_stage = "login"

if st.session_state.mfa_stage == "login":
    st.subheader("Step 1: Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        if submit_login and email and password:
            resp = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                st.success("OTP sent to your email. Please check your inbox.")
                st.session_state.email = email
                st.session_state.role = resp.json().get("role")
                st.session_state.mfa_stage = "otp"
            else:
                st.error(resp.json().get("error", "Login failed."))

if st.session_state.mfa_stage == "otp":
    st.subheader(f"Step 2: MFA Verification ({st.session_state.role.title()})")
    with st.form("otp_form"):
        otp = st.text_input("Enter OTP")
        submit_otp = st.form_submit_button("Verify OTP")
        if submit_otp and otp:
            resp = requests.post(f"{API_URL}/verify_otp", json={"email": st.session_state.email, "otp": otp})
            if resp.status_code == 200:
                st.success(f"✅ Login successful! Welcome, {st.session_state.role.title()}.")
                st.session_state.mfa_stage = "done"
            else:
                st.error(resp.json().get("error", "OTP verification failed."))
    if st.button("← Back to Login"):
        st.session_state.mfa_stage = "login"
        st.session_state.email = ""
        st.session_state.role = ""

if st.session_state.mfa_stage == "done":
    st.write("You are logged in! (Implement dashboard/admin panel here)")
    if st.button("Log Out"):
        st.session_state.mfa_stage = "login"
        st.session_state.email = ""
        st.session_state.role = ""
