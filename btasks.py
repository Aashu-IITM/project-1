import os
import shutil
import requests
import pygit
import sqlite3
import duckdb
import cv2
import pytesseract
import markdown
import json
import pandas as pd
from bs4 import BeautifulSoup
from pydub import AudioSegment
import speech_recognition as sr

data_dir = "data/"


def ensure_safe_path(path):
    """Ensure the path is within the /data directory safely."""
    base_path = os.path.join(os.getcwd(), "data")  # Absolute path of /data
    safe_path = os.path.abspath(
        os.path.join(base_path, path.lstrip("/"))
    )  # Normalize path

    if not safe_path.startswith(base_path):  # Ensure within /data
        raise PermissionError(
            f"Access to {safe_path} is not allowed. Must be within {base_path}"
        )

    return safe_path


def fetch_data_from_api(url, output_file):
    """B3: Fetch data from an API and save it."""
    ensure_safe_path(output_file)
    response = requests.get(url)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)


def clone_and_commit(repo_url, commit_message):
    """B4: Clone a git repo and make a commit."""
    repo_path = ensure_safe_path(os.path.join(data_dir, "repo"))

    if not os.path.exists(repo_path):
        pygit.Repo.clone_from(repo_url, repo_path)

    repo = pygit.load(repo_path)
    repo.add_all()
    repo.commit(message=commit_message)
    repo.push()


def run_sql_query(db_path, query):
    """B5: Run a SQL query on SQLite or DuckDB."""
    db_path = ensure_safe_path(db_path)
    conn = (
        sqlite3.connect(db_path)
        if db_path.endswith(".sqlite")
        else duckdb.connect(db_path)
    )
    result = conn.execute(query).fetchall()
    conn.close()
    return result


def scrape_website(url, output_file):
    """B6: Extract data from a website."""
    ensure_safe_path(output_file)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(soup.prettify())


def compress_resize_image(input_file, output_file, width, height):
    """B7: Compress or resize an image."""
    input_file, output_file = ensure_safe_path(input_file), ensure_safe_path(
        output_file
    )
    img = cv2.imread(input_file)
    resized = cv2.resize(img, (width, height))
    cv2.imwrite(output_file, resized)


def transcribe_audio(input_file, output_file):
    """B8: Transcribe audio from an MP3 file."""
    input_file, output_file = ensure_safe_path(input_file), ensure_safe_path(
        output_file
    )
    audio = AudioSegment.from_mp3(input_file)
    audio.export("temp.wav", format="wav")
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    os.remove("temp.wav")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)


def convert_markdown_to_html(input_file, output_file):
    """B9: Convert Markdown to HTML."""
    input_file, output_file = ensure_safe_path(input_file), ensure_safe_path(
        output_file
    )
    with open(input_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)


def filter_csv_and_return_json(input_file, output_file, column, value):
    """B10: Write an API endpoint that filters a CSV file and returns JSON data."""
    input_file, output_file = ensure_safe_path(input_file), ensure_safe_path(
        output_file
    )
    df = pd.read_csv(input_file)
    filtered_df = df[df[column] == value]
    filtered_df.to_json(output_file, orient="records")


def prevent_deletion():
    """B2: Prevent deletion of files."""

    def remove_protected(path):
        raise PermissionError("Deletion is not allowed.")

    os.remove = remove_protected
    shutil.rmtree = remove_protected


prevent_deletion()
