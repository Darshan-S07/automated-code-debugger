from flask import Flask, request, jsonify
import ast  # For static code analysis
import subprocess  # For executing the code safely
import pylint.lint  # For additional static analysis
from flask_cors import CORS  # Enable CORS for frontend integration
from transformers import pipeline  # Using Hugging Face models
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
def analyze_code_syntax(code):
    """Check syntax errors using AST."""
    try:
        ast.parse(code)
        return None  # No syntax errors
    except SyntaxError as e:
        return str(e)

def run_code(code):
    """Execute the code safely and capture errors."""
    try:
        result = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=5)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)

def get_ai_suggestions(code):
    """Get debugging suggestions from Hugging Face CodeBERT."""
    codebert = pipeline("fill-mask", model="microsoft/codebert-base")
    masked_code = code.replace("print", "<mask>")  # Example masking
    suggestions = codebert(masked_code)
    return suggestions[0]['sequence']

@app.route("/debug", methods=["POST"])
def debug_code():
    """API endpoint to debug code."""
    data = request.json
    code = data.get("code", "")
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    syntax_error = analyze_code_syntax(code)
    execution_result = run_code(code)
    ai_suggestions = get_ai_suggestions(code)
    
    response = {
        "syntax_error": syntax_error,
        "execution_result": execution_result,
        "codebert_suggestion": ai_suggestions
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
