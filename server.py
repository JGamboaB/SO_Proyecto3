#pip install flask
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']
    result = run_command(command)
    return result

def run_command(command):
    if command == 'print':
        return 'This is an echo.'
    elif command == 'hello':
        return 'Hello, world!'
    else:
        return 'Command not found.'

if __name__ == '__main__':
    app.run(debug=True)
