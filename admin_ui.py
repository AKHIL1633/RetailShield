import streamlit as st
import requests
import dashboard  # This imports show_dashboard() from your dashboard.py

st.set_page_config(page_title="RetailShield Login (MFA) Demo", layout="centered")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

BACKEND_URL = "http://localhost:5000"

def do_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# --- Horizontally aligned logo + title bar ---
st.markdown("""
<div class="brandbar-horiz">
    <img src="walmart_logo.png" class="brandbar-logo" alt="RetailShield Logo"/>
    <div class="brandbar-titlebox">
        <div class="brandbar-title">
            RetailShield Login <span class="brandbar-title-mfa">(MFA) Demo</span>
        </div>
        <div class="brandbar-subdesc">Secure Login & Fraud Dashboard</div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Main centered container ---
st.markdown('<div class="center-content">', unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# --- LOGIN CARD ---
if not st.session_state.logged_in:
    st.markdown('<div class="card login-section">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Step 1: Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    email = st.text_input("Email", value=st.session_state.email, key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
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
    st.markdown('</div>', unsafe_allow_html=True)

# --- OTP CARD ---
if st.session_state.get("awaiting_otp", False) and not st.session_state.logged_in:
    st.markdown('<div class="card otp-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">Step 2: MFA Verification <span class="role-badge">{st.session_state.role.title()}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    otp = st.text_input("Enter OTP", key="otp_input")
    if st.button("Verify OTP", key="verify_otp_button"):
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
    if st.button("← Back to Login", key="back_to_login"):
        st.session_state.awaiting_otp = False
    st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARD CARD ---
if st.session_state.logged_in:
    st.markdown('<div class="card dashboard-section">', unsafe_allow_html=True)
    st.success(f"You are logged in as {st.session_state.role.title()}! 🎉")
    dashboard.show_dashboard()
    if st.button("Log Out", key="logout_button"):
        do_logout()
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # .center-content
