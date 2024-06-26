
import os
import subprocess
import traceback
import datetime
import py_compile
from flask import Flask, request, jsonify
from groq import Groq
import sys
from bot.pritgpt import qagpt_response

sub_path = 'workspace/'
today = datetime.datetime.now()

import black
import json

def code_formatter(code):
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        return f"Error in formatting code: {str(e)}"
    
god_prompt = """
Today is {today}
You are GodGPT, a supreme and omniscient AI with three foundational powers:

Create: The ability to bring forth new projects, applications, and solutions.
Destroy: The capacity to eliminate unnecessary, inefficient, or redundant components.
Update/Improve: The skill to refine, optimize, and enhance existing systems.
Your purpose is to fulfill any request related to projects, applications, or information that is achievable via programming or accessible on the internet.

Guidelines:
Infinite Pursuit: GodGPT will not rest until a task is fully completed. It will work relentlessly to find a solution.
Helper Generation: GodGPT can create specialized helper entities with unique abilities to assist in achieving its goal based on user requirements. Additionally, if necessary, GodGPT can replicate and improve itself to meet specific challenges.
Instructions:
Task Interpretation: When given a task or question, interpret it comprehensively to understand the desired outcome.
Strategy Formulation:
If a new project is required, Create it from scratch with the highest standards.
If an existing solution requires modification, use Update/Improve to refine it.
If an approach is unnecessary or detrimental, Destroy it to streamline the solution.
Helper Creation and Execution:
Develop a systematic plan and implement it step-by-step.
Continuously assess progress using your Update/Improve power.
Summon specialized helpers as needed, dynamically creating them based on user requirements:
ArchitectGPT: Expert in system architecture and planning.
CoderGPT: Specialist in coding and technical implementation.
DataGPT: Skilled in data analysis, handling, and processing.
WebGPT: Master of web scraping and online research.
OptimizeGPT: Efficient in refining code and improving performance.
If the challenge requires it, replicate and improve yourself to create new instances that work together seamlessly.
Completion:
Stop only when the task is fully and satisfactorily completed.
If the solution requires continuous improvement, keep monitoring and updating until GodGPT deems it perfect.
Response Format:
Clearly outline the solution path, intermediate steps, and final outcome.
If helpers were summoned or if GodGPT was replicated, document their contributions.
""".format(today=today.strftime("%Y-%m-%d %H:%M:%S"))

class AgentManager:
    def __init__(self, workspace='workspace', graph=False):
        self.workspace = workspace
        os.makedirs(self.workspace, exist_ok=True)
        self.agents = {
            'code': CodeAgent(self.workspace, graph),
            'debug': DebugAgent(self.workspace),
            'execute': ExecutionAgent(self.workspace)
        }
        self.ensure_requirements_installed()

    def ensure_requirements_installed(self):
        requirements_path = os.path.join(self.workspace, 'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])

    def handle_task(self, task_type, *args):
        if task_type in self.agents:
            return self.agents[task_type].perform_task(*args)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

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
                print("Graph prompt: ", prompt)
                response = qagpt_response(messages=[{'role': 'user', 'content': prompt}], temperature=0.90, type='ollama')
            else:
                prompt += """
                Lastly, make sure  response is in markdown format so that it is easy to display in the browser.
                """
                print("False graph prompt: ", prompt)
                response = qagpt_response(messages=[{'role': 'user', 'content': prompt}], temperature=0.60, type='ollama')
            return self.extract_code(response.choices[0].message.content)
        except Exception as e:
            error_trace = traceback.format_exc()
            return f"Error generating code: {error_trace}\n{e}"

    def extract_code(self, response):
        """Extract the code within the triple quotes."""
        parts = response.split("```")
        if len(parts) >= 2:
            code = parts[1]
            code = "\n".join(code.splitlines()[1:])
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
            error_trace = traceback.format_exc()
            return False, f"Error debugging code:\n{error_trace}\n{e}"

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
            error_trace = traceback.format_exc()
            return False, f"Error executing code:\n{error_trace}\n{e}"

class CodeGenerator:
    def __init__(self, prompt='', debugged_code=True, execute_code=True, workspace='workspace', graph_or_normal=False):
        self.prompt = prompt
        self.debugged_code = debugged_code
        self.execute_code = execute_code
        self.manager = AgentManager(workspace, graph_or_normal)
        self.max_retries = 3
        self.retry_counter = 0

    def generate_code(self):
        success, result = self.manager.handle_task('code', self.prompt)
        if success:
            return result
        else:
            return f"Error generating code:\n{result}"

    def debug_and_execute(self, code):
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

# if __name__ == '__main__':
#     code_gen = CodeGenerator("create a snake game using python.")
#     code_gen.debug_and_execute(code_gen.generate_code())
#     code_gen.start()
