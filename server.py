import xml_drive as xml
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

username = ""
fs = None #file_system NODE

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
    global fs
    parts = command.split()

    if parts[0] == 'login':
        if len(parts) > 1:
            fs = None
            last_username = username
            username = parts[1]
            return 'Username set to ' + username, last_username
        else:
            return '[Error] Please provide a username.', username
        
    elif parts[0] == 'logout':
        username = ''
        fs = None
        return 'You logout.', username
    
    elif parts[0] == 'drive':
        if username == '':
            return '[Error] You must be signed in to create/enter a drive', username
        
        xml_path = username + ".xml"
        try:
            fs = xml.xml_to_obj(xml_path)
            return 'Drive loaded successfully into ' + fs.name, username
        except FileNotFoundError:
            if len(parts) > 1: 
                fs = xml.create_drive(username, parts[1])
                return 'Drive created successfully', username
            return '[Help]: \tdrive &ltsize&gt [Create new drive]\n\t drive [Enter an existing drive]', username
        
    elif parts[0] == 'ls':
        if fs is not None:
            return fs.list_dir(), username
        return '[Error] Drive not loaded', username
    
    elif parts[0] == 'cd':
        if fs is not None:
            if len(parts) > 1:
                fs = fs.change_dir_abs(parts[1])
                if fs is not None:
                    return 'Current dir: ' + fs.name, username
                return '[Error] Incorrect path', username
            return '[Help] cd &ltpath&gt', username
        return '[Error] Drive not loaded', username
    
    elif parts[0] == 'mkdir':
        if fs is not None:
            if len(parts) > 1:
                fs.create_folder(parts[1])
                return 'Folder made: ' + parts[1], username
            return '[Help] mkdir &ltname_of_directory&gt', username
        return '[Error] Drive not loaded', username
    
    elif parts[0] == 'mkfile':
        if fs is not None:
            if len(parts) > 2:
                fs.create_file(parts[1], parts[2:])
                return 'File made: ' + parts[1], username
            return '[Help] mkfile &ltname_of_file&gt &ltcontents_of_file&gt', username
        return '[Error] Drive not loaded', username

    else:
        return '[Error] Command not found.', username


if __name__ == '__main__':
    app.run(debug=True)
