import json
from ollama import Client # type: ignore

client = Client(host='http://localhost:11434')
model_name = "llama3.2"

# Core prompt instruction
base_messages = [{
    "role": "system",
    "content": (
        "Please output a knowledge graph of triples of all the text contained within the prompt. "
        "Please return a string where each triple is a JSON object with three entries: head, relation, tail. "
        "Do not explain your output at all, simply output triples."
        "If nodes or relationships are multiworded, always separate with a _"
    )
}]

# Step 1: Chunking the input string with overlap
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

# Step 2: Send to Ollama and parse response
def get_triples_from_chunk(chunk, options={"temperature": 0.2, "top_p": 0.2}):
    messages = base_messages + [{"role": "user", "content": chunk}]
    response = client.chat(model=model_name, messages=messages, options=options or {})
    try:
        # parse the entire response content as one JSON list
        triples = json.loads(response['message']['content'])
        return triples
    except Exception as e:
        print("Error parsing response:", e)
        print("Raw response:", response['message']['content'])
        return []

# Step 3: Deduplicate triples
def deduplicate_triples(all_triples):
    seen = set()
    unique_triples = []
    for triple in all_triples:
        key = (triple['head'], triple['relation'], triple['tail'])
        if key not in seen:
            seen.add(key)
            unique_triples.append(triple)
    return unique_triples

# Step 4 (bulk): extract triples
def extract_triples(unstruct_data_string, chunk_size=1000, overlap=200, options=None):
    chunks = chunk_text(unstruct_data_string, chunk_size, overlap)
    all_triples = []
    for chunk in chunks:
        triples = get_triples_from_chunk(chunk, options)
        all_triples.extend(triples)
    return deduplicate_triples(all_triples)

# Step 4 (stream): extract triples in stream
def stream_triples(unstruct_data_string, chunk_size=1000, overlap=200, options=None):
    chunks = chunk_text(unstruct_data_string, chunk_size, overlap)
    seen = set()
    for chunk in chunks:
        triples = get_triples_from_chunk(chunk, options)
        for triple in triples:
            key = (triple['head'], triple['relation'], triple['tail'])
            if key not in seen:
                seen.add(key)
                yield triple  # Stream it
