import xml.etree.ElementTree as ET
import os
import sys
import datetime

class File:
    def __init__(self, name, contents, creation_date, mod_date, size=0):
        self.name = name
        self.contents = contents
        self.creation_date = creation_date
        self.mod_date = mod_date
        self.size = size
    
    def stats(self):
        return ("Name and Extension: " + self.name + "\nCreation Date: " + self.creation_date + "\nModified Date: " + self.mod_date + "\nSize: " + str(self.size))

    def read(self):
        return self.contents
    
    def update(self, fs, content):
        space_left = remaining_space(fs) + int(self.size)
        if len(content) > space_left: #No space left
            return 

        self.contents = content
        self.mod_date = str(datetime.datetime.now())
        self.size = str(len(content))
        return self


class Folder:
    def __init__(self, name, parent=None, files=None, folders=None):
        self.name = name
        self.parent = parent
        self.files = files if files is not None else []
        self.folders = folders if folders is not None else []

    def list_dir(self):
        result = ''
        for file in self.files:
            result += ("  File: " + file.name + " \tCreation Date: " + file.creation_date + " \tModified Date: " + file.mod_date + " \tSize: " + str(file.size) + "\n")
        for folder in self.folders:
            result += ("  Folder: " + folder.name + "\n")
        return result

    def change_dir(self, f_name):      
        for folder in self.folders:
            if folder.name == f_name:
                return folder
        return None

    def change_dir_abs(self, absolute_path):
        path_components = absolute_path.split('/')
        current_folder = self

        for component in path_components:
            if component == "" or component == ".":
                continue  # Ignore empty components
            elif component == "..":
                current_folder = current_folder.parent
            else:
                current_folder = current_folder.change_dir(component)
                if current_folder is None:
                    return None  # Path not found, return None
                
        return current_folder
    
    def get_abs_path(self):
        path_components = []
        current_folder = self

        while current_folder is not None:
            path_components.insert(0, current_folder.name)
            current_folder = current_folder.parent

        absolute_path = "/" + "/".join(path_components)
        return absolute_path
    
    def find_file(self, file_name):
        for file in self.files:
            if file.name == file_name:
                return file
        return None
    
    def move_file(self, file_name, path):
        dest_dir = self.change_dir_abs(path)
        file = self.find_file(file_name)

        if dest_dir is not None and file is not None:

            for file_ in dest_dir.files:
                if file_.name == file_name: #File already exists
                    dest_dir.overwrite_file()

            dest_dir.files.append(file)
            self.files.remove(file)
            return 1
        return None

    def find_dir(self, f_name):
        for folder in self.folders:
            if folder.name == f_name:
                return folder
        return None

    def move_dir(self, dir_name, path):
        dest_dir = self.change_dir_abs(path)
        dir = self.find_dir(dir_name)

        if dest_dir is not None and dir is not None:

            for dir_ in dest_dir.folders:
                if dir_.name == dir_name: #File already exists
                    dest_dir.overwrite_folder()

            dest_dir.folders.append(dir)
            self.folders.remove(dir)
            return 1
        return None

    def overwrite_folder(self): #Ask if you want to overwrite
        pass

    def create_folder(self, name):
        for folder in self.folders:
            if folder.name == name: #Folder already exists
                self.overwrite_folder()
            
        new_folder = Folder(name, parent=self)
        self.folders.append(new_folder)
        return new_folder
    
    def overwrite_file(self): #Ask if you want to overwrite
        pass
    
    def create_file(self, fs, name, content): #Name contains the extension
        for file in self.files:
            if file.name == name: #File already exists
                self.overwrite_file()

        space_left = remaining_space(fs)
        if len(content) > space_left: #No space left
            return 

        ct = datetime.datetime.now() #Current Time
        new_file = File(name, content, str(ct), str(ct))
        size = len(content)
        new_file.size = str(size)

        self.files.append(new_file)
        return new_file
    
    def delete_file(self, file_name):
        for file in self.files:
            if file.name == file_name:
                self.files.remove(file)
                del file
    
    def delete_files(self):
        for file in self.files:
            self.files.remove(file)
            del file

    def delete_folders(self):
        for folder in self.folders:
            folder.delete_files()
            folder.delete_folders()
            self.folders.remove(folder)
            del folder

    def delete_folder(self, folder_name):
        for folder in self.folders:
            if folder.name == folder_name:
                folder.delete_files()
                folder.delete_folders()
                self.folders.remove(folder)
                del folder

    def size_of_dir(self, size=0):
        for file in self.files:
            size += int(file.size)
        for folder in self.folders:
            size += folder.size_of_dir()
        return size
    
    def copy_vv_file(self, fs, file_name, path):
        dest_dir = self.change_dir_abs(path)
        file = self.find_file(file_name)

        if dest_dir is not None and file is not None:

            for file_ in dest_dir.files:
                if file_.name == file_name: #File already exists
                    dest_dir.overwrite_file()

            space_left = remaining_space(fs)
            if int(file.size) > space_left: #No space left
                return 

            ct = datetime.datetime.now() #Current Time
            new_file = File(file.name, file.contents, str(ct), str(ct), file.size)
            dest_dir.files.append(new_file)
            return new_file

    def copy_vv_dir(self, fs, dir_name, path):
        dest_dir = self.change_dir_abs(path)
        dir = self.find_dir(dir_name)

        if dest_dir is not None and dir is not None:

            for dir_ in dest_dir.folders:
                if dir_.name == dir_name: #File already exists
                    dest_dir.overwrite_folder()

            #Size of all the files <= remaining space
            if dir.size_of_dir() > remaining_space(fs): #No space left
                return 

            dest_dir.folders.append(dir) #XML is disconnected and reconnected, so it actually copies the files
            return dir

    def copy_vr_file(self, file, path):
        if file is not None:
            destination_file_path = os.path.join(path, file.name)

            try:
                with open(destination_file_path, 'w') as destination_file:
                    destination_file.write(file.contents)

                print(f"File '{file.name}' copied to '{destination_file_path}' successfully.")
                return file
            except FileNotFoundError:
                print('FileNotFound')
                return None
        print('File is None')
        return None
    
    def copy_vr_dir(self, folder, path):
        destination_folder_path = os.path.join(path, folder.name)

        try:
            os.makedirs(destination_folder_path, exist_ok=True)
        except FileExistsError:
            return 
        except PermissionError:
            return
        
        for file in folder.files:
            destination_file_path = os.path.join(destination_folder_path, file.name)

            try:
                with open(destination_file_path, 'w') as destination_file:
                    destination_file.write(file.contents)

                print(f"File '{file.name}' copied to '{destination_file_path}' successfully.")
            except FileNotFoundError:
                print(f"Destination directory '{destination_folder_path}' not found.")

        for subfolder in folder.folders:
            copied_folder = self.copy_vr_dir(subfolder, destination_folder_path)
            
            if copied_folder is None:
                return
            
        return 'Works'
    
    def copy_rv_file(self, fs, file_path, path):
        file_name = os.path.basename(file_path)
        dir = self.change_dir_abs(path)
        if dir is None:
            return None

        if os.path.exists(file_path):
            with open(file_path, 'r') as source_file:
                file_contents = source_file.read()  
            
            new_file = dir.create_file(fs, file_name, file_contents)

            print(f"File '{file_name}' copied to XML path '{path}' successfully.")
            return new_file
        else:
            print(f"Source file '{file_path}' does not exist.")
            return None
    
    def traverse_folder(self, fs, current_dir, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                with open(item_path, "r") as file:
                    contents = file.read()
                current_dir.create_file(fs, item, contents)
            elif os.path.isdir(item_path):
                i = current_dir.create_folder(item)
                current_dir.traverse_folder(fs, i, item_path)
    
    def copy_rv_dir(self, fs, dir_path, path):
        base_folder = self.change_dir_abs(path)
        if base_folder is None:
            return None
        
        if os.path.isdir(dir_path):
            folder_name = os.path.basename(dir_path)
            new_folder = base_folder.create_folder(folder_name)

            self.traverse_folder(fs, new_folder, dir_path)

            return new_folder
        return
    
    def share_file(self, file_name, username):
        file = self.find_file(file_name)
        if file is None:
            return

        xml_path = username + ".xml"
        try:
            fs2 = xml_to_obj(xml_path)
            shared_folder = fs2.change_dir_abs('shared')
            if shared_folder is None:
                shared_folder = fs2.create_folder('shared')

            shared_folder.create_file(fs2, file.name, file.contents)
            obj_to_xml(fs2) #Save changes made
            return 'File \''+file.name+'\' successfully shared to User \''+ username +'\''
        except FileNotFoundError: #Drive not found
            return 

    def share_folder(self, dir_name, username):
        dir = self.find_dir(dir_name)
        if dir is None:
            return
        
        xml_path = username + ".xml"
        try:
            fs2 = xml_to_obj(xml_path)
            shared_folder = fs2.change_dir_abs('shared')
            if shared_folder is None:
                shared_folder = fs2.create_folder('shared')

            for folder in shared_folder.folders: 
                if folder.name == dir_name:
                    shared_folder.overwrite_file() #File already exists

            if dir.size_of_dir() > remaining_space(fs2): #Not enough space to share
                return
            
            shared_folder.folders.append(dir) #Shares the folder as it is
            obj_to_xml(fs2) #Save changes made
            return dir
        except FileNotFoundError:
            return


def obj_to_xml(file_system):
    def create_folder(folder, first=False):
        if not first:
            folder_element = ET.Element('Folder', {'name': folder.name})
        else:
            folder_element = ET.Element('Folder', {'name': folder.name, 'size': file_system.size})

        for file in folder.files:
            file_element = ET.SubElement(folder_element, 'File', {
                'name': file.name,
                'contents': file.contents,
                'creation_date': file.creation_date,
                'mod_date': file.mod_date,
                'size': file.size
            })

        for subfolder in folder.folders:
            subfolder_element = create_folder(subfolder)
            folder_element.append(subfolder_element)

        return folder_element

    root_element = create_folder(file_system, True)
    xml_tree = ET.ElementTree(root_element)
    xml_tree.write(file_system.name + ".xml", encoding='utf-8', xml_declaration=True)


def xml_to_obj(path):
    def parse_folder(xml_element, parent=None):
        name = xml_element.attrib['name']
        folder = Folder(name, parent=parent)

        for child in xml_element:
            if child.tag == "Folder":
                subfolder = parse_folder(child, folder)
                folder.folders.append(subfolder)
            elif child.tag == "File":
                file = parse_file(child)
                folder.files.append(file)

        return folder

    def parse_file(xml_element):
        name = xml_element.attrib['name']
        contents = xml_element.attrib['contents']
        creation_date = xml_element.attrib['creation_date']
        mod_date = xml_element.attrib['mod_date']
        size = xml_element.attrib['size']

        file = File(name, contents, creation_date, mod_date, size)
        return file
    
    with open(path, 'r') as file:
        xml_contents = file.read()
    
    root = ET.fromstring(xml_contents)
    username = root.attrib['name']
    size = root.attrib['size']

    fs = Folder(username)

    for child in root:
        if child.tag == "Folder":
            folder = parse_folder(child, fs)
            fs.folders.append(folder)
        elif child.tag == "File":
            file = parse_file(child)
            fs.files.append(file)

    fs.name = username
    fs.username = username
    fs.size = size

    return fs

def print_fs(node, indent=""):
    print(indent + "Folder: " + node.name)
    for file in node.files:
        print(indent + "  File: " + file.name + " - Contents: " + file.contents + " - Creation Date: " + file.creation_date + " - Modified Date: " + file.mod_date + " - Size: " + file.size)
    for folder in node.folders:
        print_fs(folder, indent + "  ")

def tree_aux(node, indent=""):
    output = ""
    output += indent + "└ Folder: " + node.name + "\n"
    for file in node.files:
        output += indent + "  └ File: " + file.name + " - Creation Date: " + file.creation_date + " - Modified Date: " + file.mod_date + " - Size: " + str(file.size) + "B\n"
    for folder in node.folders:
        output += tree_aux(folder, indent + "  ")
    return output

def tree(node):
    return "Total Space: " + str(node.size) + "B - Free Space: " + str(remaining_space(node)) + "B\n\n" + tree_aux(node)

def remaining_space_aux(node, size):
    for file in node.files:
        size -= int(file.size)
    for folder in node.folders:
        size = remaining_space_aux(folder, size)
    return size

def remaining_space(fs):
    return remaining_space_aux(fs, int(fs.size))

def create_drive(username, size):
    fs = Folder(username)
    root = Folder('root', parent=fs)
    shared = Folder('shared', parent=fs)

    fs.folders.append(root)
    fs.folders.append(shared)
    
    fs.name = username
    fs.username = username
    fs.size = str(size)

    return fs
