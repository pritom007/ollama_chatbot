from flask import Flask, render_template, request, jsonify, session
from flask_session import Session  # Import Session
from bot import pritgpt, prompt
from bot.code_generator import CodeGenerator
from bot.pritgpt import qagpt_response

import datetime

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
    response = chatbot_db_query_process(user_input)
    return jsonify({'response': response})

def chatbot_db_query_process(user_input):
    python_or_gen = prompt.python_or_general_response(user_input)
    add_to_session_history('user', user_input)
    response = qagpt_response([{'role': 'user', 'content': python_or_gen}], model='llama3-8b-8192', type='ollama', temperature=0.90)
    if 'true' in response.choices[0].message.content.lower():
        print("In true case: "+response.choices[0].message.content.lower())
        code = CodeGenerator(prompt=user_input)
        gen_code = code.generate_code()
        final_response = code.debug_and_execute(gen_code)
        return final_response
    else:
        print("In false case with db enabled: "+response.choices[0].message.content.lower())
        print("session history:", session['history'][-10:])
        # normal action
        response = qagpt_response(session['history'][-10:], model='llama3-8b-8192', type='ollama', temperature=0.50)
        add_to_session_history('assistant', response.choices[0].message.content)
        final_response = response.choices[0].message.content

        return final_response
    
def add_to_session_history(role, content):
    """Add a message to the session history."""
    if 'history' not in session:
        session['history'] = [{'role': 'system', 'content': f'Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}! Always think before you answer.'}]
    session['history'].append({'role': role, 'content': content})
    session.modified = True

if __name__ == '__main__':
    app.run(debug=True)
