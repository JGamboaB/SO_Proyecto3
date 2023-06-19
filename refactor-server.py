import xml_drive as xml
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class FileSystem:
    username = ""
    fs = None  # file_system NODE
    tree = None
    def __init__(self):
        self.username = ""
        self.fs = None  # file_system NODE
        self.tree = None
    
    def run_command(self, command):
        parts = command.split()
        overwrite = parts[-1] == '-o'

        # Login
        if parts[0] == 'login':
            return self.login(parts)
        # Logout
        elif parts[0] == 'logout':
            return self.logout()
        # Create/Enter a drive/file system
        elif parts[0] == 'drive':
            return self.create_or_enter_drive(parts)
        # List files and folders in current directory
        elif parts[0] == 'ls':
            return self.list_directory()
        # Change directory
        elif parts[0] == 'cd':
            return self.change_directory(parts)
        # Make a directory
        elif parts[0] == 'mkdir':
            return self.make_directory(parts, overwrite)
        # Make a file
        elif parts[0] == 'mk':
            return self.make_file(parts, overwrite)
        # Read file
        elif parts[0] == 'cat':
            return self.read_file(parts)
        # Properties/Stats of a file
        elif parts[0] == 'stat':
            return self.file_stats(parts)
        # Remove file
        elif parts[0] == 'rm':
            return self.remove_file(parts)
        # Remove directory
        elif parts[0] == 'rmdir':
            return self.remove_directory(parts)
        # Update file contents
        elif parts[0] == 'edit':
            return self.update_file_contents(parts, overwrite)
        # Move file
        elif parts[0] == 'mv':
            return self.move_file(parts, overwrite)
        # Move directory
        elif parts[0] == 'mvdir':
            return self.move_directory(parts, overwrite)
        # Copy file
        elif parts[0] == 'vv':
            return self.copy_file(parts, overwrite)
        # Copy directory
        elif parts[0] == 'vvdir':
            return self.copy_directory(parts, overwrite)
        # Load real file into drive
        elif parts[0] == 'rv':
            return self.load_real_file(parts, overwrite)
        # Load real folder into drive
        elif parts[0] == 'rvdir':
            return self.load_real_folder(parts, overwrite)
        # Download File
        elif parts[0] == 'vr':
            return self.download_file(parts)
        # Download Folder
        elif parts[0] == 'vrdir':
            return self.download_folder(parts)
        # Share file
        elif parts[0] == 'sh':
            return self.share_file(parts, overwrite)
        # Share folder
        elif parts[0] == 'shdir':
            return self.share_folder(parts, overwrite)
        # Properties/Stats of a file
        elif parts[0] == 'tree':
            return self.show_tree(parts)
        # Properties/Stats of a file
        elif parts[0] == 'help':
            return self.help(parts)
        else:
            path = ''
            if self.fs is not None:
                path = self.fs.get_abs_path()
            return '[Error] Command not found. Try \'help\'.', path

        
    def login(self, parts):
        if len(parts) > 1:
            if self.username != '':
                return '[Error] You must logout first.', ''
            
            self.fs = None
            self.username = parts[1]
            return 'self.Username set to ' + self.username, ''
        
        else:
            return '[Error] Please provide a self.username.', ''

    def logout(self):
        if self.tree is not None:
            xml.obj_to_xml(self.tree) #Save file_system into an XML

        self.username = ''
        self.fs = self.tree = None
        return 'You logout.', ''

    def create_or_enter_drive(self, parts):
        if self.username == '':
            return '[Error] You must be signed in to create/enter a drive', ''
        
        xml_path = self.username + ".xml"
        try:
            self.fs = xml.xml_to_obj(xml_path)
            self.tree = self.fs
            return 'Drive loaded successfully into ' + self.fs.name, '' #Existing drive
        
        except FileNotFoundError:
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) > 0:
                self.fs = xml.create_drive(self.username, parts[1]) #Create a new drive
                self.tree = self.fs
                xml.obj_to_xml(self.tree) #Save file_system into an XML
                return 'Drive created successfully', ''
            return '[Help]: \tdrive &ltsize_in_bytes&gt [Create new drive], \t drive [Enter an existing drive]', ''

    def list_directory(self):
        if self.fs is not None:
            return self.fs.list_dir(), self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''
 
    def change_directory(self, parts):
        if self.fs is not None:
            if len(parts) > 1:
                last_path = self.fs.get_abs_path()
                self.fs_copy = self.fs #In case it fails
                self.fs = self.fs.change_dir_abs(parts[1])

                if self.fs is not None:
                    return 'Current dir: ' + self.fs.get_abs_path(), last_path
                
                self.fs = self.fs_copy #It failed, so return to the last one
                return '[Error] Incorrect path', self.fs.get_abs_path()
            
            return '[Help] cd &ltpath&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def make_directory(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) == 2:

                #if not (self.fs != self.tree and not (self.fs.parent == self.tree and self.fs.name == 'shared')): #Cannot modify dir (first directory and shared)
                #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()
                
                result = self.fs.create_folder(parts[1], overwrite)

                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'Folder made: ' + parts[1], self.fs.get_abs_path()
                return '[Error] Folder already exists', self.fs.get_abs_path()
            
            return '[Help] mkdir &ltdir_name&gt [No Spaces Allowed]', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def make_file(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:

                #if not (self.fs != self.tree and not (self.fs.parent == self.tree and self.fs.name == 'shared')): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()

                # Validate the file_name has no spaces and has an extension
                if '.' not in parts[1]:
                    return '[Error] The file name contains spaces or lacks an extension.', self.fs.get_abs_path()

                # So it doesn't include the overwrite flag into the contents of the file
                if not overwrite:
                    contents = ' '.join(parts[2:])
                else:
                    contents = ' '.join(parts[2:-1]) #So it doesn't save the flag '-o' into the contents of the file

                result = self.fs.create_file(self.tree, parts[1], contents, overwrite)

                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'File made: ' + parts[1], self.fs.get_abs_path()
                return '[Error] Not enough space or file already exists', self.fs.get_abs_path()
            
            return '[Help] mk &ltfile_name&gt &ltcontents_of_file&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def read_file(self, parts):
        if self.fs is not None:
            if len(parts) > 1:
                file = self.fs.find_file(parts[1])
                if file is not None:
                    return file.read(), self.fs.get_abs_path()
                return '[Error] File not found', self.fs.get_abs_path()
            return '[Help] cat &ltfile_name&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def file_stats(self, parts):
        if self.fs is not None:
            if len(parts) > 1:
                file = self.fs.find_file(parts[1])
                if file is not None:
                    return file.stats(), self.fs.get_abs_path()
                return '[Error] File not found', self.fs.get_abs_path()
            return '[Help] stat &ltfile_name&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    def remove_file(self, parts):
        if self.fs is not None:
            if len(parts) > 1:

                #if not (self.fs != self.tree): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()
                
                self.fs.delete_file(parts[1])
                xml.obj_to_xml(self.tree) #Save file_system into an XML
                return 'File deleted', self.fs.get_abs_path()
            
            return '[Help] rm &ltfile_name&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    def remove_directory(self, parts):
        if self.fs is not None:
            if len(parts) > 1:
                
                #if not (self.fs != self.tree): #Cannot modify dir
                #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()
                
                self.fs.delete_folder(parts[1])
                xml.obj_to_xml(self.tree) #Save file_system into an XML
                return 'Directory deleted', self.fs.get_abs_path()
            
            return '[Help] rmdir &ltdir_name&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    def update_file_contents(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                file = self.fs.find_file(parts[1])

                if file is not None:
                    result = file.update(self.tree, ' '.join(parts[2:]))
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'File \''+ parts[1] + '\' has been modified', self.fs.get_abs_path()
                    return '[Error] Not enough space for changes', self.fs.get_abs_path()
                
                return '[Error] File not found', self.fs.get_abs_path()
            return '[Help] edit &ltfile_name&gt &ltnew_contents&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', '' 

    def move_file(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                result = self.fs.move_file(parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'File \''+parts[1]+'\' moved to: ' + parts[2], self.fs.get_abs_path()
                
                return '[Error] Couldn\'t move file to the desired path', self.fs.get_abs_path()
            return '[Help] mv &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def move_directory(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:

                result = self.fs.move_dir(parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'Folder \''+parts[1]+'\' moved to: ' + parts[2], self.fs.get_abs_path()
                
                return '[Error] Couldn\'t move folder to the desired path', self.fs.get_abs_path()
            return '[Help] mvdir &ltdir_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def copy_file(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:

                result = self.fs.copy_vv_file(self.tree, parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'File \''+parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                
                return '[Error] Couldn\'t copy file to the desired path', self.fs.get_abs_path()
            return '[Help] vv &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def copy_directory(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:

                result = self.fs.copy_vv_dir(self.tree, parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML

                    self.fs = xml.xml_to_obj(self.username+".xml")
                    self.tree = self.fs

                    return 'Folder \''+parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                
                return '[Error] Couldn\'t copy folder to the desired path', self.fs.get_abs_path()
            return '[Help] vvdir &ltdir_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded', ''

    def load_real_file(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                result = self.fs.copy_rv_file(self.tree, parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'File path\'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                return '[Error] Couldn\'t load file to the desired path', self.fs.get_abs_path()
            return '[Help] rv &ltfile_path&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def load_real_folder(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                result = self.fs.copy_rv_dir(self.tree, parts[1], parts[2], overwrite)
                if result is not None:
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'Folder path\'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                return '[Error] Couldn\'t load folder to the desired path', self.fs.get_abs_path()
            return '[Help] rvdir &ltdir_path&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def download_file(self, parts):
        if self.fs is not None:
            if len(parts) > 2:
                file = self.fs.find_file(parts[1])
                result = self.fs.copy_vr_file(file, parts[2])
                if result is not None:
                    return 'File \'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                return '[Error] Couldn\'t download file to the desired path', self.fs.get_abs_path()
            return '[Help] vr &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 
    
    def download_folder(self, parts):
        if self.fs is not None:
            if len(parts) > 2:
                folder = self.fs.change_dir_abs(parts[1])
                result = self.fs.copy_vr_dir(folder, parts[2])
                if result is not None:
                    return 'Folder \'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                return '[Error] Couldn\'t download folder to the desired path', self.fs.get_abs_path()
            return '[Help] vrdir &ltdir_name&gt &ltnew_path&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def share_file(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                result = self.fs.share_file(parts[1], parts[2], overwrite, self.username)
                if result is not None:
                    return 'File \''+parts[1]+'\' successfully shared to User \''+ parts[2] +'\'', self.fs.get_abs_path()
                return '[Error] Couldn\'t share the file to the desired user.', self.fs.get_abs_path()
            return '[Help] sh &ltfile_name&gt &ltself.username&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def share_folder(self, parts, overwrite):
        if self.fs is not None:
            if len(parts) > 2:
                result = self.fs.share_folder(parts[1], parts[2], overwrite, self.username)
                if result is not None:
                    return 'Folder \''+parts[1]+'\' successfully shared to User \''+ parts[2] +'\'', self.fs.get_abs_path()
                return '[Error] Couldn\'t share the folder to the desired user.', self.fs.get_abs_path()
            return '[Help] shdir &ltdir_name&gt &ltself.username&gt', self.fs.get_abs_path()
        return '[Error] Drive not loaded.', '' 

    def show_tree(self, parts):
        if self.fs is not None:
            return xml.tree(self.tree), self.fs.get_abs_path()
        return '[Error] Drive not loaded.', ''

    def help(self, parts):
        path = ''
        if self.fs is not None:
            path = self.fs.get_abs_path()
        return '''
        -------------------------------------[Help]-------------------------------------
        login &ltself.username&gt
        logout
        drive, drive &ltsize_in_bytes&gt\tEnter/Create a drive
        self.tree\t\t\t\tShow the full 'self.tree' of the file system
        ls\t\t\t\tList files and folders in current directory
        cd &ltpath&gt\t\t\tChange directory
        mk &ltfile_name&gt &ltcontents&gt\tMake a file\t\t\t-o (Overwrite)
        mkdir &ltdir_name&gt\t\tMake a directory\t\t-o (Overwrite)
        cat &ltfile_name&gt\t\t\tRead file
        stat &ltfile_name&gt\t\tProperties/Stats of a file
        edit &ltfile_name&gt &ltnew_contents&gt\tUpdate file contents
        mv &ltfile_name&gt &ltnew_path&gt\tMove file\t\t\t-o (Overwrite)
        mvdir &ltdir_name&gt &ltnew_path&gt\tMove directory\t\t\t-o (Overwrite)
        vv &ltfile_name&gt &ltnew_path&gt\tCopy (normal) file\t\t-o (Overwrite)
        vvdir &ltdir_name&gt &ltnew_path&gt\tCopy (normal) folder\t\t-o (Overwrite)
        vr &ltfile_name&gt &ltnew_path&gt\tCopy (download) file
        vrdir &ltdir_name&gt &ltnew_path&gt\tCopy (download) folder
        rv &ltfile_path&gt &ltnew_path&gt\tCopy (load) file\t\t-o (Overwrite)
        rvdir &ltdir_path&gt &ltnew_path&gt\tCopy (load) folder\t\t-o (Overwrite)
        sh &ltfile_name&gt &ltself.username&gt\tShare file\t\t\t-o (Overwrite)
        shdir &ltdir_name&gt &ltself.username&gt\tShare folder\t\t\t-o (Overwrite)
        rm &ltfile_name&gt\t\t\tRemove file
        rmdir &ltname_of_dir&gt\t\tRemove directory
        help\t\t\t\tDisplay all commands
        ''', path

# Crea una lista de clientes
user_list = []

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@app.route('/login', methods=['POST'])
def login():
    command = request.form['command']

    user = FileSystem()
    old_user = None
    
    if len(user_list) != 0:
        for obj in user_list:
            if obj.username == command:
                old_user = obj
                break

    if old_user == None:
        user.username = command
        user_list.append(user)
        user.login(command)
        return jsonify(str(user.username))
    else:
        old_user.login(old_user.username)
        return jsonify(str(old_user.username))


@app.route('/execute', methods=['POST'])
def execute():
    user = request.args.get('user')
    
    userClass = None
    for obj in user_list:
        if obj.username == user:
            userClass = obj
            break
    command = request.form['command']
    result, updated_path = obj.run_command(command)
    return jsonify(result=result, path=updated_path)


   


if __name__ == '__main__':
    app.run(debug=True)
