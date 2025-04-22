from flask import Flask, request, render_template_string, redirect, url_for
import os
import subprocess
import requests

app = Flask(__name__)

# Set up the directory for local repo
REPO_DIR = os.path.join(os.getcwd(), "repo")
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)

GITHUB_REPO_API = "https://api.github.com/repos/Chirag6500/script-sender/contents/repo"

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Script Sender</title>
</head>
<body>
    <h2>Create & Push a Script to GitHub</h2>
    {% if message %}
        <p><strong>{{ message }}</strong></p>
    {% endif %}
    <form method="post" action="/">
        <label>Script Name (e.g. script3.py):</label><br>
        <input type="text" name="filename" required><br><br>

        <label>Script Content:</label><br>
        <textarea name="content" rows="10" cols="50" required></textarea><br><br>

        <input type="submit" value="Send">
    </form>

    <hr>
    <h3>Repository Files</h3>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('index', view=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    {% if file_content %}
    <hr>
    <h3>Viewing: {{ view_file }}</h3>
    <pre>{{ file_content }}</pre>
    {% endif %}
</body>
</html>
'''

# Run git commands to add, commit, and push the file
def run_git_commands(filename):
    try:
        subprocess.run(["git", "add", filename], check=True, cwd=REPO_DIR)
        subprocess.run(["git", "commit", "-m", f"Add {filename} via UI"], check=True, cwd=REPO_DIR)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True, cwd=REPO_DIR)
        return True, "✅ Script pushed to GitHub!"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Git error: {e}"

# Fetch files from GitHub repository
def fetch_files_from_github():
    response = requests.get(GITHUB_REPO_API)
    if response.status_code == 200:
        return [file['name'] for file in response.json()]
    return []

# Fetch file content from GitHub
def fetch_file_content_from_github(file_name):
    file_url = f"https://raw.githubusercontent.com/Chirag6500/script-sender/main/repo/{file_name}"
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    return "❌ Could not fetch file content"

# Home route for displaying form and repo files
@app.route('/', methods=['GET', 'POST'])
def index():
    view_file = request.args.get('view')
    file_content = ""
    message = ""

    if request.method == 'POST':
        filename = request.form['filename']
        content = request.form['content']
        filepath = os.path.join(REPO_DIR, filename)

        # Save file locally
        with open(filepath, 'w') as f:
            f.write(content)

        success, message = run_git_commands(filename)
        return redirect(url_for('index', message=message))

    files = fetch_files_from_github()
    if view_file and view_file in files:
        file_content = fetch_file_content_from_github(view_file)

    message = request.args.get('message', '')
    return render_template_string(TEMPLATE, files=files, file_content=file_content, view_file=view_file, message=message)

# Prevent caching of responses
@app.after_request
def add_cache_control(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    return response

if __name__ == '__main__':
    app.run(debug=True)

