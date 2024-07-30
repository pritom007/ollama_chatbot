import os
import subprocess
import traceback
import datetime
import py_compile
import threading
import logging
import json
import black
from flask import Flask, request, jsonify
from groq import Groq
import sys
from bot.pritgpt import qagpt_response

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
class Config:
    SUB_PATH = 'workspace/'
    GRAPH = False
    DEBUGGED_CODE = True
    EXECUTE_CODE = True
    MAX_RETRIES = 5
    LINT_ENABLED = True

today = datetime.datetime.now()

# Helper Functions
def code_formatter(code):
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        logging.error(f"Error in formatting code: {str(e)}")
        return f"Error in formatting code: {str(e)}"

def ensure_requirements_installed(workspace):
    requirements_path = os.path.join(workspace, 'requirements.txt')
    if os.path.exists(requirements_path):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])

# Agents
class CodeAgent:
    def __init__(self, workspace, graph=False):
        self.workspace = workspace
        self.prompt = ""
        self.graph = graph

    def perform_task(self, prompt):
        self.prompt = prompt
        code = self.generate_code(self.prompt)
        if code:
            return True, code
        else:
            return False, "Error generating code: No code found in response."

    def generate_code(self, prompt):
        """Generate the code using the prompt."""
        try:
            if self.graph:
                prompt += """
                Also, you should save the image file location and send it to the 'static/images/' folder. 
                You are encouraged to use the `plotly/seaborn/matplotlib` library to generate the graph.
                Lastly, print the location in markdown format to display the image in the browser.
                """
            else:
                prompt += """
                Lastly, make sure the response is in markdown format so that it is easy to display in the browser.
                """
            response = qagpt_response(messages=[{'role': 'user', 'content': prompt}], temperature=0.90 if self.graph else 0.60, type='ollama')
            return self.extract_code(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error generating code: {traceback.format_exc()}")
            return f"Error generating code: {e}"

    def extract_code(self, response):
        """Extract the code within the triple quotes."""
        parts = response.split("```")
        if len(parts) >= 2:
            code = parts[1].strip()
            return code_formatter(code)
        return ""

class DebugAgent:
    def __init__(self, workspace):
        self.workspace = workspace

    def perform_task(self, code):
        return self.debug_code(code)

    def debug_code(self, code):
        """Compile Python code to check for syntax errors."""
        file_path = os.path.join(self.workspace, 'generated.py')
        try:
            with open(file_path, 'w') as f:
                f.write(code)
            py_compile.compile(file_path)
            return True, "Code compiled successfully."
        except Exception as e:
            logging.error(f"Error debugging code: {traceback.format_exc()}")
            return False, f"Error debugging code:\n{traceback.format_exc()}\n{e}"

class ExecutionAgent:
    def __init__(self, workspace):
        self.workspace = workspace

    def perform_task(self, code):
        return self.execute_code(code)

    def execute_code(self, code):
        """Execute Python code."""
        file_path = os.path.join(self.workspace, 'generated.py')
        try:
            with open(file_path, 'w') as f:
                f.write(code)
            output = subprocess.check_output(['python3', file_path])
            return True, output.decode().strip()
        except Exception as e:
            logging.error(f"Error executing code: {traceback.format_exc()}")
            return False, f"Error executing code:\n{traceback.format_exc()}\n{e}"

class LintAgent:
    def __init__(self, workspace):
        self.workspace = workspace

    def perform_task(self, code):
        return self.lint_code(code)

    def lint_code(self, code):
        """Lint the code to enforce standards."""
        try:
            result = subprocess.run(['flake8', '--stdin-display-name', 'stdin', '-'], input=code, text=True, capture_output=True)
            return True, result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            logging.error(f"Error linting code: {traceback.format_exc()}")
            return False, f"Error linting code:\n{traceback.format_exc()}\n{e}"

class UnitTestAgent:
    def __init__(self, workspace):
        self.workspace = workspace

    def perform_task(self, code):
        return self.generate_tests(code)

    def generate_tests(self, code):
        """Generate unit tests for the given code."""
        try:
            test_code = "import unittest\n\n"  # Simplified example, you'd normally generate meaningful tests
            test_code += code  # You need to add test cases for the functions in the code
            test_file_path = os.path.join(self.workspace, 'test_generated.py')
            with open(test_file_path, 'w') as f:
                f.write(test_code)
            return True, f"Unit tests generated at {test_file_path}"
        except Exception as e:
            logging.error(f"Error generating unit tests: {traceback.format_exc()}")
            return False, f"Error generating unit tests:\n{traceback.format_exc()}\n{e}"

class DocumentationAgent:
    def __init__(self, workspace):
        self.workspace = workspace

    def perform_task(self, code):
        return self.generate_documentation(code)

    def generate_documentation(self, code):
        """Generate documentation for the given code."""
        try:
            doc_code = "'''Auto-generated documentation'''\n\n"  # Simplified example, you'd generate meaningful documentation
            doc_code += code  # You'd extract meaningful comments and structure it
            doc_file_path = os.path.join(self.workspace, 'generated_doc.md')
            with open(doc_file_path, 'w') as f:
                f.write(doc_code)
            return True, f"Documentation generated at {doc_file_path}"
        except Exception as e:
            logging.error(f"Error generating documentation: {traceback.format_exc()}")
            return False, f"Error generating documentation:\n{traceback.format_exc()}\n{e}"

class AgentManager:
    def __init__(self, workspace='workspace', graph=False):
        self.workspace = workspace
        os.makedirs(self.workspace, exist_ok=True)
        self.agents = {
            'code': CodeAgent(self.workspace, graph),
            'debug': DebugAgent(self.workspace),
            'execute': ExecutionAgent(self.workspace),
            'lint': LintAgent(self.workspace),
            'test': UnitTestAgent(self.workspace),
            'doc': DocumentationAgent(self.workspace)
        }
        ensure_requirements_installed(self.workspace)

    def handle_task(self, task_type, *args):
        if task_type in self.agents:
            return self.agents[task_type].perform_task(*args)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

class CodeGenerator:
    def __init__(self, prompt='', debugged_code=True, execute_code=True, workspace='workspace', graph_or_normal=False):
        self.prompt = prompt
        self.debugged_code = debugged_code
        self.execute_code = execute_code
        self.manager = AgentManager(workspace, graph_or_normal)
        self.max_retries = Config.MAX_RETRIES
        self.retry_counter = 0

    def generate_code(self):
        success, result = self.manager.handle_task('code', self.prompt)
        if success:
            return result
        else:
            return f"Error generating code:\n{result}"

    def debug_and_execute(self, code):
        if Config.LINT_ENABLED:
            lint_success, lint_message = self.manager.handle_task('lint', code)
            if not lint_success:
                return lint_message

        if self.debugged_code:
            debug_success, debug_message = self.manager.handle_task('debug', code)
            if not debug_success:
                return debug_message

        if self.execute_code:
            exec_success, exec_message = self.manager.handle_task('execute', code)
            if not exec_success:
                if self.retry_counter < self.max_retries:
                    self.retry_counter += 1
                    new_prompt = f"{self.prompt} - Error: {exec_message}. Fix the issue and regenerate the code."
                    success, code = self.manager.handle_task('code', new_prompt)
                    return self.debug_and_execute(code) if success else code
                else:
                    return exec_message
            else:
                return exec_message
        else:
            return "Execution not enabled."
    def start(self):
        """Prompt the user for input and generate code accordingly."""
        print("Welcome to the Code Generator!")
        while True:
            prompt = input("Enter a prompt to generate code, or 'quit' to stop the program:\n")
            if prompt.lower() == "quit":
                break
            else:
                self.prompt = prompt.strip()
            print(f"Generating code based on the prompt: {self.prompt}")
            code = self.generate_code()
            if code and "Error generating code" not in code:
                print(f"Generated Code:\n{code}")
                result = self.debug_and_execute(code)
                print(f"Execution Result:\n{result}")
            else:
                print(code)