import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_health():
    print("Waiting for backend to be healthy...")
    for _ in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                print("Backend is healthy!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    return False

def seed():
    # 1. Create Collection
    print("Creating 'documents' collection...")
    resp = requests.post(f"{BASE_URL}/collections/documents")
    print(f"Create collection status: {resp.status_code} - {resp.text}")

    # 2. Add Document
    doc = {
        "text": """GravityWork is an AI-native project orchestration platform designed to help teams manage complex workflows.
        It integrates with Jira, Slack, and GitHub to provide a unified view of project health.
        Key features include:
        - Federated Context: Aggregates data from multiple sources.
        - Intent Router: Intelligently routes user queries to the right agent.
        - Action Agents: Capable of performing tasks like creating tickets.
        - RAG Engine: Retrieves relevant documentation to answer questions.
        
        The platform uses a 3-column UI design inspired by LeanWorks and ScaleAlpha.
        """,
        "metadata": {"source": "manual_seed", "topic": "product_overview"}
    }
    
    print("Upserting document...")
    resp = requests.post(f"{BASE_URL}/collections/documents/documents", json=doc)
    print(f"Upsert status: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    if wait_for_health():
        seed()
    else:
        print("Backend failed to start")
        sys.exit(1)
