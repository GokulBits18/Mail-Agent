# Mail-Agent

**Mail-Agent** is an AI-powered email triage and response assistant that helps manage an email inbox by automatically analyzing incoming messages, assigning priority, detecting sender sentiment, generating contextual reply options, and routing responses based on message priority.

The system combines a **local Qwen LLM through Ollama**, **Gmail IMAP/SMTP**, **FastAPI**, **SQLAlchemy with SQLite**, and a **React dashboard** to create an intelligent email management workflow.

## Overview

Mail-Agent processes emails through an automated pipeline:

**Gmail Inbox → Email Extraction → AI Analysis → Priority & Sentiment Classification → Smart Reply Generation → Automatic or Human-Approved Response**

The AI analyzes each email and produces:

* Priority classification: `Low`, `Medium`, `High`, or `Spam`
* Sender sentiment
* Positive / accepting reply
* Polite declining reply
* Neutral clarification reply

Low-priority emails can be automatically replied to, while other messages remain pending for human review.

## Key Features

### AI Email Analysis

Mail-Agent uses the local model:

```text
qwen2.5-coder:latest
```

through **Ollama**.

For every email, the model generates structured JSON containing five fields:

```text
priority
sentiment
draft_reply_1
draft_reply_2
draft_reply_3
```

The generated responses are designed to match the sender's tone and provide different response strategies.

### Intelligent Priority Classification

Emails are categorized into four priority levels:

| Priority | Purpose                                |
| -------- | -------------------------------------- |
| Low      | Routine or less urgent messages        |
| Medium   | Work or normal important communication |
| High     | Urgent communication                   |
| Spam     | Marketing or unwanted messages         |

### Sentiment Analysis

The system determines the sender's overall emotional tone, such as:

```text
Positive
Neutral
Negative
Frustrated
Friendly
Urgent
```

### Smart Reply Generation

For each analyzed email, Mail-Agent generates three possible responses:

1. **Positive / Accept** — accepts or agrees with the message.
2. **Polite Decline** — respectfully rejects the request.
3. **Ask for Details** — requests additional information or clarification.

The selected response can also be manually edited before sending.

### Automatic Email Response

Low-priority emails can be automatically replied to using the generated positive response.

Higher-priority messages remain in a pending state so that the user can review and approve the response.

### Human-in-the-Loop Approval

Pending emails can be reviewed through the dashboard.

The user can:

* Read the original email
* Select one of the AI-generated replies
* Edit the reply
* Approve and send it

This provides human oversight before sending important responses.

### Email Integration

Mail-Agent uses Gmail services for email communication.

**Receiving emails:**

```text
Gmail IMAP
imap.gmail.com
```

**Sending emails:**

```text
Gmail SMTP
smtp.gmail.com:587
```

### SQLite Database

The application stores email information and AI-generated results using **SQLite** and **SQLAlchemy**.

Stored information includes:

```text
Sender
Subject
Content
Priority
Sentiment
Draft Reply 1
Draft Reply 2
Draft Reply 3
Final Reply
Status
```

The database is stored locally as:

```text
emails.db
```

## Dashboard

The React frontend provides a centralized email management interface.

The dashboard includes:

### Priority Breakdown

A chart displays the distribution of emails by priority.

### Top Senders

A bar chart displays the senders with the highest number of emails.

### Inbox and Spam Views

Users can switch between:

```text
Inbox
Spam
```

### Email Management

Each email displays:

```text
Sender
Subject
Priority
Sentiment
Status
Actions
```

The frontend also supports reviewing pending replies and viewing previously sent responses.

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* IMAP
* SMTP
* python-dotenv

### AI

* Ollama
* Qwen 2.5 Coder

### Frontend

* React
* Axios
* Recharts
* Lucide React

The React application communicates with the FastAPI backend using Axios and the backend API is configured at `http://127.0.0.1:8000`.

### Architecture

```text
                    ┌─────────────────────┐
                    │     Gmail Inbox     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Gmail IMAP      │
                    │  Email Fetching     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │    API Backend      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌───────────────────┐       ┌───────────────────┐
       │   Local AI Model  │       │   SQLite Database │
       │ Ollama + Qwen     │       │    SQLAlchemy     │
       └─────────┬─────────┘       └───────────────────┘
                 │
                 ▼
       ┌──────────────────────┐
       │ Priority + Sentiment │
       │ + Smart Replies      │
       └──────────┬───────────┘
                  │
          ┌───────┴────────┐
          │                │
          ▼                ▼
   Low Priority       Other Emails
   Auto Reply         Human Review
          │                │
          └───────┬────────┘
                  ▼
       ┌─────────────────────┐
       │     Gmail SMTP      │
       │    Send Response    │
       └─────────────────────┘
```

## Project Structure

A typical project structure can be organized as:

```text
Mail-Agent/
│
├── backend/
│   ├── main.py
│   ├── ai_service.py
│   ├── database.py
│   ├── imap_service.py
│   ├── smtp_service.py
│   ├── emails.db
│   └── .env
│
├── frontend/
│   ├── src/
│   │   └── App.jsx
│   ├── package.json
│   └── ...
│
└── README.md
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
EMAIL_ACCOUNT=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

Use a Gmail **App Password** rather than exposing your regular Gmail password.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/GokulBits18/Mail-Agent.git
cd Mail-Agent
```

### 2. Backend Setup

Create and activate a Python virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv
```

### 3. Install Ollama

Install Ollama on your system and download the model:

```bash
ollama run qwen2.5-coder:latest
```

The local model must be available before running the AI processing pipeline.

### 4. Configure Gmail

Create the `.env` file:

```env
EMAIL_ACCOUNT=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 5. Start the Backend

Run:

```bash
uvicorn main:app --reload
```

The FastAPI server will run at:

```text
http://127.0.0.1:8000
```

## Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The React application will then provide the Mail-Agent dashboard.

## Running the Local AI Model

Before processing emails, start Ollama with:

```bash
ollama run qwen2.5-coder:latest
```

## Application Workflow

### Step 1 — Sync Inbox

The dashboard sends a request to:

```http
GET /api/process-emails
```

The backend retrieves email messages through Gmail IMAP.

### Step 2 — Store Emails

New emails are stored in the SQLite database.

### Step 3 — AI Processing

Unprocessed emails are sent to the local Qwen model for:

```text
Priority Classification
Sentiment Analysis
Reply Generation
```

### Step 4 — Routing

The system routes messages according to their priority.

```text
Low
 ↓
Automatically send generated reply

Medium / High
 ↓
Keep Pending
 ↓
Human Review

Spam
 ↓
Classified as Spam
```

### Step 5 — Human Approval

For pending emails, the user can select and edit an AI-generated response and then approve it.

The frontend sends the final reply to:

```http
POST /api/emails/{email_id}/approve
```

### Step 6 — Send Response

The backend sends the approved response through Gmail SMTP and records the final response and status.

## API Endpoints

### Get Emails

```http
GET /api/emails
```

Returns the stored email records.

### Process Inbox

```http
GET /api/process-emails
```

Fetches emails, processes unassigned messages through the AI model, and performs the appropriate routing action.

### Approve and Send

```http
POST /api/emails/{email_id}/approve
```

Sends the user-approved final reply.

## Email Statuses

Mail-Agent tracks the lifecycle of each processed message using statuses such as:

```text
Pending
Auto-Sent
Approved & Sent
Failed to Send
```

## Example AI Output

```json
{
  "priority": "Medium",
  "sentiment": "Friendly",
  "draft_reply_1": "That sounds great. I'd be happy to proceed.",
  "draft_reply_2": "Thanks for reaching out, but I won't be able to proceed at the moment.",
  "draft_reply_3": "Could you share a few more details about this?"
}
```

## Security

Sensitive credentials should never be hard-coded into the source code.

Store them in `.env` and add the file to `.gitignore`:

```gitignore
.env
emails.db
venv/
__pycache__/
node_modules/
```

## Important Components

### `ai_service.py`

Responsible for sending email content to the local Qwen model and parsing the AI-generated JSON response.

### `database.py`

Defines the SQLAlchemy email schema and initializes the SQLite database.

### `imap_service.py`

Connects to Gmail through IMAP, retrieves messages, decodes headers, extracts email bodies, removes HTML content, and stores new messages.

### `smtp_service.py`

Handles outgoing email delivery through Gmail SMTP.

### `main.py`

Acts as the FastAPI application and coordinates:

```text
Email Fetching
AI Processing
Database Updates
Priority Routing
Human Approval
Email Sending
```

### `App.jsx`

Provides the React dashboard, email list, charts, inbox/spam filtering, review interface, and approval workflow.

## Why Mail-Agent?

Mail-Agent is designed to reduce repetitive email management work by combining:

**Email Automation + Local AI + Smart Classification + Reply Generation + Human Oversight**

Instead of manually reading every message and writing every response, the system provides an AI-assisted workflow while keeping the user in control of important communications.

## Gokul

