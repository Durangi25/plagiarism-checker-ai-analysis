# Plagiarism Checker with AI Writing Analysis

A full-stack plagiarism checker web application built using **React**, **FastAPI**, and **MySQL**. The system allows users to upload assignment files or paste text directly, then generates a report showing plagiarism percentage, originality percentage, and AI/Human/Mixed writing analysis.

---

## Features

- User Sign Up and Login
- Role selection: Student, Lecturer, Admin
- Upload PDF, DOCX, and TXT files
- Paste assignment text directly
- Extract text from uploaded documents
- Store assignment data in MySQL
- Sentence-level plagiarism detection
- Originality percentage calculation
- Matched sentence and source file display
- AI, Human, and Human + AI Mixed writing estimation
- Full report dashboard
- Delete assignment option
- Responsive user interface

---

## Tech Stack

### Frontend
- React
- Vite
- Axios
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- PyMuPDF
- python-docx
- scikit-learn
- Regex
- Hashlib

### Database
- MySQL
- MySQL Workbench
- mysql-connector-python

---

## Methods Used

### Plagiarism Detection

The system uses **sentence-level TF-IDF and Cosine Similarity**.

Process:

1. Extract assignment text
2. Split text into sentences
3. Compare each sentence with stored assignments
4. Detect similar sentences using cosine similarity
5. Calculate matched weighted words
6. Generate plagiarism and originality percentages

Formula:

```text
Matched Weighted Words = Sentence Word Count × Similarity Score

Plagiarism Percentage = Matched Weighted Words / Total Words × 100

Originality Percentage = 100 - Plagiarism Percentage
```

---

### AI Writing Analysis

The AI writing analysis is rule-based and estimates:

- Human-written percentage
- AI-generated percentage
- Human + AI mixed percentage

Features used:

- Average sentence length
- Sentence length variation
- Word repetition
- Vocabulary richness
- Connector words

Classification rule:

```text
AI Score >= 70     → AI
AI Score <= 40     → Human
41 to 69           → Human + AI Mixed
```

---

## Project Structure

```text
plagiarism-checker/
│
├── backend/
│   ├── main.py
│   └── env/
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── App.css
    │
    ├── package.json
    └── vite.config.js
```

---

## Backend Setup

### 1. Create backend environment

```bash
cd backend
python -m venv env
```

### 2. Activate environment

For Windows:

```bash
env\Scripts\activate
```

### 3. Install backend dependencies

```bash
pip install fastapi uvicorn python-multipart pymupdf python-docx mysql-connector-python scikit-learn
```

---

## MySQL Database Setup

Open MySQL Workbench and run:

```sql
CREATE DATABASE IF NOT EXISTS assignment_checker;

USE assignment_checker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    extracted_text LONGTEXT,
    text_length INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Backend Database Configuration

In `backend/main.py`, update the MySQL password:

```python
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="assignment_checker"
    )
```

Replace `YOUR_MYSQL_PASSWORD` with the real MySQL password.

---

## Run Backend

```bash
cd backend
env\Scripts\activate
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

### 1. Go to frontend folder

```bash
cd frontend
```

### 2. Install frontend dependencies

```bash
npm install
npm install axios
```

### 3. Run frontend

```bash
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend running check |
| GET | `/db-test` | Database connection test |
| POST | `/signup` | Create new user |
| POST | `/login` | User login |
| POST | `/upload` | Upload PDF/DOCX/TXT file |
| POST | `/submit-text` | Submit pasted text |
| GET | `/assignments` | Get saved assignments |
| GET | `/detailed-plagiarism/{id}` | Detailed plagiarism report |
| GET | `/check-ai/{id}` | AI/Human/Mixed analysis |
| GET | `/full-report/{id}` | Full report |
| DELETE | `/assignments/{id}` | Delete assignment |

---

## Testing Flow

1. Start MySQL Server
2. Run FastAPI backend
3. Open frontend
4. Sign up or login
5. Upload a file or paste text
6. Upload or paste another similar assignment
7. Click **Check Report**
8. View plagiarism, originality, AI, Human, and Mixed percentages

---

## Important Note

This system compares assignments stored in the local MySQL database. It does not scan the entire internet.

AI-writing results are estimated values based on rule-based text analysis and should be used as decision-support, not as final academic proof.

---

## Future Improvements

- Internet plagiarism checking using plagiarism/search API
- JWT authentication
- Role-based access control
- Student-wise assignment separation
- PDF report download
- Matched text highlighting
- Admin user management
- Dashboard charts

---

## Screenshots

Add project screenshots here:

```text
screenshots/login-page.png
screenshots/dashboard.png
screenshots/report.png
```

---

## Author

Developed as a full-stack academic project using React, FastAPI, MySQL, and NLP-based text similarity methods.
