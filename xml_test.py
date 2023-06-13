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
    
    def print_attr(self):
        print("Name and Extension: " + self.name + "\nCreation Date: " + self.creation_date + "\nModified Date: " + self.mod_date + "\nSize: " + str(self.size) + "\n--------------------------------Content--------------------------------\n"+self.contents)

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
        for file in self.files:
            print("  File: " + file.name + " - Creation Date: " + file.creation_date + " - Modified Date: " + file.mod_date + " - Size: " + str(file.size))
        for folder in self.folders:
            print("  Folder: " + folder.name)

    def change_dir(self, f_name):
        if f_name == "..":
            return self.parent
        
        for folder in self.folders:
            if folder.name == f_name:
                return folder
        
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
    
    def move_file(self, file_name):
        pass



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


def xml_to_obj(xml_string):
    def parse_folder(xml_element):
        name = xml_element.attrib['name']
        folder = Folder(name)

        for child in xml_element:
            if child.tag == "Folder":
                subfolder = parse_folder(child)
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
    
    root = ET.fromstring(xml_string)
    username = root.attrib['username']
    size = root.attrib['size']

    fs = Folder(username)

    for child in root:
        if child.tag == "Folder":
            folder = parse_folder(child)
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

def create_drive(username, size):
    fs = Folder(username)
    root = Folder('Root', parent=fs)
    shared = Folder('Shared', parent=fs)

    fs.folders.append(root)
    fs.folders.append(shared)
    
    fs.name = username
    fs.username = username
    fs.size = str(size)

    return fs



# / / / / / / / / / / / / / / / / /  Example usage
xml_data = '''
<FileSystem username="JohnDoe" size="1024GB">
  <Folder name="Root">
    <File name="file1.txt" contents="Lorem ipsum dolor sit amet." creation_date="2022-01-15" mod_date="2022-02-20" size="256KB" />
    <File name="file2.txt" contents="Sed ut perspiciatis unde omnis iste natus error." creation_date="2022-03-10" mod_date="2022-04-25" size="512KB" />
    <Folder name="Subfolder">
      <File name="file3.txt" contents="Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit." creation_date="2022-05-01" mod_date="2022-06-15" size="128KB" />
    </Folder>
  </Folder>
  <Folder name="Shared">
    <File name="file4.txt" contents="Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." creation_date="2022-07-20" mod_date="2022-08-30" size="64KB" />
    <Folder name="Subfolder">
      <File name="file5.txt" contents="Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam." creation_date="2022-09-10" mod_date="2022-10-18" size="32KB" />
    </Folder>
  </Folder>
</FileSystem>
'''

fs = xml_to_obj(xml_data)
print_fs(fs)
obj_to_xml(fs)