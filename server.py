from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Variable to store the entered username
username = ""

@app.route('/')
def index():
    return render_template('terminal.html', username=username)

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']
    result, updated_username = run_command(command)
    return jsonify(result=result, username=updated_username)

def run_command(command):
    global username
    parts = command.split()

    if parts[0] == 'enter':
        if len(parts) > 1:
            last_username = username
            username = parts[1]
            return 'Username set to ' + username, last_username
        else:
            return 'Please provide a username.', username
    elif parts[0] == 'print':
        return 'This is an echo.', username
    elif parts[0] == 'hello':
        return 'Hello, world!', username
    else:
        return 'Command not found.', username

if __name__ == '__main__':
    app.run(debug=True)
