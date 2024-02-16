import chromadb
import os

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Construct the absolute path for CHROMA_DATA_PATH
CHROMA_DATA_PATH = os.path.join(os.path.dirname(current_file_path), "chroma")

COLLECTION_NAME = "movies"

Client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
Collection = Client.create_collection(
    name=COLLECTION_NAME,
    get_or_create=True
)
