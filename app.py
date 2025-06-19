from flask import Flask, request, jsonify
from mfa import generate_otp, verify_otp
from fraud_model import detect_fraud
from blockchain import Blockchain

app = Flask(__name__)

# --- User Database (simple for demo)
USERS = {
    "akhilpupala@gmail.com": {"password": "zeak scbe kqzg peiv", "role": "admin"},
    "user@example.com": {"password": "userpass", "role": "user"}
}

# --- Blockchain Init
bc = Blockchain()

@app.route('/')
def home():
    return 'RetailShield backend is running ✅'

@app.route('/login', methods=['POST'])
def login():
    """
    POST { "email": "...", "password": "..." }
    """
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        if not (email and password):
            return jsonify({"error": "Email and password required"}), 400
        user = USERS.get(email)
        if not user or user["password"] != password:
            return jsonify({"error": "Invalid credentials"}), 401
        role = user["role"]   # <-- GET THE ROLE
        # Generate OTP for MFA step (pass role!)
        otp_sent = generate_otp(email, role)
        if otp_sent:
            return jsonify({
                "message": "OTP sent to your email. Proceed to OTP verification.",
                "role": role
            })
        else:
            return jsonify({"error": "Failed to send OTP"}), 500
    except Exception as e:
        print("Error in /login:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/verify_otp', methods=['POST'])
def otp_check():
    """
    POST { "email": "...", "otp": "...", "role": "..." }
    """
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        otp = data.get('otp')
        role = data.get('role')
        if not (email and otp and role):
            return jsonify({'error': 'Email, OTP, and role required'}), 400
        if verify_otp(email, role, otp):
            return jsonify({'message': 'OTP verified successfully'})
        return jsonify({'error': 'Invalid OTP'}), 401
    except Exception as e:
        print("Error in /verify_otp:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/check_transaction', methods=['POST'])
def check_transaction():
    """
    Accepts either a single transaction (dict) or a list of transactions (batch).
    Each transaction is processed for fraud detection and logged to blockchain.
    """
    try:
        data = request.get_json(force=True)
        required_fields = [
            'amount', 'frequency', 'location_match',
            'payment_method', 'time_of_day', 'device_known', 'is_return'
        ]

        # --- Batch submission
        if isinstance(data, list):
            results = []
            for tx in data:
                if not all(k in tx for k in required_fields):
                    results.append({'error': f"Missing fields in transaction: {required_fields}"})
                    continue
                result = detect_fraud(tx)
                tx_log = {
                    "transaction": tx,
                    "result": result["risk_level"]
                }
                bc.add_block(tx_log)
                results.append(result)
            return jsonify(results)

        # --- Single transaction
        if not all(k in data for k in required_fields):
            return jsonify({'error': f"All transaction fields required: {required_fields}"}), 400
        result = detect_fraud(data)
        tx_log = {
            "transaction": data,
            "result": result["risk_level"]
        }
        bc.add_block(tx_log)
        return jsonify(result)
    except Exception as e:
        print("Error in /check_transaction:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/view_blockchain', methods=['GET'])
def view_blockchain():
    """
    Returns the full blockchain as JSON (for dashboard log)
    """
    try:
        return jsonify(bc.get_chain())
    except Exception as e:
        print("Error in /view_blockchain:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
