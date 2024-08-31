import subprocess
import csv
from typing import List, Dict

# Define the default model
DEFAULT_MODEL = "llama3"


def assistant(content: str) -> Dict[str, str]:
    return {"role": "assistant", "content": content}


def user(content: str) -> Dict[str, str]:
    return {"role": "user", "content": content}


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    return completion(prompt, model, temperature, top_p)


def completion(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    command = [
        "ollama",
        "generate",
        "--model",
        model,
        "--prompt",
        prompt,
        "--temperature",
        str(temperature),
        "--top_p",
        str(top_p),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()


def complete_and_print(prompt: str, model: str = DEFAULT_MODEL):
    print(f"==============\n{prompt}\n==============")
    response = completion(prompt, model)
    print(response, end="\n\n")


def load_conversations(filename: str) -> List[Dict[str, str]]:
    conversations = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(" [|Human|] ")
                if len(parts) >= 2:
                    conversation = {
                        "question": parts[1].strip(),
                        "answer": parts[2].strip() if len(parts) > 2 else "",
                    }
                    conversations.append(conversation)
    return conversations


def classify_text_with_llama(text: str) -> str:
    prompt = f"Classify the following text: '{text}'\nIs this about medicines or drugs? Respond with 'Yes' or 'No'."
    response = completion(prompt, model=DEFAULT_MODEL)
    return response.strip().lower()


def filter_with_llama(conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    filtered_conversations = []
    for conversation in conversations:
        question = conversation["question"]
        if classify_text_with_llama(question) == "yes":
            filtered_conversations.append(conversation)
    return filtered_conversations


def save_filtered_conversations(conversations: List[Dict[str, str]], filename: str):
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerows(conversations)


def main(input_file: str, output_file: str):
    conversations = load_conversations(input_file)
    filtered_conversations = filter_with_llama(conversations)
    save_filtered_conversations(filtered_conversations, output_file)


# Example usage
if __name__ == "__main__":
    input_file = "/kaggle/input/conversations.txt"
    output_file = "/kaggle/working/filtered_conversations.csv"
    main(input_file, output_file)

    # Print sample input
    with open(input_file, "r", encoding="utf-8") as file:
        print(file.read().splitlines()[:5])
