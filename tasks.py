import os
from btasks import (
    fetch_data_from_api,
    clone_and_commit,
    run_sql_query,
    scrape_website,
    compress_resize_image,
    transcribe_audio,
    convert_markdown_to_html,
    filter_csv_and_return_json,
)
from llm import extract_email, extract_credit_card, find_similar_comments
from utils import (
    gen,
    format_with_prettier,
    count_wednesdays_from_dates,
    sort_contacts,
    extract_first_lines_from_logs,
    create_markdown_index,
    gold_ticket,
)
import requests
import json
from typing import Dict, Any, Optional


class TaskParser:
    def __init__(self):
        self.AIPROXY_TOKEN = os.environ["AIPROXY_TOKEN"]
        self.AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"
        self.HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.AIPROXY_TOKEN}",
        }

    def parse_task(self, task_description: str) -> Dict[str, Any]:
        """
        Parse the natural language task description using AI Proxy to identify:
        1. The core task type
        2. Required parameters
        3. Input/output file paths
        """
        system_prompt = """You are a task parsing assistant. Analyze the given task description and return a JSON with:
        1. task_type: The main task category
        2. params: Any required parameters
        3. input_file: Input file path if specified
        4. output_file: Output file path if specified.
        
        Example: For "Count the number of Wednesdays in /data/dates.txt and write to /data/wednesdays.txt"
        Return: {
            "task_type": "wednesday",
            "params": {},
            "input_file": "/data/dates.txt",
            "output_file": "/data/wednesdays.txt"
        }"""

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description},
            ],
            "max_tokens": 500,
            "temperature": 0,
        }

        try:
            response = requests.post(
                f"{self.AIPROXY_BASE_URL}/chat/completions",
                headers=self.HEADERS,
                json=data,
            )
            response.raise_for_status()
            result = response.json()
            parsed_response = json.loads(result['choices'][0]['message']['content'])
            return parsed_response
        except Exception as e:
            raise ValueError(f"Failed to parse task: {str(e)}")


def execute_task(task_description: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Enhanced task execution function that uses AI Proxy for task parsing
    """
    # Initialize task parser
    parser = TaskParser()

    try:
        # Parse the task using AI Proxy
        parsed_task = parser.parse_task(task_description)

        # Extract task type and parameters
        task_type = parsed_task["task_type"].lower()
        combined_params = {
            **(params or {}),
            **(parsed_task.get("params", {})),
            "input_file": parsed_task.get("input_file"),
            "output_file": parsed_task.get("output_file"),
        }

        # Map to existing task functions based on parsed task type
        if task_type == "datagen":
            return gen()
        elif task_type == "prettier":
            return format_with_prettier()
        elif task_type == "wednesday":
            return count_wednesdays_from_dates()
        elif task_type == "sort":
            return sort_contacts()
        elif task_type == "logs":
            return extract_first_lines_from_logs()
        elif task_type == "markdown":
            return create_markdown_index()
        elif task_type == "email":
            return extract_email("data/email.txt", "data/email-sender.txt")
        elif task_type == "credit":
            return extract_credit_card("data/credit-card.png", "data/credit-card.txt")
        elif task_type == "similar":
            return find_similar_comments(
                "data/comments.txt", "data/comments-similar.txt"
            )
        elif task_type == "gold":
            return gold_ticket()
        elif task_type == "fetch_api":
            return fetch_data_from_api(
                combined_params["url"], combined_params["output_file"]
            )
        elif task_type == "clone_repo":
            return clone_and_commit(
                combined_params["repo_url"], combined_params["commit_message"]
            )
        elif task_type == "run_sql":
            return run_sql_query(combined_params["db_path"], combined_params["query"])
        elif task_type == "scrape":
            return scrape_website(
                combined_params["url"], combined_params["output_file"]
            )
        elif task_type == "resize_image":
            return compress_resize_image(
                combined_params["input_file"],
                combined_params["output_file"],
                combined_params["width"],
                combined_params["height"],
            )
        elif task_type == "transcribe_audio":
            return transcribe_audio(
                combined_params["input_file"], combined_params["output_file"]
            )
        elif task_type == "convert_markdown":
            return convert_markdown_to_html(
                combined_params["input_file"], combined_params["output_file"]
            )
        elif task_type == "filter_csv":
            return filter_csv_and_return_json(
                combined_params["input_file"],
                combined_params["output_file"],
                combined_params["column"],
                combined_params["value"],
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    except Exception as e:
        raise ValueError(f"Task execution failed: {str(e)}")


# def execute_task(task_description, params=None):
#     """
#     Executes a task based on the description provided.
#     """

#     if "datagen" in task_description.lower():
#         return gen()

#     # Task A2: Format using Prettier
#     elif "prettier" in task_description.lower():
#         return format_with_prettier()

#     # Task A3: Count Wednesdays
#     elif "wednesday" in task_description.lower():
#         return count_wednesdays_from_dates()

#     # Task A4: Sort contacts
#     elif "sort" in task_description.lower():
#         return sort_contacts()

#     # Task A5: Process logs
#     elif "logs" in task_description.lower():
#         return extract_first_lines_from_logs()

#     # Task A6: Create markdown index
#     elif "markdown" in task_description.lower():
#         return create_markdown_index()

#     # Task A7: Extract email address
#     elif "email" in task_description.lower():
#         return extract_email("data/email.txt", "data/email-sender.txt")

#     # Task A8: Extract credit card number
#     elif "credit" in task_description.lower():
#         return extract_credit_card("data/credit-card.png", "data/credit-card.txt")

#     # Task A9: Find similar comments using embeddings
#     elif "similar" in task_description.lower():
#         return find_similar_comments("data/comments.txt", "data/comments-similar.txt")

#     # Task A10: Calculate Gold ticket sales from database
#     elif "gold" in task_description.lower():
#         return gold_ticket()

#     # **New Business Tasks**

#     # Task B3: Fetch data from an API
#     elif "fetch api" in task_description.lower():
#         return fetch_data_from_api(params["url"], params["output_file"])

#     # Task B4: Clone a Git repository and commit changes
#     elif "clone repo" in task_description.lower():
#         return clone_and_commit(params["repo_url"], params["commit_message"])

#     # Task B5: Run an SQL query
#     elif "run sql" in task_description.lower():
#         return run_sql_query(params["db_path"], params["query"])

#     # Task B6: Scrape website data
#     elif "scrape" in task_description.lower():
#         return scrape_website(params["url"], params["output_file"])

#     # Task B7: Compress or resize an image
#     elif "resize image" in task_description.lower():
#         return compress_resize_image(
#             params["input_file"],
#             params["output_file"],
#             params["width"],
#             params["height"],
#         )

#     # Task B8: Transcribe audio from an MP3 file
#     elif "transcribe audio" in task_description.lower():
#         return transcribe_audio(params["input_file"], params["output_file"])

#     # Task B9: Convert Markdown to HTML
#     elif "convert markdown" in task_description.lower():
#         return convert_markdown_to_html(params["input_file"], params["output_file"])

#     # Task B10: Filter CSV and return JSON
#     elif "filter csv" in task_description.lower():
#         return filter_csv_and_return_json(
#             params["input_file"],
#             params["output_file"],
#             params["column"],
#             params["value"],
#         )

#     else:
#         raise ValueError("Unknown task description")
