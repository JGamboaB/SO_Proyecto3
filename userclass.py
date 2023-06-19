import xml_drive as xml

class User:
    def __init__(self, username):
        self.username = username
        self.fs = None
        self.tree = None

    def logout(self):
        if self.tree is not None:
            xml.obj_to_xml(self.tree)  # Save file_system into an XML

        self.fs = None
        self.tree = None
        return 'You logged out.'

    def terminal(self, parts, overwrite):

        # Login
        if parts[0] == 'login':
            if len(parts) > 1:
                if self.username != '':
                    return '[Error] You must logout first.', ''

                self.fs = None
                self.username = parts[1]
                return 'self.username set to ' + self.username, ''

            else:
                return '[Error] Please provide a self.username.', ''

        # Logout
        elif parts[0] == 'logout':
            if self.tree is not None:
                xml.obj_to_xml(self.tree) #Save file_system into an XML

            self.username = ''
            self.fs = self.tree = None
            return 'You logout.', ''

        # Create/Enter a drive/file system
        elif parts[0] == 'drive':
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

        # List files and folders in current directory
        elif parts[0] == 'ls':
            if self.fs is not None:
                return self.fs.list_dir(), self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Change directory
        elif parts[0] == 'cd':
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

        # Make a directory
        elif parts[0] == 'mkdir':
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

        # Make a file
        elif parts[0] == 'mk':
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

        # Read file
        elif parts[0] == 'cat':
            if self.fs is not None:
                if len(parts) > 1:
                    file = self.fs.find_file(parts[1])
                    if file is not None:
                        return file.read(), self.fs.get_abs_path()
                    return '[Error] File not found', self.fs.get_abs_path()
                return '[Help] cat &ltfile_name&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Properties/Stats of a file
        elif parts[0] == 'stat':
            if self.fs is not None:
                if len(parts) > 1:
                    file = self.fs.find_file(parts[1])
                    if file is not None:
                        return file.stats(), self.fs.get_abs_path()
                    return '[Error] File not found', self.fs.get_abs_path()
                return '[Help] stat &ltfile_name&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Remove file
        elif parts[0] == 'rm':
            if self.fs is not None:
                if len(parts) > 1:

                    #if not (self.fs != self.tree): #Cannot modify dir
                    #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()

                    self.fs.delete_file(parts[1])
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'File deleted', self.fs.get_abs_path()

                return '[Help] rm &ltfile_name&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Remove directory
        elif parts[0] == 'rmdir':
            if self.fs is not None:
                if len(parts) > 1:

                    #if not (self.fs != self.tree): #Cannot modify dir
                    #    return '[Error] Cannot edit the current directory', self.fs.get_abs_path()

                    self.fs.delete_folder(parts[1])
                    xml.obj_to_xml(self.tree) #Save file_system into an XML
                    return 'Directory deleted', self.fs.get_abs_path()

                return '[Help] rmdir &ltdir_name&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Update file contents
        elif parts[0] == 'edit':
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

        # Move file
        elif parts[0] == 'mv':
            if self.fs is not None:
                if len(parts) > 2:
                    result = self.fs.move_file(parts[1], parts[2], overwrite)
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'File \''+parts[1]+'\' moved to: ' + parts[2], self.fs.get_abs_path()

                    return '[Error] Couldn\'t move file to the desired path', self.fs.get_abs_path()
                return '[Help] mv &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Move directory
        elif parts[0] == 'mvdir':
            if self.fs is not None:
                if len(parts) > 2:

                    result = self.fs.move_dir(parts[1], parts[2], overwrite)
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'Folder \''+parts[1]+'\' moved to: ' + parts[2], self.fs.get_abs_path()

                    return '[Error] Couldn\'t move folder to the desired path', self.fs.get_abs_path()
                return '[Help] mvdir &ltdir_name&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Copy file
        elif parts[0] == 'vv':
            if self.fs is not None:
                if len(parts) > 2:

                    result = self.fs.copy_vv_file(self.tree, parts[1], parts[2], overwrite)
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'File \''+parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()

                    return '[Error] Couldn\'t copy file to the desired path', self.fs.get_abs_path()
                return '[Help] vv &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded', ''

        # Copy directory
        elif parts[0] == 'vvdir':
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

        # Load real file into drive
        elif parts[0] == 'rv':
            if self.fs is not None:
                if len(parts) > 2:
                    result = self.fs.copy_rv_file(self.tree, parts[1], parts[2], overwrite)
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'File path\'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                    return '[Error] Couldn\'t load file to the desired path', self.fs.get_abs_path()
                return '[Help] rv &ltfile_path&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Load real folder into drive
        elif parts[0] == 'rvdir':
            if self.fs is not None:
                if len(parts) > 2:
                    result = self.fs.copy_rv_dir(self.tree, parts[1], parts[2], overwrite)
                    if result is not None:
                        xml.obj_to_xml(self.tree) #Save file_system into an XML
                        return 'Folder path\'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                    return '[Error] Couldn\'t load folder to the desired path', self.fs.get_abs_path()
                return '[Help] rvdir &ltdir_path&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Download File
        elif parts[0] == 'vr':
            if self.fs is not None:
                if len(parts) > 2:
                    file = self.fs.find_file(parts[1])
                    result = self.fs.copy_vr_file(file, parts[2])
                    if result is not None:
                        return 'File \'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                    return '[Error] Couldn\'t download file to the desired path', self.fs.get_abs_path()
                return '[Help] vr &ltfile_name&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Download Folder
        elif parts[0] == 'vrdir':
            if self.fs is not None:
                if len(parts) > 2:
                    folder = self.fs.change_dir_abs(parts[1])
                    result = self.fs.copy_vr_dir(folder, parts[2])
                    if result is not None:
                        return 'Folder \'' +parts[1]+'\' copied to: ' + parts[2], self.fs.get_abs_path()
                    return '[Error] Couldn\'t download folder to the desired path', self.fs.get_abs_path()
                return '[Help] vrdir &ltdir_name&gt &ltnew_path&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Share file
        elif parts[0] == 'sh':
            if self.fs is not None:
                if len(parts) > 2:
                    result = self.fs.share_file(parts[1], parts[2], overwrite, self.username)
                    if result is not None:
                        return 'File \''+parts[1]+'\' successfully shared to User \''+ parts[2] +'\'', self.fs.get_abs_path()
                    return '[Error] Couldn\'t share the file to the desired user.', self.fs.get_abs_path()
                return '[Help] sh &ltfile_name&gt &ltself.username&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Share folder
        elif parts[0] == 'shdir':
            if self.fs is not None:
                if len(parts) > 2:
                    result = self.fs.share_folder(parts[1], parts[2], overwrite, self.username)
                    if result is not None:
                        return 'Folder \''+parts[1]+'\' successfully shared to User \''+ parts[2] +'\'', self.fs.get_abs_path()
                    return '[Error] Couldn\'t share the folder to the desired user.', self.fs.get_abs_path()
                return '[Help] shdir &ltdir_name&gt &ltself.username&gt', self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Show the full 'self.tree' of the file system
        elif parts[0] == 'self.tree':
            if self.fs is not None:
                return xml.self.tree(self.tree), self.fs.get_abs_path()
            return '[Error] Drive not loaded.', ''

        # Display all commands
        elif parts[0] == 'help':
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

        else:
            path = ''
            if self.fs is not None:
                path = self.fs.get_abs_path()
            return '[Error] Command not found. Try \'help\'.', path

