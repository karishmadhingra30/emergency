# First Aid Chatbot Training Strategy

## Current Implementation Overview

The chatbot currently uses:
- **Model**: Gemma 2B (2 billion parameters) via Ollama
- **Approach**: RAG (Retrieval-Augmented Generation) with static knowledge base
- **Knowledge**: 18 topics in `first_aid_knowledge.py` (~651 lines)
- **No Fine-tuning**: Uses pre-trained model + prompt engineering

---

## Training Approach 1: Hugging Face Datasets

### Recommended Datasets

#### 1. **Medical/First Aid Datasets**

| Dataset | Size | Focus | HF Link |
|---------|------|-------|---------|
| **MedQuAD** | 47,457 Q&A pairs | Medical questions from NIH | `medalpaca/medical_meadow_medqa` |
| **HealthCareMagic-100k** | 100k conversations | Doctor-patient dialogues | `lavita/ChatDoctor-HealthCareMagic-100k` |
| **MedDialog** | 3.66M utterances | Clinical conversations | `medical_dialog` |
| **PubMedQA** | 1k expert annotations | Biomedical research Q&A | `pubmed_qa` |
| **First Aid QA** | Custom scraped | Specific first aid procedures | Build custom |
| **Disaster Response** | Limited | Emergency protocols | Build custom |

#### 2. **Recommended Training Pipeline**

```python
# Step 1: Install dependencies
# pip install datasets transformers torch accelerate peft bitsandbytes

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Step 2: Load datasets
medqa = load_dataset("medalpaca/medical_meadow_medqa")
chatdoctor = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k")

# Step 3: Combine and filter for first aid relevance
first_aid_keywords = [
    "bleeding", "burn", "fracture", "CPR", "choking", "poisoning",
    "heart attack", "stroke", "shock", "wound", "injury", "emergency"
]

def is_first_aid_relevant(example):
    text = f"{example.get('input', '')} {example.get('output', '')}".lower()
    return any(keyword in text for keyword in first_aid_keywords)

filtered_dataset = medqa.filter(is_first_aid_relevant)

# Step 4: Format for instruction tuning
def format_for_training(example):
    return {
        "text": f"""### Instruction:
You are an emergency first aid assistant. Provide clear, actionable medical advice.

### Input:
{example['input']}

### Response:
{example['output']}"""
    }

training_data = filtered_dataset.map(format_for_training)
```

#### 3. **Fine-tuning with LoRA (Recommended)**

```python
# Step 5: Configure LoRA for parameter-efficient fine-tuning
lora_config = LoraConfig(
    r=16,                      # Rank of update matrices
    lora_alpha=32,             # Scaling factor
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Step 6: Load base model (Gemma 2B)
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2b",
    load_in_4bit=True,         # 4-bit quantization for memory efficiency
    torch_dtype=torch.float16,
    device_map="auto"
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# Step 7: Training arguments
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./first_aid_gemma_lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
    evaluation_strategy="steps",
    eval_steps=100,
    warmup_steps=50,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=training_data["train"],
    eval_dataset=training_data["test"],
)

# Step 8: Train
trainer.train()

# Step 9: Save LoRA adapters (only ~10-50 MB)
model.save_pretrained("./first_aid_lora_adapters")
```

#### 4. **Benefits of HuggingFace Approach**

✅ **Pros:**
- Large-scale medical knowledge (100k+ examples)
- Professional medical language patterns
- Active community with pre-built datasets
- Easy to filter for first aid relevance
- LoRA allows fine-tuning on consumer GPUs

⚠️ **Cons:**
- May contain general medical info beyond first aid
- Requires GPU for training (4+ hours on T4/A10)
- Need careful filtering for emergency-specific content
- Western medical bias (not India-specific)

---

## Training Approach 2: PDF Documents

### Strategy for PDF-Based Training

#### 1. **Recommended PDF Sources**

##### **Official Medical Guidelines:**
- **Red Cross First Aid Manuals** (American Red Cross, Indian Red Cross)
- **WHO Emergency Care Guidelines**
- **St. John Ambulance First Aid Manual**
- **National Disaster Management Authority (India) Handbooks**
- **Indian Council of Medical Research (ICMR) Emergency Protocols**

##### **India-Specific Sources:**
- NDMA flood safety guidelines
- Mountain rescue protocols (India Mountaineering Foundation)
- Monsoon health advisories (Ministry of Health)
- Snake bite treatment (Indian Journal of Medical Research)

#### 2. **PDF Processing Pipeline**

```python
# Step 1: Install dependencies
# pip install pypdf2 langchain sentence-transformers faiss-cpu

import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json

# Step 2: Extract text from PDFs
def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Process multiple PDFs
pdf_sources = [
    "red_cross_first_aid.pdf",
    "who_emergency_care.pdf",
    "ndma_flood_guidelines.pdf",
    "snake_bite_treatment_india.pdf"
]

documents = []
for pdf in pdf_sources:
    text = extract_pdf_text(pdf)
    documents.append({
        "text": text,
        "source": pdf
    })

# Step 3: Chunk documents intelligently
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,           # ~200 words per chunk
    chunk_overlap=200,         # Preserve context
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = []
for doc in documents:
    splits = text_splitter.split_text(doc["text"])
    for split in splits:
        chunks.append({
            "text": split,
            "source": doc["source"]
        })

print(f"Created {len(chunks)} text chunks")

# Step 4: Create vector database
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [chunk["text"] for chunk in chunks]
metadatas = [{"source": chunk["source"]} for chunk in chunks]

vectorstore = FAISS.from_texts(
    texts=texts,
    embedding=embeddings,
    metadatas=metadatas
)

# Save for later use
vectorstore.save_local("./first_aid_vectordb")
```

#### 3. **Enhanced RAG Implementation**

```python
# Step 5: Integrate with chatbot (enhanced gemma_chat.py)

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import ollama

class EnhancedGemmaChat:
    def __init__(self):
        # Load vector database
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = FAISS.load_local(
            "./first_aid_vectordb",
            self.embeddings
        )
        self.model_name = "gemma2:2b"

    def get_relevant_context(self, query, k=3):
        """Retrieve top-k most relevant PDF chunks"""
        docs = self.vectorstore.similarity_search(query, k=k)
        context = "\n\n".join([
            f"Source: {doc.metadata['source']}\n{doc.page_content}"
            for doc in docs
        ])
        return context

    def chat(self, user_message):
        # Get relevant PDF knowledge
        pdf_context = self.get_relevant_context(user_message)

        # Combine with existing knowledge base
        static_context = self.get_static_knowledge(user_message)

        # Build enhanced prompt
        system_prompt = """You are an emergency first aid expert assistant.
Provide clear, actionable medical advice based on authoritative sources."""

        full_prompt = f"""{system_prompt}

**Authoritative Medical Guidelines:**
{pdf_context}

**Additional Context:**
{static_context}

**User Question:**
{user_message}

Provide step-by-step first aid instructions."""

        # Call Gemma
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}]
        )

        return response['message']['content']
```

#### 4. **Converting PDFs to Training Data**

```python
# Step 6: Create instruction-tuning dataset from PDFs

from transformers import pipeline
import json

# Use existing LLM to generate Q&A pairs from PDF chunks
qa_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large"
)

training_data = []

for chunk in chunks[:100]:  # Process first 100 chunks as example
    # Generate questions from content
    question_prompt = f"""Generate a medical emergency question that would be answered by this text:
{chunk['text']}

Question:"""

    question = qa_generator(
        question_prompt,
        max_length=100,
        num_return_sequences=1
    )[0]['generated_text']

    training_data.append({
        "instruction": "You are a first aid expert. Answer this emergency question.",
        "input": question,
        "output": chunk['text'],
        "source": chunk['source']
    })

# Save training dataset
with open("first_aid_training_data.json", "w") as f:
    json.dump(training_data, f, indent=2)

print(f"Created {len(training_data)} training examples from PDFs")
```

#### 5. **Benefits of PDF Approach**

✅ **Pros:**
- Authoritative medical sources (Red Cross, WHO, etc.)
- India-specific guidelines available (NDMA, ICMR)
- Full control over training content
- Can include diagrams/illustrations
- Offline-friendly (PDFs can be curated in advance)
- No data privacy concerns

⚠️ **Cons:**
- Requires PDF acquisition (copyright considerations)
- OCR quality varies (scanned PDFs need cleanup)
- Manual curation needed
- Smaller dataset size vs HuggingFace
- Time-intensive preprocessing

---

## Hybrid Recommendation: Best of Both Worlds

### Optimal Training Strategy

```
┌─────────────────────────────────────────┐
│  Step 1: PDF Processing                 │
│  - Extract authoritative guidelines     │
│  - Create vector database (FAISS)       │
│  - Use for RAG retrieval                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Step 2: HuggingFace Dataset Filtering  │
│  - Load medical Q&A datasets            │
│  - Filter for first aid relevance       │
│  - Combine with PDF-generated Q&A       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Step 3: LoRA Fine-tuning               │
│  - Fine-tune Gemma 2B with LoRA         │
│  - ~5000-10000 first aid examples       │
│  - Focus on Indian context              │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Step 4: Enhanced RAG Deployment        │
│  - Use fine-tuned model                 │
│  - Augment with PDF vector search       │
│  - Keep static knowledge as fallback    │
└─────────────────────────────────────────┘
```

### Implementation Priorities

1. **Short-term (1-2 weeks):**
   - ✅ Set up PDF processing pipeline
   - ✅ Create FAISS vector database from Red Cross/WHO PDFs
   - ✅ Enhance `gemma_chat.py` with RAG retrieval
   - No training needed - immediate improvement

2. **Medium-term (1 month):**
   - Load HuggingFace medical datasets
   - Filter for first aid relevance
   - Generate Q&A from PDFs using LLM
   - Create combined training dataset (5k+ examples)

3. **Long-term (2-3 months):**
   - Fine-tune Gemma 2B with LoRA
   - Evaluate on held-out test set
   - Deploy fine-tuned model via Ollama
   - Continuous improvement cycle

---

## Dataset Quality Checklist

When selecting training data, ensure:

- ✅ **Medical Accuracy**: Verified by professionals
- ✅ **Emergency Focus**: Prioritize life-threatening conditions
- ✅ **Clarity**: Step-by-step instructions
- ✅ **India-Specific**: Include local context (snake species, monsoons, etc.)
- ✅ **Accessibility**: Written for layperson understanding
- ✅ **Recency**: Updated medical guidelines (post-2020)
- ✅ **Safety Warnings**: Include "when to seek professional help"

---

## Evaluation Metrics

Track chatbot improvement using:

1. **Accuracy**: Responses match medical guidelines
2. **Completeness**: Includes all critical steps
3. **Safety**: Appropriate warnings and disclaimers
4. **Relevance**: Answers match user intent
5. **Response Time**: <2 seconds for RAG, <30 seconds for generation

---

## Resources & References

### HuggingFace Datasets
- Medical Meadow: https://huggingface.co/medalpaca
- ChatDoctor: https://huggingface.co/lavita
- PubMedQA: https://huggingface.co/datasets/pubmed_qa

### PDF Sources
- Indian Red Cross: https://indianredcross.org
- NDMA Guidelines: https://ndma.gov.in
- WHO Emergency Care: https://www.who.int/emergencies

### Training Tools
- PEFT (LoRA): https://github.com/huggingface/peft
- LangChain: https://python.langchain.com
- Ollama: https://ollama.ai

---

## Next Steps

1. Decide: **Quick RAG enhancement** (PDFs) or **Deep fine-tuning** (HF datasets)?
2. Acquire authoritative PDF sources
3. Set up GPU environment (Google Colab/Lambda Labs if needed)
4. Implement chosen pipeline
5. Evaluate against current baseline
6. Iterate based on user feedback

**Recommendation**: Start with PDF-based RAG enhancement for immediate improvement, then layer in HuggingFace fine-tuning for long-term performance gains.
