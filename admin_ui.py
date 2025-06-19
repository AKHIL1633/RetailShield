import streamlit as st
import requests
import dashboard  # This imports show_dashboard() from your dashboard.py

st.set_page_config(page_title="RetailShield Login (MFA) Demo", layout="centered")

BACKEND_URL = "http://localhost:5000"

def do_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "role" not in st.session_state:
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("🔐 RetailShield Login (MFA) Demo")
    st.header("Step 1: Login")

    email = st.text_input("Email", value=st.session_state.email)
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        resp = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": email, "password": password}
        )
        try:
            data = resp.json()
        except Exception:
            st.error(f"Backend error! Raw response: {resp.text}")
            st.stop()
        if resp.status_code == 200:
            st.success("OTP sent to your email. Check your inbox!")
            st.session_state.email = email
            st.session_state.role = data.get("role", "user")
            st.session_state.awaiting_otp = True
        else:
            st.error(data.get("error", "Login failed!"))

if st.session_state.get("awaiting_otp", False) and not st.session_state.logged_in:
    st.header(f"Step 2: MFA Verification ({st.session_state.role.title()})")
    otp = st.text_input("Enter OTP")
    if st.button("Verify OTP"):
        resp = requests.post(
            f"{BACKEND_URL}/verify_otp",
            json={"email": st.session_state.email, "otp": otp, "role": st.session_state.role}
        )
        try:
            data = resp.json()
        except Exception:
            st.error(f"Backend error! Raw response: {resp.text}")
            st.stop()
        if resp.status_code == 200:
            st.success(f"Login successful! Welcome, {st.session_state.role.title()}.")
            st.session_state.logged_in = True
            st.session_state.awaiting_otp = False
        else:
            st.error(data.get("error", "OTP verification failed."))

    if st.button("← Back to Login"):
        st.session_state.awaiting_otp = False

if st.session_state.logged_in:
    st.success(f"You are logged in as {st.session_state.role.title()}! 🎉")
    dashboard.show_dashboard()
    if st.button("Log Out"):
        do_logout()
        st.experimental_rerun()
