Plagiarism Checker with AI Writing Analysis

A full-stack plagiarism checker web application built using React, FastAPI, and MySQL. The system allows users to upload assignment files or paste text directly, then generates a report showing plagiarism percentage, originality percentage, and AI/Human/Mixed writing analysis.
---
Features
User Sign Up and Login
Role selection: Student, Lecturer, Admin
Upload PDF, DOCX, and TXT files
Paste assignment text directly
Extract text from uploaded documents
Store assignment data in MySQL
Sentence-level plagiarism detection
Originality percentage calculation
Matched sentence and source file display
AI, Human, and Human + AI Mixed writing estimation
Full report dashboard
Delete assignment option
Responsive user interface
---
Tech Stack
Frontend
React
Vite
Axios
CSS
Backend
Python
FastAPI
Uvicorn
PyMuPDF
python-docx
scikit-learn
Regex
Hashlib
Database
MySQL
MySQL Workbench
mysql-connector-python
---
Methods Used
Plagiarism Detection
The system uses sentence-level TF-IDF and Cosine Similarity.
Process:
Extract assignment text
Split text into sentences
Compare each sentence with stored assignments
Detect similar sentences using cosine similarity
Calculate matched weighted words
Generate plagiarism and originality percentages
Formula:
```text
Matched Weighted Words = Sentence Word Count × Similarity Score

Plagiarism Percentage = Matched Weighted Words / Total Words × 100

Originality Percentage = 100 - Plagiarism Percentage
```
---
AI Writing Analysis
The AI writing analysis is rule-based and estimates:
Human-written percentage
AI-generated percentage
Human + AI mixed percentage
Features used:
Average sentence length
Sentence length variation
Word repetition
Vocabulary richness
Connector words
Classification rule:
```text
AI Score >= 70     → AI
AI Score <= 40     → Human
41 to 69           → Human + AI Mixed
```
---
Project Structure
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
Backend Setup
1. Create backend environment
```bash
cd backend
python -m venv env
```
2. Activate environment
For Windows:
```bash
env\\Scripts\\activate
```
3. Install backend dependencies
```bash
pip install fastapi uvicorn python-multipart pymupdf python-docx mysql-connector-python scikit-learn
```
---
MySQL Database Setup
Open MySQL Workbench and run:
```sql
CREATE DATABASE IF NOT EXISTS assignment\_checker;

USE assignment\_checker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO\_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    password\_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO\_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    extracted\_text LONGTEXT,
    text\_length INT,
    uploaded\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP
);
```
---
Backend Database Configuration
In `backend/main.py`, update the MySQL password:
```python
def get\_db\_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="YOUR\_MYSQL\_PASSWORD",
        database="assignment\_checker"
    )
```
Replace `YOUR\_MYSQL\_PASSWORD` with the real MySQL password.
---
Run Backend
```bash
cd backend
env\\Scripts\\activate
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
Frontend Setup
1. Go to frontend folder
```bash
cd frontend
```
2. Install frontend dependencies
```bash
npm install
npm install axios
```
3. Run frontend
```bash
npm run dev
```
Frontend runs on:
```text
http://localhost:5173
```
---
Main API Endpoints
Method	Endpoint	Description
GET	`/`	Backend running check
GET	`/db-test`	Database connection test
POST	`/signup`	Create new user
POST	`/login`	User login
POST	`/upload`	Upload PDF/DOCX/TXT file
POST	`/submit-text`	Submit pasted text
GET	`/assignments`	Get saved assignments
GET	`/detailed-plagiarism/{id}`	Detailed plagiarism report
GET	`/check-ai/{id}`	AI/Human/Mixed analysis
GET	`/full-report/{id}`	Full report
DELETE	`/assignments/{id}`	Delete assignment
---
Testing Flow
Start MySQL Server
Run FastAPI backend
Open frontend
Sign up or login
Upload a file or paste text
Upload or paste another similar assignment
Click Check Report
View plagiarism, originality, AI, Human, and Mixed percentages
---
Important Note
This system compares assignments stored in the local MySQL database. It does not scan the entire internet.
AI-writing results are estimated values based on rule-based text analysis and should be used as decision-support, not as final academic proof.
---
Future Improvements
Internet plagiarism checking using plagiarism/search API
JWT authentication
Role-based access control
Student-wise assignment separation
PDF report download
Matched text highlighting
Admin user management
Dashboard charts
