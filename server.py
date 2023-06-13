import xml_drive as xml
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

username = ""
fs = None #file_system NODE
tree = None

#SAVE CHANGES INTO THE XML FILE with every mkdir, mkfile, copy, move, delete, ...

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
    global tree
    parts = command.split()

    if parts[0] == 'login':
        if len(parts) > 1:
            fs = None
            username = parts[1]
            return 'Username set to ' + username, ''
        else:
            return '[Error] Please provide a username.', ''
        
    elif parts[0] == 'logout':
        username = ''
        fs = tree = None
        return 'You logout.', ''
    
    elif parts[0] == 'drive':
        if username == '':
            return '[Error] You must be signed in to create/enter a drive', ''
        
        xml_path = username + ".xml"
        try:
            fs = xml.xml_to_obj(xml_path)
            tree = fs
            return 'Drive loaded successfully into ' + fs.name, ''
        except FileNotFoundError:
            if len(parts) > 1: 
                fs = xml.create_drive(username, parts[1])
                tree = fs
                #xml.obj_to_xml(fs) #Save file_system into an XML
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
            return '[Help] mkdir &ltdir_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'mkfile':
        if fs is not None:
            if len(parts) > 2:
                fs.create_file(parts[1], ' '.join(parts[2:]))
                return 'File made: ' + parts[1], fs.get_abs_path()
            return '[Help] mkfile &ltfile_name&gt &ltcontents_of_file&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    elif parts[0] == 'cat':
        if fs is not None:
            if len(parts) > 1:
                file = fs.find_file(parts[1])
                if file is not None:
                    return file.read(), fs.get_abs_path()
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] cat &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'stat':
        if fs is not None:
            if len(parts) > 1:
                file = fs.find_file(parts[1])
                if file is not None:
                    return file.stats(), fs.get_abs_path()
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] stat &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    elif parts[0] == 'rm':
        if fs is not None:
            if len(parts) > 1:
                fs.delete_file(parts[1])
                return 'File deleted', fs.get_abs_path()
            return '[Help] rm &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    elif parts[0] == 'rmdir':
        if fs is not None:
            if len(parts) > 1:
                fs.delete_folder(parts[1])
                return 'Directory deleted', fs.get_abs_path()
            return '[Help] rmdir &ltdir_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    elif parts[0] == 'edit':
        if fs is not None:
            if len(parts) > 2:
                file = fs.find_file(parts[1])
                if file is not None:
                    file.update(' '.join(parts[2:]))
                    return 'File \''+ parts[1] + '\' has been modified', fs.get_abs_path()
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] edit &ltfile_name&gt &ltnew_contents&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    elif parts[0] == 'mv':
        if fs is not None:
            if len(parts) > 2:
                result = fs.move_file(parts[1], parts[2])
                if result is not None:
                    return 'File \''+parts[1]+'\' moved to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t move file to the desired path', fs.get_abs_path()
            return '[Help] mv &ltfile_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    elif parts[0] == 'mvdir':
        if fs is not None:
            if len(parts) > 2:
                result = fs.move_dir(parts[1], parts[2])
                if result is not None:
                    return 'Folder \''+parts[1]+'\' moved to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t move folder to the desired path', fs.get_abs_path()
            return '[Help] mvdir &ltdir_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    elif parts[0] == 'tree':
        if fs is not None:
            return xml.tree(tree), fs.get_abs_path()
        return '[Error] Drive not loaded.', ''

    elif parts[0] == 'help':
        path = ''
        if fs is not None:
            path = fs.get_abs_path()
        return '''[Help]----------------------------
        login &ltusername&gt
        logout
        drive, drive &ltsize&gt
        tree
        ls
        cd &ltpath&gt
        mkdir &ltdir_name&gt 
        mkfile &ltfile_name&gt
        cat &ltfile_name&gt
        stat &ltfile_name&gt
        edit &ltfile_name&gt &ltnew_contents&gt
        mv &ltfile_name&gt &ltnew_path&gt
        mvdir &ltdir_name&gt &ltnew_path&gt
        rmdir &ltname_of_dir&gt
        rm &&ltfile_name&gt
        ''', path

    else:
        path = ''
        if fs is not None:
            path = fs.get_abs_path()
        return '[Error] Command not found. Try \'help\'.', path


if __name__ == '__main__':
    app.run(debug=True)
