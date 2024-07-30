def python_or_general_response(user_input):
    python_or_general = f"""
        Here is the prompt from user:
        ```
        {user_input}
        ```
        Your task is to understand if the user prompt is asking for "writing code in python or any code related task or any
        task that can be done by writing python code", 
        if so then you should output only in `True` or `False`.
    """
    return python_or_general

def generate_graph_response(user_input):
    graph_or_normal = f"""
        Here is the user prompt:
        ```
        {user_input}
        ```
        Your task is to determine if the user prompt includes words that are only closely related to `graph/plot/histogram/bar chart` etc.,
        Output in `True` or `False`. 
    """
    return graph_or_normal

def create_html_response(prompt):
    create_html = f"""
        Here is the prompt from user:
        {prompt}
        Your task is to create an appropriate inner HTML file with the user prompt. Just give code no extra explanation.
    """
    return create_html