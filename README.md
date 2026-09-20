# SportsBuddy 🏏⚽🏀

**SportsBuddy** is a domain-specific AI chatbot for a sports shop. It helps users discover and compare sports products using natural-language queries.

The application combines:

* React + TypeScript frontend
* FastAPI backend
* Ollama + Llama 3.2 3B for natural-language understanding and response generation
* A structured JSON product catalogue
* Deterministic product filtering
* Deterministic product recommendation/ranking

> **Note:** SportsBuddy uses a lightweight **RAG-style architecture** based on deterministic structured retrieval. It does not currently use embeddings or a vector database.

---

## 1. Project Overview

SportsBuddy allows users to ask questions such as:

* "Show me running shoes"
* "I need Nike football products"
* "Find badminton equipment under $100"
* "Show me basketball products"
* "What running shoes do you recommend?"
* "Do you have Adidas products?"
* "Show me products under $50"

Instead of asking the LLM to invent products, the application retrieves products from the actual product catalogue and provides those products to the LLM for response generation.

The product catalogue is the **source of truth**.

---

## 2. Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Frontend   │
                         │   TypeScript + Vite │
                         └──────────┬──────────┘
                                    │
                              POST /chat
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI Backend  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Ollama        │
                         │    Llama 3.2 3B     │
                         └──────────┬──────────┘
                                    │
                         Structured Requirements
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Product Search    │
                         │   JSON Catalogue    │
                         └──────────┬──────────┘
                                    │
                              Matching Products
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Recommendation      │
                         │ / Ranking Engine    │
                         └──────────┬──────────┘
                                    │
                                  Top 5
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Ollama        │
                         │ Grounded Generation │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Response   │
                         │  + Product Cards    │
                         └─────────────────────┘
```

---

# 3. RAG-Style Processing

SportsBuddy uses a simplified retrieval-augmented generation approach.

The flow is:

```text
User Query
    ↓
LLM Query Understanding
    ↓
Structured Requirements
    ↓
Product Retrieval
    ↓
Product Ranking
    ↓
Top 5 Products
    ↓
LLM Grounded Response
    ↓
User
```

### Example

User asks:

> "Show me running shoes under $150"

The first LLM call converts the natural-language request into structured requirements:

```json
{
  "intent": "product_search",
  "query": "running shoes",
  "sport": "Running",
  "category": "Footwear",
  "max_price": 150
}
```

The backend then searches the product catalogue.

For example:

```text
Product Catalogue
       ↓
sport = Running
       ↓
category = Footwear
       ↓
price <= 150
       ↓
Matching Products
```

The recommendation engine ranks the matching products.

The top products are then passed to the second LLM prompt:

```text
Available Products:

1. Nike Air Zoom Pegasus 40
   Price: $130
   Rating: 4.7

2. ASICS Gel-Kayano 30
   Price: $140
   Rating: 4.6

...
```

The LLM generates a natural-language response using only the retrieved products.

---

# 4. Is This Traditional RAG?

Not exactly.

Traditional RAG commonly looks like:

```text
User Query
    ↓
Embedding Model
    ↓
Vector Database
    ↓
Semantic Similarity Search
    ↓
Relevant Chunks
    ↓
LLM
    ↓
Answer
```

SportsBuddy currently uses:

```text
User Query
    ↓
LLM
    ↓
Structured Filters
    ↓
JSON Product Search
    ↓
Deterministic Ranking
    ↓
Top Products
    ↓
LLM
    ↓
Answer
```

There is currently:

* No embedding model
* No vector database
* No semantic vector search
* No document chunking

This approach is appropriate for the current structured product dataset because products have explicit fields such as sport, category, brand, and price.

---

# 5. Dataset

The product catalogue is located at:

```text
backend/data/sports-shop-products.json
```

The dataset contains approximately:

* 200 products
* 18 sports
* 4 major categories
* 48+ subcategories
* 50+ brands

### Sports

Examples include:

* Badminton
* Baseball
* Basketball
* Boxing & MMA
* Cricket
* Cycling
* Football
* Golf
* Gym & Fitness
* Hiking & Outdoor
* Running
* Skateboarding
* Skiing & Snowboarding
* Swimming
* Table Tennis
* Tennis
* Volleyball
* Yoga & Pilates

### Product Fields

Each product contains fields such as:

```text
id
name
brand
sport
category
subcategory
price
originalPrice
currency
rating
reviewCount
inStock
stockQuantity
description
features
colors
sizes
gender
isNew
isBestSeller
sku
```

The dataset is treated as the authoritative source for product information.

---

# 6. Backend

The backend is implemented using **FastAPI**.

Main backend files:

```text
backend/
├── app/
│   ├── main.py
│   ├── products.py
│   ├── recommendations.py
│   ├── llm.py
│   └── schemas.py
│
└── data/
    └── sports-shop-products.json
```

---

## 7. Backend Responsibilities

### `main.py`

Responsible for:

* FastAPI application
* API endpoints
* CORS configuration
* Chat orchestration

Main endpoint:

```http
POST /chat
```

---

### `products.py`

Responsible for:

* Loading product data
* Product filtering
* Product search

Supported filters include:

```text
query
sport
category
subcategory
brand
max_price
```

The filters are applied deterministically by the backend.

---

### `recommendations.py`

Responsible for deterministic product ranking.

Products are scored using factors such as:

```text
Rating
Review count
Stock availability
Best-seller status
New product status
Sale status
Query relevance
```

Example scoring logic:

```text
rating × 10
+
review count contribution
+
stock bonus
+
best seller bonus
+
new product bonus
+
sale bonus
+
query relevance
```

The recommendation engine does **not** create new products.

It only reorders products that were already retrieved from the catalogue.

---

### `llm.py`

Responsible for communication with Ollama.

There are two main LLM operations.

#### 1. Requirement Extraction

The first LLM call understands the user's natural-language query.

Example:

```text
"Find me Nike running shoes below $150"
```

becomes:

```json
{
  "intent": "product_search",
  "query": "running shoes",
  "sport": "Running",
  "category": "Footwear",
  "brand": "Nike",
  "max_price": 150
}
```

#### 2. Response Generation

The second LLM call receives the retrieved products and generates a natural-language answer.

The prompt explicitly instructs the LLM to use only the supplied products.

---

### `schemas.py`

Contains the structured requirements model:

```python
class ChatRequirements(BaseModel):
    intent: Literal[
        "product_search",
        "general_question",
        "unknown"
    ] = "unknown"

    query: str | None = None
    sport: str | None = None
    category: str | None = None
    subcategory: str | None = None
    brand: str | None = None
    max_price: float | None = None
    user_skill_level: str | None = None
```

---

# 8. Chat Processing

The `/chat` endpoint follows this process:

```text
POST /chat
    ↓
extract_requirements()
    ↓
normalize_requirements()
    ↓
Is this a product search?
    │
    ├── No
    │     ↓
    │   General LLM response
    │
    └── Yes
          ↓
      search_products()
          ↓
      recommend_products()
          ↓
      Top 5 products
          ↓
      generate_response()
          ↓
      Response
```

---

# 9. Query Understanding

The LLM is used primarily for understanding natural language.

For example:

```text
"I want something for running, preferably Nike, and under $120"
```

The LLM identifies:

```json
{
  "sport": "Running",
  "brand": "Nike",
  "max_price": 120
}
```

The backend then performs the actual filtering.

This separation is intentional.

### LLM

Responsible for:

* Understanding natural language
* Extracting user requirements
* Generating conversational responses

### Backend

Responsible for:

* Product retrieval
* Filtering
* Ranking
* Product truth
* Price filtering
* Stock information

This prevents the LLM from becoming the source of truth for product data.

---

# 10. Frontend

The frontend uses:

* React
* TypeScript
* Vite
* CSS

Frontend structure:

```text
frontend/
└── src/
    ├── components/
    │   ├── ChatWindow.tsx
    │   ├── ChatMessage.tsx
    │   ├── ProductCard.tsx
    │   ├── ChatInput.tsx
    │   └── ErrorBoundary.tsx
    │
    ├── services/
    │   └── chatApi.ts
    │
    ├── types/
    │   └── chat.ts
    │
    ├── utils/
    │   └── format.ts
    │
    ├── App.tsx
    ├── index.css
    └── main.tsx
```

---

# 11. Frontend Responsibilities

The frontend is intentionally kept separate from the chatbot intelligence.

React is responsible for:

* Displaying the chat interface
* Sending messages
* Showing loading state
* Showing errors
* Displaying assistant responses
* Rendering product cards
* Maintaining chat history
* Responsive UI

The frontend does **not** perform:

* Product filtering
* Recommendation ranking
* LLM processing
* Product selection

---

# 12. API

## POST `/chat`

Request:

```json
{
  "message": "Show me Nike running shoes under $150"
}
```

Response:

```json
{
  "message": "I found several Nike running shoes under $150...",
  "requirements": {
    "intent": "product_search",
    "query": "running shoes",
    "sport": "Running",
    "category": "Footwear",
    "brand": "Nike",
    "max_price": 150,
    "user_skill_level": null
  },
  "products": [],
  "total_matches": 3
}
```

The actual `products` array contains the matching catalogue products.

---

# 13. Environment Variables

Frontend environment:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

An example environment file is also provided:

```text
frontend/.env.example
```

---

# 14. Ollama Setup

SportsBuddy uses Ollama for local LLM inference.

Install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

Verify that Ollama is running:

```bash
ollama list
```

The backend expects the model:

```text
llama3.2:3b
```

Using Ollama means the chatbot can run locally without requiring an OpenAI API key.

---

# 15. Running the Backend

Navigate to the backend:

```bash
cd backend
```

Create/activate your Python virtual environment.

Example:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 16. Running the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Vite:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 17. Example Queries

### Product Search

```text
Show me running shoes
```

```text
I need Nike football products
```

```text
Find badminton equipment under $100
```

```text
Show me Adidas products
```

```text
I need basketball shoes under $120
```

```text
Show me products below $50
```

### General Questions

```text
What sports products do you sell?
```

```text
What brands are available?
```

```text
Hello
```

The chatbot distinguishes between general questions and product-search requests.

---

# 18. No-Match Handling

If no products satisfy the requested filters, the backend returns an empty product list.

For example:

```text
Show me Nike cricket shoes under $5,000
```

If there are no matching products, the chatbot informs the user that no matching products were found.

The response-generation prompt is designed to prevent the LLM from inventing alternative products that are not present in the supplied catalogue.

---

# 19. Grounding

A key design goal is to prevent hallucinated product information.

The final LLM prompt receives the actual retrieved products.

For example:

```text
Retrieved Products:

Nike Air Zoom Pegasus 40
Price: $130
Rating: 4.7
Brand: Nike
Sport: Running
```

The LLM can discuss this product because it exists in the retrieved data.

It should not create:

```text
Nike Air Zoom Pegasus 50
```

if that product was not retrieved.

Therefore:

```text
Catalogue
    ↓
Retrieval
    ↓
Ranking
    ↓
Grounded Context
    ↓
LLM
```

---

# 20. Why Use an LLM?

The LLM is not being used to replace the database.

Its main purpose is to understand natural language.

For example, users can say:

```text
"I need something for jogging"
```

instead of:

```text
sport = Running
category = Footwear
```

The LLM converts the user's natural language into structured requirements.

It also converts structured product results back into a natural conversational response.

---

# 21. Why Not Let the LLM Search Products Directly?

Allowing the LLM to invent or determine product information would introduce several problems:

* Hallucinated products
* Incorrect prices
* Incorrect availability
* Incorrect ratings
* Inconsistent filtering
* Difficult testing

Instead:

```text
LLM
 ↓
Understand query
 ↓
Backend
 ↓
Search real data
 ↓
LLM
 ↓
Explain results
```

This creates a clear separation between language understanding and business/data logic.

---

# 22. Recommendation Strategy

Recommendations are deterministic.

The ranking engine considers:

1. Product rating
2. Number of reviews
3. Stock availability
4. Best-seller status
5. New-product status
6. Sale status
7. Query relevance

The recommendation engine does not perform semantic reasoning.

Its job is to provide a predictable ordering of products after filtering.

---

# 23. User Skill Level

The chatbot schema supports:

```text
user_skill_level
```

For example:

```text
"I'm a beginner looking for badminton equipment"
```

The skill level can be extracted as user context.

However, the current product dataset does not contain a reliable `skill_level` field.

Therefore, skill level is **not used as a deterministic product filter**.

This prevents unsupported assumptions about which products are intended for beginners or advanced users.

---

# 24. Error Handling

The application includes handling for:

* LLM failures
* Invalid responses
* API failures
* Empty product results
* Invalid product prices
* Frontend request errors
* Loading states

The frontend also includes an error boundary to prevent an unexpected React rendering error from crashing the entire interface without feedback.

---

# 25. CORS

The FastAPI backend allows the local Vite frontend:

```text
http://localhost:5173
```

This allows the browser application to communicate with:

```text
http://localhost:8000
```

during local development.

---

# 26. Testing

Testing performed during development included:

* Backend API testing
* Product search testing
* LLM requirement extraction testing
* Recommendation testing
* No-match testing
* Frontend build testing
* Frontend/backend integration testing
* Browser-based chat testing
* Loading/error-state testing

One observed limitation is that a small local LLM such as Llama 3.2 3B can occasionally produce inconsistent structured extraction for broad natural-language queries.

The backend therefore includes deterministic normalization and fallback handling to improve reliability.

---

# 27. Current Limitations

SportsBuddy currently does not implement:

* Vector embeddings
* Vector database
* Semantic similarity search
* PDF/document ingestion
* Conversation memory
* User accounts
* Order placement
* Payment processing
* Real-time inventory
* External e-commerce integration

The current retrieval system is based on structured JSON filtering.

---

# 28. Future Improvements

A future version could implement full vector-based RAG:

```text
Product/Data Documents
        ↓
Document Chunking
        ↓
Embedding Model
        ↓
Vector Database
        ↓
        ↑
User Query
        ↓
Query Embedding
        ↓
Semantic Search
        ↓
Relevant Documents
        ↓
LLM
        ↓
Grounded Response
```

Potential technologies:

* ChromaDB
* FAISS
* pgvector
* Qdrant
* OpenAI embeddings
* Sentence Transformers

Other improvements could include:

* Conversation memory
* Product comparison
* Personalized recommendations
* Product detail pages
* Inventory APIs
* Shopping-cart integration
* Order tracking
* Multi-language support
* Better evaluation datasets
* Automated backend tests
* Automated end-to-end tests

---

# 29. Project Design Principles

SportsBuddy follows these principles:

### 1. Data is the source of truth

The product catalogue is authoritative.

### 2. LLM understands language

The LLM converts natural-language input into structured requirements.

### 3. Backend performs deterministic retrieval

Product filtering is performed by application code.

### 4. Recommendations are deterministic

The recommendation engine ranks actual products.

### 5. LLM generates grounded responses

The final response is generated from retrieved products.

### 6. Frontend does not contain business logic

React is responsible for presentation and user interaction.

---

# 30. Complete Request Flow

For example, the user enters:

```text
"Can you find me Nike running shoes under $150?"
```

### Step 1 — Frontend

React sends:

```http
POST /chat
```

with:

```json
{
  "message": "Can you find me Nike running shoes under $150?"
}
```

### Step 2 — LLM

Ollama extracts:

```json
{
  "intent": "product_search",
  "query": "running shoes",
  "sport": "Running",
  "category": "Footwear",
  "brand": "Nike",
  "max_price": 150
}
```

### Step 3 — Backend Retrieval

The backend filters the JSON catalogue:

```text
Sport = Running
AND
Category = Footwear
AND
Brand = Nike
AND
Price <= 150
```

### Step 4 — Recommendation

Matching products are ranked.

### Step 5 — Context

Top 5 products are provided to the LLM.

### Step 6 — Generation

The LLM creates a user-friendly response based on those products.

### Step 7 — Frontend

React displays:

```text
Assistant response

Product 1
Product 2
Product 3
...
```

---

# 31. Key Takeaway

SportsBuddy demonstrates how an LLM can be combined with deterministic application logic to build a domain-specific chatbot.

The important architecture is:

```text
                 Natural Language
                       │
                       ▼
                 ┌───────────┐
                 │    LLM    │
                 │ Understand│
                 └─────┬─────┘
                       │
               Structured Query
                       │
                       ▼
              ┌────────────────┐
              │ Product Search │
              │  JSON Dataset  │
              └───────┬────────┘
                      │
               Matching Products
                      │
                      ▼
              ┌────────────────┐
              │ Recommendation │
              │     Engine     │
              └───────┬────────┘
                      │
                    Top 5
                      │
                      ▼
                 ┌───────────┐
                 │    LLM    │
                 │  Generate │
                 └─────┬─────┘
                       │
                       ▼
                 Final Answer
```

This keeps the LLM responsible for **language**, while the application remains responsible for **data accuracy, filtering, and recommendations**.
