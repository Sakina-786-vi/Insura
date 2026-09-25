# 🛡️ INSURA — Intelligent Insurance Assistant

<p align="center">
  <strong>Understand your insurance. Make informed decisions.</strong>
</p>

<p align="center">
  An AI-powered insurance assistant that transforms complex insurance policies into an accessible, conversational experience.
</p>

<p align="center">

![CI](https://img.shields.io/badge/CI-Passing-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask-black?style=for-the-badge&logo=flask)
![n8n](https://img.shields.io/badge/Workflow-n8n-orange?style=for-the-badge&logo=n8n)
![SurrealDB](https://img.shields.io/badge/Database-SurrealDB-purple?style=for-the-badge)
![Cognee](https://img.shields.io/badge/Knowledge-Cognee-blueviolet?style=for-the-badge)
![Groq](https://img.shields.io/badge/AI-Groq-f55036?style=for-the-badge)
![Sarvam AI](https://img.shields.io/badge/Voice%20%26%20Language-Sarvam%20AI-0f766e?style=for-the-badge)

</p>

---

## 📌 Overview

**INSURA** is an intelligent insurance assistant designed to simplify complex insurance documents and improve the way users interact with their insurance policies.

Users can upload their insurance policy PDFs, which are processed through an automated **n8n extraction workflow**. The extracted information is stored in **SurrealDB** and indexed into **Cognee**, enabling contextual and policy-specific retrieval for the chatbot.

INSURA combines:

- 📄 Automated insurance policy document extraction
- 🤖 AI-powered policy chatbot
- 🧠 Policy-aware knowledge retrieval with Cognee
- 💬 General insurance question answering
- 🎯 Insurance simulation capabilities
- 🌐 Multilingual interaction using Sarvam AI
- 🎙️ Speech-to-text and text-to-speech support
- 🔐 User-specific policy data isolation
- 📊 Centralized logging and monitoring

The goal is to provide users with an accessible, conversational, and intelligent way to understand their insurance coverage.

---
## 🏗️ System Architecture

The following diagram illustrates the major components of the INSURA platform.

```mermaid
flowchart LR
    User[Authenticated User]

    Frontend[INSURA Frontend UI]
    Auth[Authentication System]

    Flask[Flask Backend API]

    Upload[Policy PDF Upload]
    PolicyAPI[Policy Processing API]
    ChatAPI[Chatbot API]
    SimAPI[Simulation API]

    n8n[n8n Policy Extraction Workflow]

    SurrealDB[(SurrealDB)]
    PolicyData[Extracted Policy Data]

    Cognee[Cognee Policy Knowledge Layer]
    LanceDB[(Cognee LanceDB Storage)]

    Groq[Groq AI]
    Chatbot[INSURA Chatbot]
    Simulation[INSURA Simulation Engine]

    Sarvam[Sarvam AI Services]
    STT[Speech to Text]
    Translation[Translation]
    TTS[Text to Speech]

    CloudWatch[Logging and Monitoring]

    User --> Frontend
    Frontend --> Auth
    Frontend --> Flask

    Flask --> Upload
    Flask --> PolicyAPI
    Flask --> ChatAPI
    Flask --> SimAPI

    Upload --> n8n
    PolicyAPI --> n8n

    n8n --> PolicyData
    PolicyData --> SurrealDB

    SurrealDB --> Cognee
    Cognee --> LanceDB

    ChatAPI --> Cognee
    Cognee --> Chatbot
    Chatbot --> Groq

    SimAPI --> Cognee
    Cognee --> Simulation
    Simulation --> Groq

    Frontend --> Sarvam
    Sarvam --> STT
    Sarvam --> Translation
    Sarvam --> TTS

    STT --> ChatAPI
    Chatbot --> Translation
    Translation --> TTS
    TTS --> Frontend

    Flask --> CloudWatch
    n8n --> CloudWatch
    Cognee --> CloudWatch
    Groq --> CloudWatch
    Sarvam --> CloudWatch
```

---

## ✨ Key Features

### 📄 1. Insurance Policy Upload and Extraction

Users can upload insurance policy PDF documents through the INSURA frontend.

The policy processing pipeline:

1. The user uploads a policy PDF.
2. The Flask backend sends the document to the n8n workflow.
3. n8n extracts structured policy information.
4. Extracted policy data is stored in SurrealDB.
5. Relevant policy information is indexed into Cognee.
6. The policy becomes available for contextual chatbot retrieval.

🔗 **[View the n8n Policy Extraction Workflow](./frontend/n8n/insura-policy-extraction-workflow.png)**

> The workflow image should be stored in the repository at:
>
> `frontend/n8n/insura-policy-extraction-workflow.png`

---

### 🤖 2. AI Insurance Chatbot

The INSURA chatbot allows authenticated users to ask questions about their insurance policies.

Example questions:

- What is my policy coverage?
- What is my deductible?
- Does my policy cover hospitalization?
- What exclusions are mentioned in my policy?
- What is the claim process?
- What benefits are included in my insurance plan?

The chatbot uses:

```text
User Question
      ↓
Flask Chatbot API
      ↓
Cognee Policy Retrieval
      ↓
Relevant Policy Information
      ↓
Existing Groq AI Service
      ↓
INSURA Chatbot Response
```

The chatbot is designed to use policy-specific context when available.

If a requested fact is not present in the user's policy, the chatbot should respond:

> "This is not specified in your policy"

The system should not invent or assume missing policy information.

General insurance questions can continue to work without requiring policy-specific retrieval.

---

### 🧠 3. Cognee Knowledge Layer

INSURA uses **Cognee** as a policy knowledge and retrieval layer.

Cognee is responsible for organizing and retrieving relevant policy information. SurrealDB remains the primary application database and source of truth.

Cognee is not intended to replace:

- SurrealDB
- The existing chatbot service
- The existing simulation service
- The n8n extraction workflow
- The Groq AI integration

#### Cognee Responsibilities

- Index extracted policy information
- Support semantic policy retrieval
- Provide relevant policy context to the chatbot
- Maintain policy-scoped knowledge
- Support reindexing when a policy is updated or replaced
- Prevent cross-user policy data leakage
- Gracefully handle retrieval or indexing failures

#### Policy Retrieval Flow

```text
SurrealDB
    ↓
Cognee Indexing
    ↓
Cognee Knowledge Storage
    ↓
Policy-Specific Retrieval
    ↓
Existing Groq AI Service
```

Cognee retrieval must be scoped by:

- Authenticated user ID
- Policy ID
- Relevant policy context

Users must never retrieve information belonging to another user.

---

### 🎯 4. Insurance Simulation

INSURA includes an insurance simulation feature that can help users explore insurance-related scenarios.

The simulation service remains part of the existing backend architecture.

Cognee may optionally provide relevant policy information to the simulation service, but the simulation logic remains outside Cognee.

```text
User
  ↓
Simulation API
  ↓
Optional Policy Retrieval
  ↓
Existing Simulation Engine
  ↓
Groq AI
  ↓
Simulation Response
```

The simulation system must continue to use the existing simulation route and service rather than introducing a separate simulation architecture.

---

### 🌐 5. Sarvam AI Integration

INSURA can integrate Sarvam AI services to support multilingual and voice-based interactions.

Potential capabilities include:

- 🎙️ Speech-to-text
- 🌍 Language translation
- 🔊 Text-to-speech

#### Voice Interaction Flow

```text
User Voice Input
      ↓
Sarvam Speech-to-Text
      ↓
Flask Chatbot API
      ↓
Policy Retrieval with Cognee
      ↓
Groq AI Response
      ↓
Sarvam Translation
      ↓
Sarvam Text-to-Speech
      ↓
Frontend Audio Output
```

Sarvam AI configuration should be managed through environment variables.

API keys must never be hardcoded or committed to the repository.

---

## 🔄 Core Application Workflows

### Policy Processing Workflow

```mermaid
flowchart TD
    A[User Uploads Policy PDF]
    B[INSURA Frontend]
    C[Flask Backend]
    D[n8n Extraction Workflow]
    E[Extracted Policy Data]
    F[SurrealDB]
    G[Cognee Indexing]
    H[Policy Available for Retrieval]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
```

### Policy Chatbot Workflow

```mermaid
flowchart TD
    A[Authenticated User]
    B[Chatbot UI]
    C[Flask Chatbot API]
    D{Policy-Specific Question?}
    E[Cognee Policy Retrieval]
    F[Relevant Policy Context]
    G[General Insurance Knowledge]
    H[Existing Groq AI Service]
    I[Chatbot Response]

    A --> B
    B --> C
    C --> D
    D -->|Yes| E
    E --> F
    F --> H
    D -->|No| G
    G --> H
    H --> I
    I --> B
```

### Voice and Translation Workflow

```mermaid
flowchart TD
    A[User Voice Input]
    B[Sarvam Speech-to-Text]
    C[Flask Chatbot API]
    D[Cognee Policy Retrieval]
    E[Existing Groq AI Service]
    F[Sarvam Translation]
    G[Sarvam Text-to-Speech]
    H[Frontend Audio Output]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
```

---

## 🧰 Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | Existing INSURA UI | User interface and interaction |
| Backend | Flask | API routes and application logic |
| Authentication | Existing authentication system | User authentication and identity |
| Workflow Automation | n8n | Policy document extraction |
| Primary Database | SurrealDB | Application data and extracted policies |
| Knowledge Layer | Cognee 1.6.0 | Policy indexing and retrieval |
| Vector Storage | LanceDB | Cognee vector persistence |
| Language Model | Groq AI | Chatbot and simulation responses |
| Voice and Language | Sarvam AI | Speech, translation, and voice services |
| Monitoring | Application logging and monitoring | Operational visibility |

---

## 📁 Suggested Repository Structure

```text
INSURA/
│
├── frontend/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── ...
│   │
│   ├── cognee/
│   │   ├── initialization.py
│   │   ├── indexing.py
│   │   └── retrieval.py
│   │
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   └── n8n/
│       ├── insura-policy-extraction-workflow.png
│       ├── insura-policy-comparison-workflow.png
│       ├── insura-learning-generation-workflow.png
│       └── README.md
│
├── docs/
│   └── architecture.md
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/INSURA.git
cd INSURA
```

Replace `YOUR_USERNAME` with your GitHub username or organization.

---

### 2. Configure the Backend Environment

Create a `.env` file inside the backend directory.

```bash
cp backend/.env.example backend/.env
```

Configure the required environment variables:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=true

# Authentication
AUTH_SECRET_KEY=your_secret_key

# SurrealDB
SURREALDB_URL=your_surrealdb_url
SURREALDB_NAMESPACE=your_namespace
SURREALDB_DATABASE=your_database
SURREALDB_USER=your_username
SURREALDB_PASSWORD=your_password

# Groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model

# Cognee
COGNEE_SYSTEM_ROOT_DIRECTORY=./.cognee_data/system
COGNEE_DATA_ROOT_DIRECTORY=./.cognee_data/data

# Sarvam AI
SARVAM_API_KEY=your_sarvam_api_key

# n8n
N8N_WEBHOOK_URL=your_n8n_webhook_url
```

> Do not commit `.env` files, API keys, database credentials, or private configuration to GitHub.

---

### 3. Install Backend Dependencies

Create and activate a virtual environment:

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```
---

### 5. Start the Backend

Run the Flask application using the project's configured entry point.

Example:

```bash
python backend/app.py
```

> The exact command may vary depending on the existing INSURA backend structure.

---

### 6. Start the Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```
---

## 📚 Documentation

| Resource | Link |
|---|---|
| n8n Policy Extraction Workflow | [View Workflow Image](./frontend/n8n/insura-policy-extraction-workflow.png) |
| n8n Policy Comparison Workflow | [View Workflow Image](./frontend/n8n/insura-policy-comparison-workflow.png) |
| n8n Learning Generation Workflow | [View Workflow Image](./frontend/n8n/insura-learning-generation-workflow.png) |
| System Architecture | [Architecture Documentation](./docs/architecture.md) |
| Backend | [Backend Directory](./backend/) |
| Frontend | [Frontend Directory](./frontend/) |

---

## 🚀 Future Improvements

Potential future enhancements include:

- Claim document assistance
- Policy renewal reminders
- Advanced multilingual support
- Voice-based policy conversations
- Enhanced audit logging

---

## ⚠️ Disclaimer

INSURA is an AI-powered insurance assistance platform.

AI-generated responses are intended to help users understand insurance-related information and should not be treated as a substitute for official policy documents, professional insurance advice, or confirmation from the relevant insurance provider.

Users should verify important coverage, exclusions, claim requirements, and financial decisions against their official policy documentation and insurer.

---

## 🤝 Contributing

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Test your changes.
5. Commit your changes.

```bash
git commit -m "Add your feature"
```

6. Push your branch.

```bash
git push origin feature/your-feature
```

7. Open a pull request.

Please ensure that contributions maintain existing authentication, data isolation, chatbot, simulation, and policy-processing behavior.

---

## 📄 License

Add your project's license information here.

---

<p align="center">
  Built with ❤️ for a simpler and more accessible insurance experience.
</p>
