from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Variable to store the entered username
username = ""
user_drives = {}


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
    global user_drives

    parts = command.split()

    if parts[0] == 'enter':
        if len(parts) > 1:
            last_username = username
            username = parts[1]
            if username not in user_drives:
                # Create the user's drive folders (root and shared)
                user_drives[username] = {'root': {}, 'shared': {}}
            return 'Username set to ' + username, last_username
        else:
            return 'Please provide a username.', username
    elif parts[0] == 'print':
        return 'This is an echo.', username
    elif parts[0] == 'hello':
        return 'Hello, world!', username
    elif parts[0] == 'create':
        if len(parts) > 1:
            folder_name = parts[1]
            if folder_name not in user_drives[username]['root']:
                user_drives[username]['root'][folder_name] = {}
                return 'Folder created: ' + folder_name, username
            else:
                return 'Folder already exists: ' + folder_name, username
        else:
            return 'Please provide a folder name.', username
    elif parts[0] == 'share':
        if len(parts) > 1:
            file_name = parts[1]
            if file_name in user_drives[username]['root']:
                user_drives[username]['shared'][file_name] = user_drives[username]['root'][file_name]
                return 'File shared: ' + file_name, username
            else:
                return 'File not found in your drive: ' + file_name, username
        else:
            return 'Please provide a file name to share.', username
    elif parts[0] == 'list':
        return 'drive contents: ' + str(user_drives[username]), username
    else:
        return 'Command not found.', username


if __name__ == '__main__':
    app.run(debug=True)
