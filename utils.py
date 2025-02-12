import pandas as pd
from datetime import datetime
import os
import glob
import json
import sqlite3
import subprocess


import subprocess
import os


def gen():
    # Ensure we're in the correct working directory
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data')

    # Run the subprocess
    result = subprocess.run(
        [
            "uv",
            "run",
            "datagen.py",
            "22f2000644@ds.study.iitm.ac.in",
            "--root",
            data_dir,
        ],
        capture_output=True,
        text=True,
    )

    # Check if the process was successful
    if result.returncode == 0:
        print("Process ran successfully")
        print(result.stdout)  # Optionally print output
    else:
        print(f"Process failed with return code {result.returncode}")
        print(result.stderr)  # Optionally print error output
    return "data created"


def format_with_prettier():
    try:
        file_path = 'data/format.md'

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")

        # Run Prettier on the file
        result = subprocess.run(
            ["npx", "prettier", "--write", file_path],
            check=True,
            capture_output=True,
            text=True,
        )

        # Return success message
        return f"File {file_path} formatted successfully."

    except subprocess.CalledProcessError as e:
        print(f"Prettier command failed: {e.stderr}")
        return None

    except FileNotFoundError as e:
        print(str(e))
        return None


def count_wednesdays_from_dates():
    file_path = "data/dates.txt"
    with open(file_path, "r") as file:
        dates = file.read().splitlines()

    date_formats = [
        "%d-%b-%Y",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
        "%b %d, %Y",
        "%d-%b-%Y",
    ]
    wc = 0
    for date_str in dates:
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                if date_obj.weekday() == 2:
                    wc += 1
                break
            except ValueError:
                continue

    with open("data/dates-wednesdays.txt", "w") as file:
        file.write(str(wc))

    print(f"Count of Wednesdays: {wc}")


def extract_first_lines_from_logs():
    log_dir = "data/logs/"
    log_files = sorted(
        glob.glob(os.path.join(log_dir, "*.log")), key=os.path.getmtime, reverse=True
    )[:10]

    first_lines = []
    for log_file in log_files:
        with open(log_file, "r") as file:
            first_line = file.readline().strip()
            first_lines.append(first_line)

    with open("data/logs-recent.txt", "w") as file:
        for line in first_lines:
            file.write(line + "\n")

    print(f"Extracted first lines from {len(first_lines)} log files to output")


def create_markdown_index():
    docs_dir = "data/docs/"
    md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)

    index = {}

    for md in md_files:
        with open(md, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("# "):
                    filename = os.path.relpath(md, docs_dir)
                    index[filename] = line[2:]
                    break

    output_file = "data/docs/index.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(index, file, indent=2)

    print(f"Index file created: {output_file}")


def sort_contacts():
    file_path = "data/contacts.json"
    with open(file_path, "r") as file:
        contacts = json.load(file)

    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))

    output_file = "data/contacts-sorted.json"
    with open(output_file, "w") as file:
        json.dump(sorted_contacts, file, indent=4)

    print("Sorting complete. Sorted contacts saved to /data/contacts-sorted.json")


def gold_ticket():
    conn = sqlite3.connect("data/ticket-sales.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total = cur.fetchone()[0]
    conn.close()
    with open("data/ticket-sales-gold.txt", "w") as f:
        f.write(str(total))
    return total


# gold_ticket()
gen()
