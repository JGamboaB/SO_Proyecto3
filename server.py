import xml_drive as xml
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

username = ""
fs = None #file_system NODE
tree = None

#SAVE CHANGES INTO THE XML FILE with every ... SHARE, copy

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

    # Login
    if parts[0] == 'login':
        if len(parts) > 1:
            if username != '':
                return '[Error] You must logout first.', ''
            
            fs = None
            username = parts[1]
            return 'Username set to ' + username, ''
        
        else:
            return '[Error] Please provide a username.', ''
    
    # Logout
    elif parts[0] == 'logout':
        if tree is not None:
            xml.obj_to_xml(tree) #Save file_system into an XML

        username = ''
        fs = tree = None
        return 'You logout.', ''
    
    # Create/Enter a drive/file system
    elif parts[0] == 'drive':
        if username == '':
            return '[Error] You must be signed in to create/enter a drive', ''
        
        xml_path = username + ".xml"
        try:
            fs = xml.xml_to_obj(xml_path)
            tree = fs
            return 'Drive loaded successfully into ' + fs.name, '' #Existing drive
        
        except FileNotFoundError:
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) > 0:
                fs = xml.create_drive(username, parts[1]) #Create a new drive
                tree = fs
                xml.obj_to_xml(tree) #Save file_system into an XML
                return 'Drive created successfully', ''
            return '[Help]: \tdrive &ltsize_in_bytes&gt [Create new drive], \t drive [Enter an existing drive]', ''
    
    # List files and folders in current directory
    elif parts[0] == 'ls':
        if fs is not None:
            return fs.list_dir(), fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Change directory
    elif parts[0] == 'cd':
        if fs is not None:
            if len(parts) > 1:
                last_path = fs.get_abs_path()
                fs_copy = fs #In case it fails
                fs = fs.change_dir_abs(parts[1])

                if fs is not None:
                    return 'Current dir: ' + fs.get_abs_path(), last_path
                
                fs = fs_copy #It failed, so return to the last one
                return '[Error] Incorrect path', fs.get_abs_path()
            
            return '[Help] cd &ltpath&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Make a directory
    elif parts[0] == 'mkdir':
        if fs is not None:
            if len(parts) > 1:

                #if not (fs != tree and not (fs.parent == tree and fs.name == 'shared')): #Cannot modify dir (first directory and shared)
                #    return '[Error] Cannot edit the current directory', fs.get_abs_path()
                
                fs.create_folder(parts[1])
                xml.obj_to_xml(tree) #Save file_system into an XML
                return 'Folder made: ' + parts[1], fs.get_abs_path()
            
            return '[Help] mkdir &ltdir_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Make a file
    elif parts[0] == 'mk':
        if fs is not None:
            if len(parts) > 2:

                #if not (fs != tree and not (fs.parent == tree and fs.name == 'shared')): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', fs.get_abs_path()

                result = fs.create_file(tree, parts[1], ' '.join(parts[2:]))
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'File made: ' + parts[1], fs.get_abs_path()
                return '[Error] Not enough space or file already exists', fs.get_abs_path()
            
            return '[Help] mk &ltfile_name&gt &ltcontents_of_file&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    # Read file
    elif parts[0] == 'cat':
        if fs is not None:
            if len(parts) > 1:
                file = fs.find_file(parts[1])
                if file is not None:
                    return file.read(), fs.get_abs_path()
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] cat &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Properties/Stats of a file
    elif parts[0] == 'stat':
        if fs is not None:
            if len(parts) > 1:
                file = fs.find_file(parts[1])
                if file is not None:
                    return file.stats(), fs.get_abs_path()
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] stat &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    # Remove file
    elif parts[0] == 'rm':
        if fs is not None:
            if len(parts) > 1:

                #if not (fs != tree): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', fs.get_abs_path()
                
                fs.delete_file(parts[1])
                xml.obj_to_xml(tree) #Save file_system into an XML
                return 'File deleted', fs.get_abs_path()
            
            return '[Help] rm &ltfile_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    # Remove directory
    elif parts[0] == 'rmdir':
        if fs is not None:
            if len(parts) > 1:
                
                #if not (fs != tree): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', fs.get_abs_path()
                
                fs.delete_folder(parts[1])
                xml.obj_to_xml(tree) #Save file_system into an XML
                return 'Directory deleted', fs.get_abs_path()
            
            return '[Help] rmdir &ltdir_name&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    # Update file contents
    elif parts[0] == 'edit':
        if fs is not None:
            if len(parts) > 2:
                file = fs.find_file(parts[1])

                if file is not None:
                    result = file.update(tree, ' '.join(parts[2:]))
                    if result is not None:
                        xml.obj_to_xml(tree) #Save file_system into an XML
                        return 'File \''+ parts[1] + '\' has been modified', fs.get_abs_path()
                    return '[Error] Not enough space for changes', fs.get_abs_path()
                
                return '[Error] File not found', fs.get_abs_path()
            return '[Help] edit &ltfile_name&gt &ltnew_contents&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', '' 
    
    # Move file
    elif parts[0] == 'mv':
        if fs is not None:
            if len(parts) > 2:

                result = fs.move_file(parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'File \''+parts[1]+'\' moved to: ' + parts[2], fs.get_abs_path()
                
                return '[Error] Couldn\'t move file to the desired path', fs.get_abs_path()
            return '[Help] mv &ltfile_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Move directory
    elif parts[0] == 'mvdir':
        if fs is not None:
            if len(parts) > 2:

                result = fs.move_dir(parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'Folder \''+parts[1]+'\' moved to: ' + parts[2], fs.get_abs_path()
                
                return '[Error] Couldn\'t move folder to the desired path', fs.get_abs_path()
            return '[Help] mvdir &ltdir_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 
    
    # Copy file
    elif parts[0] == 'vv':
        if fs is not None:
            if len(parts) > 2:

                result = fs.copy_vv_file(tree, parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'File \''+parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                
                return '[Error] Couldn\'t copy file to the desired path', fs.get_abs_path()
            return '[Help] vv &ltfile_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    # Copy directory
    elif parts[0] == 'vvdir':
        if fs is not None:
            if len(parts) > 2:

                result = fs.copy_vv_dir(tree, parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML

                    fs = xml.xml_to_obj(username+".xml")
                    tree = fs

                    return 'Folder \''+parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                
                return '[Error] Couldn\'t copy folder to the desired path', fs.get_abs_path()
            return '[Help] vvdir &ltdir_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded', ''
    
    # Load real file into drive
    elif parts[0] == 'rv':
        if fs is not None:
            if len(parts) > 2:
                result = fs.copy_rv_file(tree, parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'File path\'' +parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t load file to the desired path', fs.get_abs_path()
            return '[Help] rv &ltfile_path&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 
    
    # Load real folder into drive
    elif parts[0] == 'rvdir':
        if fs is not None:
            if len(parts) > 2:
                result = fs.copy_rv_dir(tree, parts[1], parts[2])
                if result is not None:
                    xml.obj_to_xml(tree) #Save file_system into an XML
                    return 'Folder path\'' +parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t load folder to the desired path', fs.get_abs_path()
            return '[Help] rvdir &ltdir_path&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    # Download File
    elif parts[0] == 'vr':
        if fs is not None:
            if len(parts) > 2:
                file = fs.find_file(parts[1])
                result = fs.copy_vr_file(file, parts[2])
                if result is not None:
                    return 'File \'' +parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t download file to the desired path', fs.get_abs_path()
            return '[Help] vr &ltfile_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 
    
    # Download Folder
    elif parts[0] == 'vrdir':
        if fs is not None:
            if len(parts) > 2:
                folder = fs.change_dir_abs(parts[1])
                result = fs.copy_vr_dir(folder, parts[2])
                if result is not None:
                    return 'Folder \'' +parts[1]+'\' copied to: ' + parts[2], fs.get_abs_path()
                return '[Error] Couldn\'t download folder to the desired path', fs.get_abs_path()
            return '[Help] vrdir &ltdir_name&gt &ltnew_path&gt', fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    # Share file
    elif parts[0] == 'sh':
        pass

    # Share folder
    elif parts[0] == 'shdir':
        pass

    # Show the full 'tree' of the file system
    elif parts[0] == 'tree':
        if fs is not None:
            return xml.tree(tree), fs.get_abs_path()
        return '[Error] Drive not loaded.', ''

    # Display all commands
    elif parts[0] == 'help':
        path = ''
        if fs is not None:
            path = fs.get_abs_path()
        return '''
        ---------------------------------[Help]---------------------------------
        login &ltusername&gt
        logout
        drive, drive &ltsize_in_bytes&gt\tEnter/Create a drive
        tree\t\t\t\tShow the full 'tree' of the file system
        ls\t\t\t\tList files and folders in current directory
        cd &ltpath&gt\t\t\tChange directory
        mk &ltfile_name&gt\t\t\tMake a file
        mkdir &ltdir_name&gt\t\tMake a directory
        cat &ltfile_name&gt\t\t\tRead file
        stat &ltfile_name&gt\t\tProperties/Stats of a file
        edit &ltfile_name&gt &ltnew_contents&gt\tUpdate file contents
        mv &ltfile_name&gt &ltnew_path&gt\tMove file
        mvdir &ltdir_name&gt &ltnew_path&gt\tMove directory
        vv &ltfile_name&gt &ltnew_path&gt\tCopy (normal) file
        vvdir &ltdir_name&gt &ltnew_path&gt\tCopy (normal) folder
        vr &ltfile_name&gt &ltnew_path&gt\tCopy (download) file
        vrdir &ltdir_name&gt &ltnew_path&gt\tCopy (download) folder
        rv &ltfile_path&gt &ltnew_path&gt\tCopy (load) file
        rvdir &ltdir_path&gt &ltnew_path&gt\tCopy (load) folder
        sh &ltfile_name&gt &ltusername&gt\tShare file
        shdir &ltdir_name&gt &ltusername&gt\tShare folder
        rm &ltfile_name&gt\t\t\tRemove file
        rmdir &ltname_of_dir&gt\t\tRemove directory
        help\t\t\t\tDisplay all commands
        ''', path

    else:
        path = ''
        if fs is not None:
            path = fs.get_abs_path()
        return '[Error] Command not found. Try \'help\'.', path


if __name__ == '__main__':
    app.run(debug=True)
