import argparse
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base URL of the Open WebUI API - get from env or use default
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000/api")

# Retrieve the API key from the environment variable
API_KEY = os.getenv("OPEN_WEBUI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the OPEN_WEBUI_API_KEY environment variable or in .env file.")

# Common headers for all API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def upload_knowledge(file_path):
    """Upload a knowledge document for indexing."""
    url = f"{BASE_URL}/v1/files/"
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers={"Authorization": f"Bearer {API_KEY}"}, files=files)
    if response.status_code == 200:
        print("File uploaded successfully.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to upload file: {response.status_code}")
        print(response.text)

def list_knowledge():
    """List all loaded knowledge documents."""
    url = f"{BASE_URL}/v1/files/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print("Knowledge documents:")
        for doc in data:
            collection = doc.get("meta", {}).get("collection_name", "N/A")
            print(f"- ID: {doc.get('id')}")
            print(f"  Filename: {doc.get('filename')}")
            print(f"  Collection: {collection}")
            print()
    else:
        print(f"Failed to retrieve knowledge documents: {response.status_code}")
        print(response.text)

def list_models():
    """List all available LLM models."""
    url = f"{BASE_URL}/models"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print("Available models:")
        for model in data.get("data", []):
            print(f"- {model.get('name')}")
    else:
        print(f"Failed to retrieve models: {response.status_code}")
        print(response.text)

def ask_question(question, model, knowledge_ids=None):
    """Execute a one-shot question to an LLM with optional knowledge documents."""
    url = f"{BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question}]
    }
    if knowledge_ids:
        payload["knowledge_ids"] = knowledge_ids
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("Response:")
        for choice in data.get("choices", []):
            content = choice.get("message", {}).get("content", "")
            # Replace escaped newlines with actual newlines
            formatted_content = content.replace("\\n", "\n")
            print(formatted_content)
            print()
    else:
        print(f"Failed to get response: {response.status_code}")
        print(response.text)

def load_directory(directory_path):
    """Load all MD files from a directory and its subdirectories."""
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory")
        return
    
    md_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    if not md_files:
        print(f"No .md files found in {directory_path}")
        return
    
    print(f"Found {len(md_files)} .md files. Uploading...")
    
    for file_path in md_files:
        print(f"Uploading: {file_path}")
        upload_knowledge(file_path)

def main():
    parser = argparse.ArgumentParser(description="Open WebUI CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a knowledge document")
    upload_parser.add_argument("file", help="Path to the document")

    # Load directory command
    load_dir_parser = subparsers.add_parser("load-dir", help="Load all MD files from a directory and subdirectories")
    load_dir_parser.add_argument("directory", help="Path to the directory")

    # List knowledge documents command
    subparsers.add_parser("list-knowledge", help="List all loaded knowledge documents")

    # List models command
    subparsers.add_parser("list-models", help="List all available LLM models")

    # Ask question command
    ask_parser = subparsers.add_parser("ask", help="Ask a one-shot question")
    ask_parser.add_argument("question", help="The question to ask")
    ask_parser.add_argument("--model", required=True, help="Model name to use")
    ask_parser.add_argument("--knowledge", nargs="*", help="Optional list of knowledge document IDs")

    args = parser.parse_args()

    if args.command == "upload":
        upload_knowledge(args.file)
    elif args.command == "load-dir":
        load_directory(args.directory)
    elif args.command == "list-knowledge":
        list_knowledge()
    elif args.command == "list-models":
        list_models()
    elif args.command == "ask":
        ask_question(args.question, args.model, args.knowledge)

if __name__ == "__main__":
    main()
