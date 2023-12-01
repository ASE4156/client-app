import argparse
from flask import Flask, render_template, request, jsonify
import requests

parser = argparse.ArgumentParser(description='Run Flask app')
parser.add_argument('--api-token', required=False, help='API token for backend server')
args = parser.parse_args()

app = Flask(__name__)
api_token = args.api_token
client_id = -1

@app.route('/')
def home():
    print(api_token)
    return render_template('home.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/prompt')
def prompt():
    return render_template('prompt.html')


@app.route('/prompt-details')
def prompt_details():
    prompt_id = request.args.get('prompt_id')
    print(prompt_id)

    if not prompt_id:
        return jsonify({'error': 'Missing prompt_id parameter'}), 400

    cpp_service_url = "http://localhost:8080/prompt"

    response = requests.get(cpp_service_url, json={'prompt_id': int(prompt_id)})
    print(response)
    print(response.json())
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to communicate with the C++ service'}), response.status_code


@app.route('/submit-prompt', methods=['POST'])
def submit_prompt():
    client_id, client_name = get_client_id()
    form_data = {
        'prompt_name': request.form['promptName'],
        'prompt_description': request.form['promptDescription'],
        'prompt_content': request.form['prompt'],
        'client_id': client_id
    }

    cpp_service_url = "http://localhost:8080/prompt"

    response = requests.post(cpp_service_url, json=form_data)
    print(response.json())
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to communicate with the C++ service'}), 500

@app.route('/get-prompts')
def get_prompts():
    client_id, client_name = get_client_id()
    if not client_id:
        return jsonify({'error': 'Failed to retrieve client ID'}), 500

    cpp_service_url = "http://localhost:8080/prompt/client_id"
    response = requests.get(cpp_service_url, json={'client_id': client_id})

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to communicate with the C++ service'}), response.status_code

@app.route('/api-token')
def token():
    return render_template('token.html', existing_token=api_token)

@app.route('/get-client')
def get_client():
    client_id, client_name = get_client_id()
    if client_id:
        return jsonify({'clientId': client_id, 'clientName': client_name})
    else:
        return jsonify({'error': 'Failed to retrieve client ID'}), 500

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    backend_url = "http://localhost:8080/llm/text/conversation"

    try:
        print(data['text'], data['prompt_id'])
        response = requests.post(backend_url, json={'text': data['text'], 'prompt_id': int(data['prompt_id'])})
        response_data = response.json()
        print(response_data)
        return jsonify(response_data)
    except requests.RequestException as e:
        print(e)
        return jsonify({'response': 'Error communicating with backend service'}), 500

def get_client_id():
    global client_id
    cpp_service_url = "http://localhost:8080/token/getClient"
    print(api_token)
    response = requests.get(cpp_service_url, json={'token': api_token})
    print(response)
    if response.status_code == 200:
        result = response.json()
        print(result)
        client_id = result.get('clientId')
        client_name = result.get('clientName')
        return client_id, client_name
    else:
        print("Error getting client_id: ", response.json())
        return None


if __name__ == '__main__':
    app.run(debug=True)
