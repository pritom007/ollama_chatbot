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

def bg_for_db_response(name, user_query): 
    bg_for_db = f"""
        first send a post request to url 'http://internal-tf-tssqa-qa-dataservice-alb-1974417174.ap-northeast-1.elb.amazonaws.com/' with endpoint: 'api/v1/items/{name}/time/'. 
        make the data for the post request. Data format is:
        ```
            {{
            "from_time": "%Y-%m-%d %H:%M:%S.0000",
            "to_time": "%Y-%m-%d %H:%M:%S.0000"
            }}
        ```
        The headers need 
        ```
            {{
            'Content-Type': 'application/json', 
            'API-Key': "os.getenv('DB_API_KEY')" # always get the api key from environment variable DB_API_KEY
            }}
        ```
        Determine the vaule for `from_time` and `to_time` based on the user query.
        The data should be in list of dictionary format. So read few data first to understand After getting the data you should further process the data 
        and give output based on {user_query}.
        """
    return bg_for_db

def read_data_from_json_response(prompt):
    read_data_from_json = f"""
        Here is the prompt from user:
        {prompt}
        Your task write python code for reading data from `/Users/pritom_binance/Desktop/office/cryptographic_qa/bot/data.json`,
        the data in the file has this format: 
        ```
        [
            {{
            "test_suite": "",
            "error_message": "",
            "project_name": "",
            "execution_time": "0:00:00.196919",
            "when_executed": "YYYY-MM-DD HH:MM:SS.00000",
            "status": "pass/fail/skip/Pass/Fail/Skip",
            "id": 00000000,
            "name": "test_case_name",
            "tags": [
                "tag1",
            ]
            }},
        ]
        ```
        note: you need to convert this `execution_time` to seconds by using this exact python code: 
        ```
        def convert_to_sec(time_str):
            time_parts = time_str.split(':')
            time_parts = reversed(time_parts)
            total_seconds = 0
            for index, part in enumerate(time_parts):
                total_seconds += float(part) * (60 ** index)
            return total_seconds
        ```
        Always compare the data after converting to lower case.
        (make sure to use the exact code above to convert the time to seconds)
        Finally, based on user query and the data format above provide the output
    """
    return read_data_from_json

def create_html_response(prompt):
    create_html = f"""
        Here is the prompt from user:
        {prompt}
        Your task is to create an appropriate inner HTML file with the user prompt. Just give code no extra explanation.
    """
    return create_html