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
    result, updated_path = run_command(command)
    return jsonify(result=result, path=updated_path)

def run_command(command):
    global username
    global fs
    parts = command.split()

    if parts[0] == 'login':
        if len(parts) > 1:
            fs = None
            last_username = username
            username = parts[1]
            return 'Username set to ' + username, ''
        else:
            return '[Error] Please provide a username.', ''
        
    elif parts[0] == 'logout':
        username = ''
        fs = None
        return 'You logout.', ''
    
    elif parts[0] == 'drive':
        if username == '':
            return '[Error] You must be signed in to create/enter a drive', ''
        
        xml_path = username + ".xml"
        try:
            fs = xml.xml_to_obj(xml_path)
            return 'Drive loaded successfully into ' + fs.name, ''
        except FileNotFoundError:
            if len(parts) > 1: 
                fs = xml.create_drive(username, parts[1])
                return 'Drive created successfully', ''
            return '[Help]: \tdrive &ltsize&gt [Create new drive]\n\t drive [Enter an existing drive]', ''
        
    elif parts[0] == 'ls':
        if fs is not None:
            return fs.list_dir(), fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'cd':
        if fs is not None:
            if len(parts) > 1:
                last_path = fs.get_abs_path()
                fs_copy = fs #In case it fails
                fs = fs.change_dir_abs(parts[1])
                if fs is not None:
                    return 'Current dir: ' + fs.get_abs_path(), last_path
                fs = fs_copy
                return '[Error] Incorrect path', fs.get_abs_path()
            return '[Help] cd &ltpath&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'mkdir':
        if fs is not None:
            if len(parts) > 1:
                fs.create_folder(parts[1])
                return 'Folder made: ' + parts[1], fs.get_abs_path()
            return '[Help] mkdir &ltname_of_directory&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'mkfile':
        if fs is not None:
            if len(parts) > 2:
                fs.create_file(parts[1], parts[2:])
                return 'File made: ' + parts[1], fs.get_abs_path()
            return '[Help] mkfile &ltname_of_file&gt &ltcontents_of_file&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    else:
        if fs is not None:
            return '[Error] Command not found.', fs.get_abs_path()
        return '[Error] Command not found.', ''


if __name__ == '__main__':
    app.run(debug=True)
