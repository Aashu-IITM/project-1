import json
import requests
import pytesseract
from PIL import Image
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import os

# Load AIProxy Token from environment variable (recommended for security)
AIPROXY_TOKEN = os.environ["AIPROXY_TOKEN"]
AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
}


def extract_email(input_file, output_file):
    """Extract sender's email address from an email file using GPT-4o-Mini."""
    with open(input_file, "r", encoding="utf-8") as file:
        email_text = file.read()

    prompt = f"Extract the sender's email address from the following email:\n\n{email_text}\n\nReturn only the email address."

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0,
    }

    response = requests.post(
        f"{AIPROXY_BASE_URL}/chat/completions", headers=HEADERS, json=data
    )
    response_json = response.json()

    if "choices" in response_json and len(response_json["choices"]) > 0:
        extracted_email = response_json["choices"][0]["message"]["content"].strip()
    else:
        extracted_email = "ERROR: Could not extract email"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(extracted_email)

    print(f"Extracted email: {extracted_email}")
    return extracted_email


def preprocess_image(img_path):
    """Preprocess the credit card image for better OCR accuracy."""
    img = cv2.imread(img_path)

    if img is None:
        print(f"ERROR: Could not load image -> {img_path}")
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance details
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Apply a slight blur to remove noise
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Morphological operations to close small gaps
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)

    return morph


def extract_credit_card(input_file, output_file):
    """Extract credit card number from an image using OCR with preprocessing."""
    processed_img = preprocess_image(input_file)

    if processed_img is None:
        return

    # Run OCR with an optimized config
    custom_config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)

    # Extract only numbers (ignoring expiry dates and text)
    card_number = "".join(filter(str.isdigit, extracted_text))

    if 13 <= len(card_number) <= 19:  # Valid credit card length check
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(card_number)
        print(f"✅ Extracted credit card number: {card_number}")
    else:
        print("⚠️ OCR may have failed; extracted text:", extracted_text)


def get_text_embedding(text):
    """Generate text embeddings using AIProxy's text-embedding-3-small model."""
    data = {"model": "text-embedding-3-small", "input": [text]}

    response = requests.post(
        f"{AIPROXY_BASE_URL}/embeddings", headers=HEADERS, json=data
    )
    response_json = response.json()

    if "data" in response_json and len(response_json["data"]) > 0:
        return response_json["data"][0]["embedding"]
    else:
        raise ValueError("Failed to generate embedding")


def find_similar_comments(input_file, output_file):
    """Find the most similar pair of comments using text embeddings and cosine similarity."""
    with open(input_file, "r", encoding="utf-8") as file:
        comments = file.read().splitlines()

    embeddings = [get_text_embedding(comment) for comment in comments]

    max_similarity = -1
    most_similar_pair = None

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if sim > max_similarity:
                max_similarity = sim
                most_similar_pair = (comments[i], comments[j])

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(most_similar_pair, file, indent=4)

    print(f"Most similar comments saved to {output_file}")
    return most_similar_pair


# extract_email("data/email.txt", "data/email-sender.txt")
# extract_credit_card("data/credit_card.png", "data/credit-card.txt")
# find_similar_comments("data/comments.txt", "data/comments-similar.txt")
