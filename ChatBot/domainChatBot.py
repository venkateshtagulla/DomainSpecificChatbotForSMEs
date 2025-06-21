# Install dependencies
!pip install PyMuPDF faiss-gpu transformers pdfplumber sentence-transformers bitsandbytes huggingface_hub flask flask-cors pyngrok

from huggingface_hub import login
from google.colab import files
import pdfplumber
import faiss
from sentence_transformers import SentenceTransformer
import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok

# Authenticate Hugging Face (manually or using environment variable)
login()

# Upload PDF file
uploaded = files.upload()

# Extract text from the uploaded PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Assuming the uploaded file is the first one
pdf_path = list(uploaded.keys())[0]
document_text = extract_text_from_pdf(pdf_path)
print("Extracted Text (Preview):", document_text[:500])  # Display first 500 characters

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Split text into chunks
def split_text_into_chunks(text, chunk_size=512):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

chunks = split_text_into_chunks(document_text)

# Generate embeddings for each chunk
embeddings = embedding_model.encode(chunks, convert_to_tensor=False)

# Create and populate the FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

print(f"FAISS index created with {index.ntotal} vectors.")

# Define quantization config and load LLaMA model
quantization_config = BitsAndBytesConfig(load_in_8bit=True)
READER_MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    READER_MODEL_NAME,
    torch_dtype=torch.float16,
    quantization_config=quantization_config,
    device_map="cuda:0",
)
tokenizer = AutoTokenizer.from_pretrained(READER_MODEL_NAME)

# Text generation pipeline
READER_LLM = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    do_sample=True,
    temperature=0.5,
    repetition_penalty=1.2,
    max_new_tokens=300,
)

# Prompt template
PROMPT_TEMPLATE = """
You are a highly intelligent assistant tasked with answering only the specific question asked, based strictly on the provided context. Follow these rules without exception:

1. **Answer the question provided accurately** based only on the given context. Do not include or generate any additional questions or commentary.
2. **Do not provide any extra details, comments, or explanations** beyond what is strictly required to answer the question.
3. If the answer is not found in the context, respond **only** with: "No answer found."
4. Avoid generating new questions or assumptions. Respond only to the question explicitly stated.
5. strictly return answer to the given question from context no need to return context and question simply return correct answer in well structured paragraph.

**Context:**
{context}

**Question:**
{question}

**Answer:**
"""

# Retrieval
def retrieve_relevant_chunks(query, k=5):
    query_embedding = embedding_model.encode([query], convert_to_tensor=False)
    distances, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0]]

# Cache
question_answer_cache = {}

def generate_answer_with_cache(query):
    if query in question_answer_cache:
        print("Answer retrieved from cache:")
        return question_answer_cache[query]
    
    print("Processing query for the first time:")
    relevant_chunks = retrieve_relevant_chunks(query)
    context = " ".join(relevant_chunks)
    final_prompt = PROMPT_TEMPLATE.format(question=query, context=context)
    response = READER_LLM(final_prompt)
    answer = response[0]["generated_text"].split("Answer:")[-1].strip()
    question_answer_cache[query] = answer
    print(answer)
    return answer

# Load ngrok token from environment variable
# (Set this in Colab or your environment manually to avoid hardcoding it)
os.environ["NGROK_AUTH_TOKEN"] = "YOUR_REAL_TOKEN_HERE"  # ← Set securely in actual use
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

# Flask setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("message", "")
    try:
        answer = generate_answer_with_cache(query)
        print(f"Generated answer: {answer}")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"response": answer})

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print("Public URL:", public_url)
    app.run(port=5000)
