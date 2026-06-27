from flask import Flask, render_template, request
import requests

app = Flask(__name__)
TIMEOUT = 30

def post_json(url, headers, data):
    try:
        r = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        return r.status_code
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except requests.exceptions.RequestException:
        return "REQUEST_ERROR"

def check_openai(api_key):
    return post_json(
        "https://api.openai.com/v1/responses",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"model": "gpt-4.1-mini", "input": "hello", "max_output_tokens": 5}
    )

def check_gemini(api_key):
    return post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        {"Content-Type": "application/json"},
        {"contents": [{"parts": [{"text": "hello"}]}]}
    )

def check_groq(api_key):
    return post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 5
        }
    )

PROVIDERS = {
    "OpenAI": check_openai,
    "Google Gemini": check_gemini,
    "Groq": check_groq,
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()

        if not api_key:
            result = ("NONE", "NO API KEY ENTERED", "bad")
        else:
            for name, checker in PROVIDERS.items():
                status = checker(api_key)

                if status in [200, 201]:
                    result = (name, "WORKING", "good")
                    break
                elif status == 429:
                    result = (name, "VALID BUT QUOTA / RATE LIMIT", "warn")
                    break
                elif status == 403:
                    result = (name, "VALID BUT ACCESS FORBIDDEN", "warn")
                    break

            if result is None:
                result = ("NOT MATCHED", "API KEY NOT WORKING", "bad")

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)