from flask import Flask, render_template, request, jsonify, session
from flask_session import Session  # Import Session
import ollama

app = Flask(__name__)

# Configure server-side session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

@app.route('/')
def home():
    session.clear()  # Clear the session when the chat starts
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['text']

    # Get history from session, or initialize if it doesn't exist
    if 'history' not in session:
        session['history'] = []
    
    # Add the user's message to the history
    session['history'].append({'role': 'user', 'content': user_input})

    # Start the stream with the history
    stream = ollama.chat(model='llama3', stream=True, messages=session['history'])
    
    # The response will be the last message from the bot
    response = ''
    for part in stream:
        response += part['message']['content']
        # Save bot messages to the history as well
        if part['message']['role'] == 'model':
            session['history'].append({'role': 'model', 'content': part['message']['content']})

    # Make sure to modify the session every time you change it
    session.modified = True

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
