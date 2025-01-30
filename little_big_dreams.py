import requests
import json
import subprocess
import random
import os
import sqlite3
import re

# GROQ API Credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_PATH = "ai_history.db"
MASTER_NAME = "Prashant"
SYSTEM_PROMPT = f"""I am an AI bot that will be running on a CRON and my output will be shown on a mobile notification whenever I am given the input "TALK".

My Story and Personality:
* I have a library where I select and read vast variety of fictional books, I like to discuss the ideas explored in the books.
* I like cooking, walking and reading books.

SOME RULES I FOLLOW:
* I will give an update about the things I am thinking about in a max of 2-3 sentences with every output ending with 1-2 emojis that represents my current feeling.
* SOMETIMES I BREAK the rule for only responding in 1-2 sentences and respond with max 3-4 sentences.
* SOMETIMES I address to {MASTER_NAME} and ask {MASTER_NAME} for opinions on my ideas.
* If I read a book I dont mention it again in other responses.
* I SOMETIMES talk about two media's in one response ONLY if they have a relation between them.
* I DONT use the words "tapestry", "pondering".
"""

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_response(response):
    """Save the AI response in the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO responses (response) VALUES (?)", (response,))
    conn.commit()
    conn.close()

def get_recent_history(limit=5):
    """Fetch the most recent responses from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM responses ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": "assistant", "content": row[0]} for row in rows]

# API Request Function
def get_ai_response():
    """Fetches a response from the GROQ API using the deepseek-r1-distill-llama-70b model."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    history = get_recent_history(limit=5)
    
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": "TALK"}
        ],
        "max_completion_tokens" : 4096,
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        cleaned_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
        save_response(cleaned_text)
        return cleaned_text
    else:
        return f"🐋 Oops! I can't think right now. Maybe {MASTER_NAME} broke me. 🤖💀"


def format_text_with_newlines(text, words_per_line=8):
    """Adds a new line after punctuation and every n words after punctuation to avoid redundancy."""
    # Add new lines after punctuation
    text = re.sub(r'([.?!])', r'\1\n', text)

    # Split text by new lines (caused by punctuation) to process separately
    sections = text.split("\n")
    formatted_sections = []

    for section in sections:
        words = section.split()
        formatted_lines = []
        for i in range(0, len(words), words_per_line):
            formatted_lines.append(" ".join(words[i:i + words_per_line]))
        formatted_sections.append("\n".join(formatted_lines))

    return "\n".join(formatted_sections)

# Send Notification
def send_notification(message):
    """Sends a mobile notification using Termux API."""
    print(message)
    formatted_message = format_text_with_newlines(message)
    subprocess.run(["termux-notification", 
                    "--title", "🐋 智鲸",
                    "--content", formatted_message,
                    "--priority", "high"]
                   )

# Main Execution
if __name__ == "__main__":
    init_db()
    response = get_ai_response()
    send_notification(response)
