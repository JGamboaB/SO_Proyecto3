import xml.etree.ElementTree as ET
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
    
    def update(self, content):
        self.contents = content
        self.mod_date = str(datetime.datetime.now())
        self.size = sys.getsizeof(self)


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

    def copy_vv_file(self, file_name, path):
        dest_dir = self.change_dir_abs(path)
        file = self.find_file(file_name)

        if dest_dir is not None and file is not None:

            for file_ in dest_dir.files:
                if file_.name == file_name: #File already exists
                    dest_dir.overwrite_file()

            dest_dir.files.append(file)

    def copy_vv_dir(self, dir_name, path):
        dest_dir = self.change_dir_abs(path)
        dir = self.find_dir(dir_name)

        if dest_dir is not None and dir is not None:

            for dir_ in dest_dir.folders:
                if dir_.name == dir_name: #File already exists
                    dest_dir.overwrite_folder()

            dest_dir.folders.append(dir)

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
    
    def create_file(self, name, content): #Name contains the extension
        for file in self.files:
            if file.name == name: #File already exists
                self.overwrite_file()

        ct = datetime.datetime.now() #Current Time
        new_file = File(name, content, str(ct), str(ct))
        size = sys.getsizeof(new_file)
        new_file.size = size

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
    username = root.attrib['username']
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
        print(indent + "  File: " + file.name + " - Contents: " + file.contents + " - Creation Date: " + file.creation_date + " - Modified Date: " + file.mod_date + " - Size: " + str(file.size))
    for folder in node.folders:
        print_fs(folder, indent + "  ")

def tree(node, indent=""):
    output = ""
    output += indent + "└ Folder: " + node.name + "\n"
    for file in node.files:
        output += indent + "  └ File: " + file.name + " - Contents: " + file.contents + " - Creation Date: " + file.creation_date + " - Modified Date: " + file.mod_date + " - Size: " + str(file.size) + "\n"
    for folder in node.folders:
        output += tree(folder, indent + "  ")
    return output


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
