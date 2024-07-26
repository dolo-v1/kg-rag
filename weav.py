import weaviate
import os
import weaviate.classes.config as wc
import json
from weaviate.util import generate_uuid5


URI = os.environ["URI"]
APIKEY = os.environ["APIKEY"]
huggingface_key = os.environ["HF_API_KEY"]


def load_text_files(directory):
    text_data = {}
    for file in os.listdir("/home/shusrith/Downloads/archive/oa_other_txt.PMC000xxxxxx.baseline.2024-06-17/PMC000xxxxxx/")[:100]:
            if file.endswith('.txt'):
                file_path = os.path.join("/home/shusrith/Downloads/archive/oa_other_txt.PMC000xxxxxx.baseline.2024-06-17/PMC000xxxxxx/", file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_data[file] = f.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        text_data[file] = f.read()
    return text_data


def setup_weaviate():
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=URI,
        auth_credentials=weaviate.auth.AuthApiKey(api_key=APIKEY),
        headers={
        "X-huggingface-Api-Key": huggingface_key
        }
    )

    client.collections.create(
        name="PubMedOthers2",
        properties=[
            wc.Property(name="title", data_type=wc.DataType.TEXT),
            wc.Property(name="overview", data_type=wc.DataType.TEXT),
        ],

        vectorizer_config=wc.Configure.Vectorizer.text2vec_huggingface( # specify the vectorizer and model type you're using
          model="sentence-transformers/all-MiniLM-L6-v2",
          wait_for_model=True,
          use_gpu=True,
          use_cache=True,
        ),
    )

    return client





import time
from weaviate.exceptions import WeaviateBatchError

def upload_data_to_weaviate(client, text_data):
    docs = client.collections.get("PubMedOthers2")
    retry_attempts = 3
    batch_size = 50

    for attempt in range(retry_attempts):
        try:
            with docs.batch.fixed_size(
                batch_size=batch_size,
                concurrent_requests=1
            ) as batch:
                for key, value in text_data.items():
                    item = {
                        "title": key,
                        "overview": value,
                    }
                    batch.add_object(item)

            if len(docs.batch.failed_objects) > 0:
                print("There were some errors")
            else:
                break  # Exit the retry loop if successful

        except WeaviateBatchError as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retry_attempts - 1:
                print("Retrying...")
            else:
                print("Max retry attempts reached. Exiting.")
                raise

# Example usage:
# client = ...  # Initialize your Weaviate client
# text_data = ...  # Your data to upload
# upload_data_to_weaviate(client, text_data)



f = load_text_files(None)
# client = setup_weaviate()

client = weaviate.connect_to_weaviate_cloud(
        cluster_url=URI,
        auth_credentials=weaviate.auth.AuthApiKey(api_key=APIKEY),
        headers={
        "X-huggingface-Api-Key": huggingface_key
        }
    )
upload_data_to_weaviate(client, f)


def test_upload_to_weaviate(client):
    docs = client.collections.get("PubMedOthers2")
    
    try:
        with docs.batch.fixed_size(batch_size=1, concurrent_requests=1) as batch:
            item = {
                "title": "Test Title",
                "overview": "Test Overview"
            }
            batch.add_object(item)
        
        if len(docs.batch.failed_objects) > 0:
            print("Errors occurred during batch upload:")
            for fo in docs.batch.failed_objects:
                print(fo)
        else:
            print("Batch upload successful.")
    
    except WeaviateBatchError as e:
        print(f"Upload failed with error: {e}")

# Example usage:
# client = ...  # Initialize your Weaviate client



# test_upload_to_weaviate(client)
client.close()
