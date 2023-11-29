import argparse
from flask import Flask, render_template

parser = argparse.ArgumentParser(description='Run Flask app')
parser.add_argument('--api-token', required=False, help='API token for backend server')
args = parser.parse_args()

app = Flask(__name__)
api_token = args.api_token

@app.route('/')
def home():
    print(api_token)
    return render_template('home.html')

@app.route('/create')
def prompt():
    return render_template('create.html')

@app.route('/negotiator')
def negotiator():
    return render_template('prompt.html')

@app.route('/api-token')
def token():
    return render_template('token.html', existing_token=api_token)

if __name__ == '__main__':
    app.run(debug=True)
