from flask import Flask, render_template_string, redirect, url_for, request
import subprocess
import json

app = Flask(__name__)

def run_script(script_name, *args):
    """Helper function to run a script and return its output."""
    result = subprocess.run(['python', script_name, *args], capture_output=True, text=True)
    return result.stdout

@app.route('/')
def index():
    # Run the script and capture the output
    output1 = run_script('starlink_asset_id.py', 'status', 'alert_detail', 'usage')
    try:
        output1 = output1.split('starlink-grpcs-tools: ')[1].replace("'", '"')
        # Check if the output is valid JSON
        try:
            output = json.loads(output1)
            output = json.dumps(output, indent=4)
        except json.JSONDecodeError:
            output = json.dumps({"status": "error", "message": "Invalid JSON format"}, indent=4)
    except IndexError:
        output = json.dumps({"status": "error", "message": "Failed to parse output"}, indent=4)

    # HTML template with buttons
    html_template = """
    <html>
    <head>
        <title>Control Panel</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                color: #333;
                margin: 0;
                padding-top: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            h1 {
                color: #333;
            }
            form {
                margin-bottom: 20px;
            }
            button {
                background-color: #333;
                color: #fff;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #555;
            }
            pre {
                background-color: #e0e0e0;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .container {
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Starlink Control</h1>
            <form action="{{ url_for('execute_action') }}" method="post">
                <button name="action" value="reboot" type="submit">Reboot</button>
                <button name="action" value="stow" type="submit">Stow</button>
                <button name="action" value="unstow" type="submit">Unstow</button>
            </form>
            <h1>Starlink Status</h1>
            <pre>{{ output }}</pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, output=output, output1=output1)

@app.route('/execute_action', methods=['POST'])
def execute_action():
    action = request.form['action']
    output = run_script('dish_control.py', action)
    return render_template_string("""
    <html>
    <head><title>Action Output</title></head>
    <body>
        <h1>Action Output</h1>
        <pre>{{ output }}</pre>
        <a href="{{ url_for('index') }}">Back to Home</a>
    </body>
    </html>
    """, output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
