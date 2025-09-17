# app.py
import os
from flask import Flask, jsonify, render_template
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# --- IMPORTANT: Set up your API Key ---
# Before running, set your API key in your terminal or deployment service:
# export GOOGLE_API_KEY='your_google_api_key_here'
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    print("🔴 Critical Error: GOOGLE_API_KEY environment variable not set.")
    model = None

# --- Your Secret Contract-Generating Prompt ---
THE_SECRET_PROMPT = """
Generate a simple, one-page freelance Non-Disclosure Agreement (NDA).
The agreement is between a 'Disclosing Party' and a 'Receiving Party'.
Include clauses for:
1. Definition of Confidential Information.
2. Obligations of the Receiving Party.
3. Time Period (make it 3 years).
4. A concluding signature block for both parties.
IMPORTANT: Add a clear disclaimer at the bottom stating: 'This document is AI-generated and is not a substitute for legal advice from a qualified attorney.'
"""

# This function serves the main webpage (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# This is the API endpoint that the button click calls
@app.route('/generate-contract', methods=['POST'])
def generate_contract_api():
    if model is None:
        return jsonify({'error': 'Server is not configured with an API key.'}), 500
    
    try:
        # Call the Gemini API with your secret prompt
        response = model.generate_content(THE_SECRET_PROMPT)
        contract_text = response.text
        return jsonify({'contract_text': contract_text})
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return jsonify({'error': 'Failed to generate contract due to an internal error.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
