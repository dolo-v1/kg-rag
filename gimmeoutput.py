import subprocess
import csv
from typing import List, Dict


def completion(
    prompt: str,
) -> str:
    command = ["ollama", "run", "llama3.1", prompt]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()


def load_conversations(filename: str) -> List[Dict[str, str]]:
    conversations = []
    q = None
    a = None
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if "Human" in line:
                q = line[9:].strip()
            elif "AI" in line:
                a = line[6:].strip()
                if q is not None and a is not None:
                    conversation = {"question": q, "answer": a}
                    conversations.append(conversation)
                    q = None
                    a = None
    return conversations


def classify_text_with_llama(text: str) -> str:
    prompt = f"Classify the following text: '{text}'\nIs this about medicines or drugs? Respond only with 'Yes' or 'No' and aboslutely nothing else."
    response = completion(prompt)
    return response.strip().lower()


def filter_with_llama(conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    filtered_conversations = []
    for i, conversation in enumerate(conversations):
        question = conversation["question"]
        if classify_text_with_llama(question) == "yes":
            filtered_conversations.append(conversation)
        if i % 100 == 0:
            print(f"Processed {i} conversations.")
    return filtered_conversations


def save_filtered_conversations(conversations: List[Dict[str, str]], filename: str):
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerows(conversations)


def main(input_file: str, output_file: str):
    conversations = load_conversations(input_file)
    print(f"Loaded {len(conversations)} conversations.")
    filtered_conversations = filter_with_llama(conversations)
    print(f"Filtered {len(filtered_conversations)} conversations.")
    save_filtered_conversations(filtered_conversations, output_file)


if __name__ == "__main__":
    input_file = "test.csv"
    output_file = "filtered_conversations.csv"
    main(input_file, output_file)
