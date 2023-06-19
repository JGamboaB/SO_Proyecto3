import userclass as u
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

users = {}
@app.route('/')
def index():
    return render_template('terminal.html', username='Proyecto')

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']
    result, updated_path = run_command(command)
    return jsonify(result=result, path=updated_path)

def run_command(command):
    parts = command.split()
    overwrite = parts[-1] == '-o'
    # Help
    if parts[0] == 'help':
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
                ''', ''
    # Login
    elif parts[0] == 'login':
        if len(parts) > 1:
            username = parts[1]
            if username in users:
                return '[Error] User is already logged in.', ''
            users[username] = u.User(username)
            return 'Username set to ' + username, ''
        else:
            return '[Error] Please provide a username.', ''

    # Logout
    elif parts[0] == 'logout':
        if len(parts) > 1 and parts[1] in users:
            user = users[parts[1]]
            del users[parts[1]]
            return user.logout(), ''
        else:
            return '[Error] Invalid username.', ''
    else:
        username = parts[1]
        if username not in users:
            return '[Error] User is not logged in.', ''

        user = users[username]
        return user.terminal(parts, overwrite)


if __name__ == '__main__':
    app.run(debug=True)
