# 🚀 CustomerLens AI

> **AI-Powered Customer Intelligence Platform**  
> Transform customer datasets and business documents into actionable insights using **Analytics + Machine Learning + RAG + LLMs**.

---

## 🧭 What is CustomerLens AI?

CustomerLens AI is a full-stack customer intelligence platform designed to answer one main question:

> **"What is happening with my customers, why is it happening, and what should I do next?"**

Instead of having separate tools for CSV analysis, customer profiles, ML predictions, document search, and AI assistance, CustomerLens brings them together in one application.

The platform can:

- Upload and analyze customer datasets
- Automatically understand dataset columns
- Generate metrics, charts, and statistical insights
- Build a Customer 360° view
- Predict customer churn/fraud risk
- Explain ML predictions
- Upload business/research documents
- Index documents into a vector database
- Answer questions using RAG
- Provide an AI Copilot for natural-language analysis
- Maintain prediction history, notifications, activity, and reports

---

# 🏗️ High-Level Architecture

```text
                         ┌─────────────────────────┐
                         │     CustomerLens UI      │
                         │ React + TypeScript       │
                         │ TanStack Router         │
                         │ React Query + Tailwind   │
                         └────────────┬────────────┘
                                      │
                              REST API / Axios
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      FastAPI Backend     │
                         │ Authentication           │
                         │ Business Logic           │
                         │ API Routes               │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼────────────────────────┐
              │                       │                        │
              ▼                       ▼                        ▼
       ┌─────────────┐        ┌───────────────┐       ┌────────────────┐
       │   SQLite    │        │   Analytics   │       │  ML Pipeline   │
       │ Application │        │    Engine     │       │                │
       │   Database  │        │ Pandas        │       │ Scikit-learn  │
       └─────────────┘        └───────────────┘       │ Logistic Reg. │
                                                      └────────────────┘
              │
              │
              └──────────────────────┐
                                     ▼
                            ┌───────────────────┐
                            │   RAG Pipeline    │
                            │ Document Chunking │
                            │ Embeddings        │
                            │ ChromaDB          │
                            │ Retrieval         │
                            │ Groq LLM          │
                            └─────────┬─────────┘
                                      │
                                      ▼
                                🤖 AI Copilot
```

---

# 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React | UI |
| Language | TypeScript | Type-safe frontend |
| Routing | TanStack Router | Page routing |
| Server State | TanStack React Query | API data, caching, mutations |
| Styling | Tailwind CSS | UI styling |
| Backend | FastAPI | REST APIs |
| Runtime | Uvicorn | Backend server |
| Database | SQLite | Application persistence |
| Data Processing | Pandas | Dataset analysis |
| ML | Scikit-learn | Prediction model |
| Model | Logistic Regression | Churn/fraud classification |
| Model Storage | Joblib | Persist trained models |
| Embeddings | Sentence Transformers | Convert text into vectors |
| Embedding Model | `all-MiniLM-L6-v2` | Document embeddings |
| Vector DB | ChromaDB | Semantic document retrieval |
| LLM | Groq API | AI-generated responses |
| API Client | Axios | Frontend → backend communication |
| Version Control | Git + GitHub | Collaboration/versioning |

---

# 📱 APPLICATION PAGES — COMPLETE BREAKDOWN

The most important part of this README is the following section.

Each page is explained in four ways:

1. **What the page does**
2. **What technology is used**
3. **How the backend works**
4. **What happens behind the UI**

---

# 1️⃣ 🏠 Home Page

### Purpose

The Home page is the **entry point and high-level overview** of CustomerLens.

It gives the user a quick understanding of the current state of their customer intelligence workspace.

### What is shown?

The Home page can summarize:

- Total datasets
- Total customers
- Total documents
- Revenue
- Transactions
- Average LTV
- Average risk
- Average churn
- Number of predictions
- Average prediction probability
- Average prediction confidence
- Recent activity
- Dataset information
- Recent insights
- Upload activity

### Architecture

```text
Home Page
    ↓
React Component
    ↓
React Query
    ↓
GET /home/summary
    ↓
FastAPI
    ↓
SQLite
    ↓
Aggregate application data
    ↓
JSON Response
    ↓
Home Dashboard
```

### Technologies

- React
- TypeScript
- TanStack React Query
- FastAPI
- SQLite

### Important concept

The Home page is primarily an **aggregation layer**.

It does not independently calculate every metric in the frontend. The backend collects information from the application's data sources and returns a summary.

---

# 2️⃣ 📊 Dashboard

### Purpose

The Dashboard is the **business intelligence overview** of the platform.

While Home is the overall application overview, Dashboard focuses more strongly on **customer/business analytics**.

### What it does

It can present:

- Customer metrics
- Revenue metrics
- Transaction information
- Churn information
- Risk information
- Dataset statistics
- Prediction statistics
- Charts
- Business KPIs

### Architecture

```text
Dashboard
    ↓
React + React Query
    ↓
GET /dashboard
    ↓
FastAPI
    ↓
SQLite + Analytics Services
    ↓
Aggregated KPIs
    ↓
Charts / Cards
```

### Technologies

- React
- TypeScript
- React Query
- FastAPI
- SQLite
- Pandas / analytics logic

### Why this page matters

This is the page you can demonstrate when explaining:

> "How can raw customer data be converted into business-level KPIs?"

---

# 3️⃣ 📤 Upload Center

### Purpose

The Upload Center is where users bring new data into CustomerLens.

It supports structured datasets and documents.

### Supported dataset formats

```text
CSV
XLSX
XLS
JSON
```

Other supported files can be treated as documents for the document/RAG workflow.

### Upload architecture

```text
User selects file
       ↓
React FormData
       ↓
Axios
       ↓
POST /datasets or /documents
       ↓
FastAPI
       ↓
File validation
       ↓
Storage
       ↓
Metadata saved in SQLite
       ↓
Dataset/document becomes available
```

### Technologies

- React
- TypeScript
- Axios
- FastAPI
- Pandas
- SQLite

### Important engineering point

The frontend decides whether the upload is a dataset or document based on the file extension and sends it to the corresponding backend endpoint.

---

# 4️⃣ 🗃️ Dataset Explorer

### Purpose

Dataset Explorer allows the user to inspect uploaded structured data.

### Features

- Dataset list
- Dataset metadata
- Number of rows
- Number of columns
- Dataset preview
- Column information
- Search/filtering
- Download dataset
- Delete dataset

### Architecture

```text
Dataset Explorer
       ↓
GET /datasets
       ↓
SQLite
       ↓
Dataset metadata
```

For preview:

```text
GET /datasets/{id}/preview
       ↓
Backend loads dataset
       ↓
Pandas
       ↓
Rows returned as JSON
       ↓
Frontend table
```

### Technologies

- React
- TypeScript
- FastAPI
- SQLite
- Pandas

---

# 5️⃣ 🔄 AI Workflow

### Purpose

The AI Workflow page represents the **data-to-intelligence pipeline**.

Conceptually:

```text
Upload
  ↓
Understand
  ↓
Analyze
  ↓
Predict
  ↓
Ask AI
  ↓
Take Action
```

The workflow connects the different intelligence modules rather than treating analytics, ML, and RAG as isolated features.

### Main technologies

- FastAPI
- Pandas
- Scikit-learn
- ChromaDB
- Sentence Transformers
- Groq API

---

# 6️⃣ 🤖 AI Copilot

## ⭐ One of the most important pages

The AI Copilot is the natural-language interface of CustomerLens.

Instead of manually navigating through datasets and documents, users can ask questions.

Examples:

```text
Which customer segment has the highest revenue?

Why is churn increasing?

What does this uploaded document say about customer retention?

Summarize the important information from the uploaded documents.
```

---

## RAG Architecture

```text
                 User Question
                      ↓
                AI Copilot UI
                      ↓
                POST /rag/query
                      ↓
               RAG Backend
                      ↓
              Query Processing
                      ↓
              Generate Query
                      ↓
             Vector Retrieval
                      ↓
                  ChromaDB
                      ↓
             Relevant Chunks
                      ↓
              Context Builder
                      ↓
                 Groq API
                      ↓
              Generated Answer
                      ↓
                Copilot UI
```

---

## Document ingestion

When a document enters the RAG system:

```text
Document
   ↓
Text Extraction
   ↓
Text Cleaning
   ↓
Chunking
   ↓
Sentence Transformer
   ↓
Embedding Vectors
   ↓
ChromaDB
```

### Embeddings

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embedding model converts text into numerical vectors.

Conceptually:

```text
"Customer churn increased"
             ↓
        [0.12, -0.44, 0.81, ...]
```

Semantically similar text produces similar vectors.

---

## ChromaDB

ChromaDB is used as the **vector database**.

It stores:

- Document chunks
- Embeddings
- Metadata
- Chunk identifiers

When a user asks a question, the query is embedded and compared against stored vectors.

---

## Groq API

The **Groq API is the LLM generation layer**.

ChromaDB answers:

> "Which pieces of information are relevant?"

The Groq LLM answers:

> "How should those relevant pieces of information be turned into a useful response?"

This separation is important.

```text
ChromaDB = Retrieval
Groq = Generation
```

---

# 7️⃣ 👤 Customer 360°

### Purpose

Customer 360° provides a consolidated view of an individual customer.

Instead of checking multiple screens, the user can see customer intelligence in one place.

### Possible information

- Customer profile
- Customer ID
- Dataset information
- Transactions/business data
- Complaints or related records
- Prediction results
- Risk/churn information
- Other available customer signals

### Architecture

```text
Customer ID
     ↓
GET /customers/{id}
     ↓
FastAPI
     ↓
SQLite
     ↓
Customer + related information
     ↓
Customer 360 UI
```

### Why it matters

Customer 360° converts raw records into an **individual customer intelligence view**.

---

# 8️⃣ 📈 Analytics

### Purpose

Analytics is the main **exploratory data analysis layer**.

It automatically understands uploaded datasets and generates meaningful visualizations.

---

## Analytics Pipeline

```text
Dataset
   ↓
Pandas DataFrame
   ↓
Semantic Column Detection
   ↓
Column Classification
   ↓
Metric Calculation
   ↓
Chart Generation
   ↓
Analytics UI
```

### Semantic detection

The system tries to identify:

```text
customer_id
name
money
date
churn
fraud
category
location
```

For example:

```text
customer_id
customerId
user_id
customer_number
```

can all be interpreted as customer identifiers.

---

## Column classification

Columns are classified as:

```text
Numeric
Categorical
Datetime
Identifier
```

Identifiers are generally excluded from analytical calculations to prevent meaningless graphs.

---

## Automatically generated charts

The analytics engine can create:

### Line charts

For:

```text
Date + Numeric
```

Example:

```text
Revenue over time
```

### Bar charts

For:

```text
Category + Numeric
```

Example:

```text
Average Revenue by Segment
```

### Distribution charts

For numeric variables.

### Scatter plots

For relationships between two numerical variables.

---

# 9️⃣ 💡 AI Insights

### Purpose

The Insights page converts raw statistics into human-readable observations.

Instead of only showing:

```text
Revenue = 5,200,000
```

the system can generate:

```text
The average revenue is X and values range from Y to Z.
```

### Insight categories

The system can generate insights about:

- Dataset size
- Missing values
- Dominant categories
- Category diversity
- Average values
- Median values
- Highest values
- Correlations
- Revenue
- Churn

### Architecture

```text
Dataset
   ↓
compute_metrics()
   ↓
classify_columns()
   ↓
generate_insights()
   ↓
Insight objects
   ↓
Insights UI
```

### Main backend functions

```python
compute_metrics()
generate_insights()
analyze_dataset()
```

---

# 🔟 🔮 Predictions

## Purpose

The Predictions page provides ML-based customer risk predictions.

The current workflow is designed around binary prediction such as:

```text
High Churn Risk
Low Churn Risk
```

or a suitable fraud/risk target.

---

## Prediction Architecture

```text
Customer selected
       ↓
POST /predict
       ↓
Find customer
       ↓
Find customer's dataset
       ↓
Detect churn/fraud target
       ↓
Select numeric features
       ↓
Median Imputation
       ↓
Logistic Regression
       ↓
Probability
       ↓
Confidence
       ↓
Feature contribution
       ↓
Save result in SQLite
```

---

## ML Model

The prediction pipeline uses:

```python
SimpleImputer(strategy="median")
```

followed by:

```python
LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)
```

### Why Logistic Regression?

- Fast
- Simple
- Interpretable
- Works well as a baseline
- Provides probability estimates
- Coefficients can be inspected for explanations

---

## Prediction output

The backend returns:

```text
Prediction
Probability
Confidence
Explanation
Model features
```

Example conceptually:

```json
{
  "prediction": "high_churn_risk",
  "probability": 0.82,
  "confidence": 0.82
}
```

### Confidence

The current implementation calculates:

```python
confidence = max(probability, 1 - probability)
```

### Explanation

The system examines Logistic Regression coefficients and returns the features with the largest absolute coefficients.

---

## Model persistence

Trained models are stored using:

```text
Joblib
```

Conceptually:

```text
Dataset
   ↓
Train model
   ↓
dataset_id.joblib
   ↓
Future prediction
   ↓
Reuse trained model
```

---

# 1️⃣1️⃣ 📑 Reports

### Purpose

Reports provide a more consolidated representation of customer/business intelligence.

The report layer can combine:

- Dataset information
- KPIs
- Analytics
- Predictions
- Insights

### Backend

```text
GET /reports/dashboard
```

The backend prepares the data while the frontend presents it in a report-oriented interface.

---

# 1️⃣2️⃣ 🔔 Notifications

### Purpose

The Notifications page provides a centralized place for system/user notifications.

This keeps important events separate from the analytical content.

Examples of notification-producing events can include:

- Dataset processing
- Prediction-related events
- System activity
- Other application events

### Architecture

```text
Backend event
     ↓
Notification persistence
     ↓
GET /notifications
     ↓
React Query
     ↓
Notification UI
```

---

# 1️⃣3️⃣ 🕒 Activity

### Purpose

Activity tracks important actions occurring inside the platform.

Examples:

```text
Dataset uploaded
Prediction generated
Document added
Customer action
```

### Architecture

```text
Application action
       ↓
Activity record
       ↓
SQLite
       ↓
GET /activity
       ↓
Activity UI
```

---

# 1️⃣4️⃣ 👤 Profile

### Purpose

The Profile page handles the user's application identity/profile information.

Authentication and profile information are connected to the backend user system.

### Relevant APIs

```text
GET  /auth/me
POST /auth/register
POST /auth/login
```

---

# 1️⃣5️⃣ ⚙️ Settings

The Settings page provides application/user configuration.

The page belongs to the application-management layer rather than the analytics/ML layer.

---

# 🧠 CORE BACKEND SERVICES

The backend is divided into logical responsibilities.

---

## `platform.py`

This contains major platform APIs and dataset/customer-related functionality.

Examples include:

```text
datasets
customers
customer 360
analytics
documents
dashboard
```

---

## `analysis_service.py`

This is one of the most important services in the project.

It contains:

```python
detect_semantic_columns()
classify_columns()
compute_metrics()
generate_charts()
generate_insights()
analyze_dataset()
```

### Overall flow

```text
Raw DataFrame
     ↓
Semantic understanding
     ↓
Column classification
     ↓
Metrics
     ↓
Charts
     ↓
Insights
```

---

## `predictions.py`

Responsible for:

```text
POST /predict
POST /predict/batch
GET /predictions/history
```

It handles:

- Dataset lookup
- Target detection
- Feature selection
- Model training
- Model loading
- Prediction
- Probability
- Confidence
- Explanation
- Prediction persistence

---

# 🗄️ DATABASE ARCHITECTURE

CustomerLens uses **two different storage concepts for two different jobs**.

## SQLite

Used for application/relational data.

Conceptually:

```text
Users
Datasets
Customers
Documents
Predictions
Activity
Notifications
```

SQLite is the system of record for application state.

---

## ChromaDB

Used for vector data.

```text
Document
   ↓
Chunks
   ↓
Embeddings
   ↓
ChromaDB
```

ChromaDB is **not a replacement for SQLite**.

The two databases solve different problems:

```text
SQLite
→ structured application data

ChromaDB
→ semantic/vector retrieval
```

---

# 🔐 AUTHENTICATION & DATA OWNERSHIP

CustomerLens associates application data with users.

Backend queries use the authenticated user's identity when retrieving protected resources.

Conceptually:

```text
Login
  ↓
Authenticated User
  ↓
Request
  ↓
current_user
  ↓
user["sub"]
  ↓
Owner-filtered database query
```

This prevents one user's datasets from being treated as another user's datasets.

---

# 🔌 FRONTEND → BACKEND API FLOW

The frontend centralizes API calls in:

```text
frontend/src/api/platform.ts
```

Example:

```typescript
predict: (
  customer_id: string,
  features: Record<string, unknown> = {},
) =>
  api
    .post("/predict", {
      customer_id,
      features,
    })
    .then((r) => r.data)
```

The flow is:

```text
React Page
   ↓
platformApi
   ↓
Axios client
   ↓
FastAPI
   ↓
Business logic
   ↓
SQLite / ML / RAG
   ↓
JSON
   ↓
React Query
   ↓
UI
```

---

# 🧩 REACT QUERY PATTERN

CustomerLens uses React Query for server state.

Example:

```typescript
const history = useQuery({
  queryKey: ["prediction-history"],
  queryFn: platformApi.predictionHistory,
});
```

After a prediction:

```typescript
onSuccess: () =>
  qc.invalidateQueries({
    queryKey: ["prediction-history"],
  })
```

This means the prediction history automatically refreshes after a new prediction.

---

# 📁 PROJECT STRUCTURE

```text
CustomerLens_AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── platform.py
│   │   │   ├── predictions.py
│   │   │   └── ...
│   │   │
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   ├── storage.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── analysis_service.py
│   │   │   └── RAG/document services
│   │   │
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── platform.ts
│   │   │
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── assets/
│   │   │
│   │   └── routes/
│   │       ├── _app.home.tsx
│   │       ├── _app.dashboard.tsx
│   │       ├── _app.datasets.tsx
│   │       ├── _app.documents.tsx
│   │       ├── _app.copilot.tsx
│   │       ├── _app.customer-360.tsx
│   │       ├── _app.analytics.tsx
│   │       ├── _app.insights.tsx
│   │       ├── _app.predictions.tsx
│   │       ├── _app.reports.tsx
│   │       ├── _app.notifications.tsx
│   │       ├── _app.profile.tsx
│   │       └── _app.settings.tsx
│   │
│   └── package.json
│
├── .gitignore
└── README.md
```

---

# 🔄 COMPLETE END-TO-END DATA FLOW

This is the most important architecture to remember for interviews.

```text
                    USER
                     │
                     ▼
              React Frontend
                     │
              Axios / React Query
                     │
                     ▼
               FastAPI APIs
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     SQLite       Pandas       ML Model
        │            │            │
        │            ▼            │
        │       Analytics          │
        │       Metrics            │
        │       Charts             │
        │       Insights           │
        │                           │
        └────────────┬──────────────┘
                     │
                     ▼
               Customer 360
                     │
                     ▼
              AI / RAG Layer
                     │
             ┌───────┴───────┐
             ▼               ▼
          ChromaDB         Groq API
         Retrieval        Generation
             │               │
             └───────┬───────┘
                     ▼
                 AI Copilot
```

---

# 🧪 DATA ANALYSIS PIPELINE

```text
Upload CSV/XLSX/JSON
        ↓
Pandas DataFrame
        ↓
Detect semantic columns
        ↓
Classify columns
        ↓
Calculate metrics
        ↓
Generate charts
        ↓
Generate insights
        ↓
Display analytics
```

---

# 🤖 ML PIPELINE

```text
Customer
   ↓
Customer's Dataset
   ↓
Find Target
   ↓
Select Numeric Features
   ↓
Missing Value Imputation
   ↓
Logistic Regression
   ↓
Probability
   ↓
Confidence
   ↓
Feature Explanation
   ↓
Save Prediction
```

---

# 📚 RAG PIPELINE

```text
             DOCUMENT INGESTION
                     │
                     ▼
               Text Extraction
                     │
                     ▼
                  Chunking
                     │
                     ▼
             Sentence Transformer
                     │
                     ▼
                 Embeddings
                     │
                     ▼
                 ChromaDB
                     │
                     │
             USER QUESTION
                     │
                     ▼
                 Embedding
                     │
                     ▼
              Similarity Search
                     │
                     ▼
             Relevant Chunks
                     │
                     ▼
                Context
                     │
                     ▼
                 Groq LLM
                     │
                     ▼
              Grounded Answer
```

---

# 🎯 WHY THIS PROJECT IS TECHNICALLY INTERESTING

CustomerLens is not just a CRUD application.

It combines multiple AI/software engineering concepts:

### 1. Full-stack engineering

```text
React → FastAPI → SQLite
```

### 2. Data engineering

```text
File upload → Pandas → structured analysis
```

### 3. Machine Learning

```text
Features → preprocessing → classification → probability
```

### 4. Explainable ML

```text
Model coefficients → feature contribution
```

### 5. Generative AI

```text
Documents → embeddings → retrieval → LLM
```

### 6. Vector databases

```text
Text → vectors → ChromaDB → similarity search
```

### 7. API engineering

```text
Frontend → Axios → FastAPI → services
```

### 8. Authentication

```text
User → authenticated request → owner-filtered data
```

---

# 🎤 INTERVIEW REVISION

## Explain CustomerLens in 30 seconds

> CustomerLens AI is a full-stack customer intelligence platform built with React, TypeScript and FastAPI. Users can upload customer datasets and documents, after which the system automatically analyzes structured data using Pandas to generate metrics, charts and insights. It also provides Customer 360° views and Logistic Regression-based churn/fraud predictions with probability and feature explanations. For unstructured documents, I implemented a RAG pipeline using Sentence Transformers and ChromaDB for semantic retrieval and Groq as the LLM generation layer. SQLite stores the application's structured data, while ChromaDB handles vector search.

---

## If the interviewer asks: "Explain your RAG."

Answer:

> I first extract and chunk uploaded documents. Each chunk is converted into an embedding using `all-MiniLM-L6-v2` and stored in ChromaDB with metadata. When the user asks a question through the AI Copilot, the query is embedded and used for similarity search. The most relevant chunks are retrieved and passed as context to the Groq LLM, which generates the final answer based on the retrieved information.

---

## If asked: "Why ChromaDB?"

> ChromaDB is used specifically for vector similarity search. SQLite is good for structured relational application data, but document retrieval requires comparing embeddings, so I use ChromaDB for the RAG layer.

---

## If asked: "Why Groq?"

> Groq provides the LLM inference layer. In my architecture, ChromaDB handles retrieval while Groq handles natural-language generation.

---

## If asked: "How does your prediction system work?"

> I identify a suitable churn or fraud target, select numeric features, handle missing values with median imputation, and train a class-balanced Logistic Regression model. The model produces a probability, from which I derive the prediction and confidence. I also inspect model coefficients to provide feature-level explanations and persist the trained model using Joblib.

---

## If asked: "How does your application understand an unknown CSV?"

> I don't hard-code the dataset structure. I use semantic column detection with aliases and fuzzy matching to identify concepts such as customer ID, revenue, date, churn, fraud and category. I also classify columns into numeric, categorical, datetime and identifier types. The analysis engine then uses those classifications to automatically select suitable metrics and visualizations.

---

## If asked: "Why do you use SQLite and ChromaDB together?"

```text
SQLite
→ users
→ datasets
→ customers
→ predictions
→ application metadata

ChromaDB
→ document chunks
→ embeddings
→ semantic retrieval
```

They are complementary, not competing databases.

---

# 📌 QUICK PROJECT CHEAT SHEET

| Component | Technology |
|---|---|
| UI | React |
| Language | TypeScript |
| Routing | TanStack Router |
| Server state | React Query |
| Styling | Tailwind CSS |
| API | FastAPI |
| Server | Uvicorn |
| Relational DB | SQLite |
| Data analysis | Pandas |
| ML | Scikit-learn |
| ML algorithm | Logistic Regression |
| Preprocessing | SimpleImputer |
| Model persistence | Joblib |
| Embeddings | Sentence Transformers |
| Embedding model | all-MiniLM-L6-v2 |
| Vector DB | ChromaDB |
| LLM | Groq API |
| HTTP client | Axios |
| Version control | Git/GitHub |

---


# 🚀 Future Improvements

Possible next versions:

- PostgreSQL for production-scale relational storage
- Redis/background workers
- XGBoost/LightGBM prediction models
- Model evaluation metrics
- SHAP explainability
- Hybrid BM25 + vector retrieval
- RAG reranking
- RAG evaluation
- Streaming LLM responses
- Docker
- CI/CD
- Cloud deployment
- Role-based access control
- Data drift monitoring
- Model drift monitoring
- Automated model retraining

---

# 👩‍💻 Author

**Nandini Shukla**

B.Tech CSE — Artificial Intelligence & Machine Learning

**Focus:** AI Engineering • Machine Learning • Generative AI • RAG • Full-Stack Development

---

## ⭐ One-Line Summary

> **CustomerLens AI transforms raw customer data and business documents into an intelligent customer intelligence workspace using analytics, machine learning, vector search, RAG, and LLM-powered assistance.**


