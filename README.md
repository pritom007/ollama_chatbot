# Flask Ollama Chatbot

This project is a web-based chat application powered by the Ollama model. It's built using Flask, a lightweight WSGI web application framework in Python. The app is designed to handle conversations, maintain context, and integrate with external data sources for enriched interaction capabilities.

## Features

- Real-time chatting experience with contextual memory.
- New chat session initiation from the UI.
- Chat session history display on the sidebar.
- Integration with external data sources like databases and file systems for dynamic responses.
- Markdown rendering for rich text responses.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What you need to install the software:

- Python 3.6+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository to your local machine:

   ```sh
   git clone https://github.com/pritom007/ollama_chatbot.git

2. Navigate to the cloned directory:

   ```bash
   cd ollama_chatbot

3. Create a virtual environment:

    ```bash
    python -m venv venv

4. Activate the virtual environment:

    - On Mac/Linux env:

    ```bash
    source venv/bin/activate

    - On Windows:

    ```bash
    .\venv\Scripts\activate


5. Install the required packages:

    ```bash
    pip install -r requirements.txt

6. Start the Flask application:

    ```bash
    flask run
    ```
    Or with Python directly:

    ```bash
    python3 app.py
    ```

### Usage

Open your web browser and navigate to http://127.0.0.1:5000/ to start chatting with the Ollama chatbot.
    
To initiate a new chat session, click the "New Chat" button.

Click on a chat session in the sidebar to view its history.

### Built With
    
#### Flask - The web framework used
    
#### Ollama - OpenAI's model library for chatbot functionality
    
#### HTML/CSS/JS - Frontend technologies

### Contributing
    
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

### Authors
    
Your Name - Initial work - YourUsername    

See also the list of contributors who participated in this project.


