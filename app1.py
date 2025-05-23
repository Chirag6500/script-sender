from flask import Flask, request, render_template_string, redirect, url_for
import os
import subprocess
import requests

app = Flask(__name__)

# Set up the directory for the local repo
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
        # Pull the latest changes from the remote repository before making changes
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True, cwd=REPO_DIR)

        # Stage the new file
        subprocess.run(["git", "add", filename], check=True, cwd=REPO_DIR)

        # Commit the changes
        subprocess.run(["git", "commit", "-m", f"Add {filename} via UI"], check=True, cwd=REPO_DIR)

        # Push the changes to the remote repository
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=REPO_DIR)

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

# Check the git status to see if there are uncommitted changes
def check_git_status():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_DIR)
    if result.stdout:
        return False, "There are pending changes. Please commit and push them first."
    return True, "Repository is clean."

# Home route for displaying form and repo files
@app.route('/', methods=['GET', 'POST'])
def index():
    view_file = request.args.get('view')
    file_content = ""
    message = ""

    # Check if the repository has any pending changes
    status_ok, status_message = check_git_status()

    if request.method == 'POST':
        filename = request.form['filename']
        content = request.form['content']
        filepath = os.path.join(REPO_DIR, filename)

        # Save the script file locally
        with open(filepath, 'w') as f:
            f.write(content)

        # Run the git commands to add, commit, and push the file
        success, message = run_git_commands(filename)
        return redirect(url_for('index', message=message))

    # Fetch the list of files from the GitHub repository
    files = fetch_files_from_github()

    if view_file and view_file in files:
        # Fetch the content of the selected file from GitHub
        file_content = fetch_file_content_from_github(view_file)

    message = request.args.get('message', '')
    return render_template_string(TEMPLATE, files=files, file_content=file_content, view_file=view_file, message=message, status_message=status_message)

# Prevent caching of responses
@app.after_request
def add_cache_control(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    return response

if __name__ == '__main__':
    app.run(debug=True)

