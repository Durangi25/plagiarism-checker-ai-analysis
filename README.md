Plagiarism Checker with AI Writing Analysis
A full stack plagiarism checker web application built using React, FastAPI and MySQL. The system allows students and lecturers to upload assignment files or paste text directly, then stores submissions in a local database. Lecturers can generate detailed plagiarism, originality, and AI-writing analysis reports.
---
Project Overview
This project is designed for academic assignment checking. It supports local database based plagiarism detection, assignment submission management and rule based AI writing analysis.
The system uses sentence level TF-IDF and cosine similarity to compare submitted assignments with previously stored assignments. It also estimates whether writing is Human written, AI-generated, or Human+AI mixed using writing-style features.
---
Key Features
Authentication
User Sign Up
User Login
Role selection:
Student
Lecturer
Admin role removed
Student Features
Upload PDF, DOCX and TXT files
Paste assignment text
Paste text limit: 3000 characters
Clear pasted text
View own uploaded files
Delete own uploaded files
Cannot view plagiarism reports
Lecturer Features
Upload PDF, DOCX and TXT files
Paste assignment text
View all uploaded assignments
View uploaded student name
Generate full plagiarism report
View matched sentence details
View AI/Human/Mixed writing analysis
Delete any assignment
Report Features
Plagiarism percentage
Originality percentage
Total words
Matched weighted words
Matched source file
Submitted sentence
Matched sentence
Sentence similarity percentage
Human writing percentage
AI writing percentage
Human + AI mixed percentage
Paragraph-level AI analysis
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
1. Text Extraction
The backend extracts text from uploaded documents.
Supported file types:
PDF
DOCX
TXT
Libraries used:
`PyMuPDF` for PDF text extraction
`python-docx` for DOCX text extraction
UTF-8 decoding for TXT files
---
2. Plagiarism Detection
The system uses sentence-level TF-IDF and cosine similarity.
Process:
Extract assignment text
Clean the text
Split the text into sentences
Compare each sentence with stored assignment sentences
Calculate cosine similarity
Mark sentences as matched if similarity is above the threshold
Calculate plagiarism and originality percentages
Formula
```text
Matched Weighted Words = Sentence Word Count × Similarity Score

Plagiarism Percentage = Matched Weighted Words / Total Words × 100

Originality Percentage = 100 - Plagiarism Percentage
```
---
3. AI Writing Analysis
The system uses a rule-based writing-style estimation method.
Features used:
Average sentence length
Sentence length variation
Word repetition
Vocabulary richness
Connector words
Classification Rule
```text
AI Score >= 70     → AI
AI Score <= 40     → Human
41 to 69           → Human + AI Mixed
```
Percentage Calculation
```text
Human Percentage = Human Words / Total Words × 100

AI Percentage = AI Words / Total Words × 100

Mixed Percentage = Mixed Words / Total Words × 100
```
---
Project Structure
```text
plagiarism-checker/
|
├── backend/
|   ├── main.py
|   └── env/
|
└── frontend/
    ├── src/
    |   ├── App.jsx
    |   └── App.css
    |
    ├── package.json
    └── vite.config.js
```
---
Backend Setup
1. Go to backend folder
```bash
cd backend
```
2. Create virtual environment
```bash
python -m venv env
```
3. Activate virtual environment
For Windows:
```bash
env\Scripts\activate
```
4. Install backend dependencies
```bash
pip install fastapi uvicorn python-multipart pymupdf python-docx mysql-connector-python scikit-learn
```
---
MySQL Setup
The backend can create the database and required tables automatically when it starts.
Database name:
```text
assignment_checker
```
Tables:
```text
users
assignments
```
If manual setup is needed, run this in MySQL Workbench:
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
    user_id INT NULL,
    uploader_name VARCHAR(100),
    uploader_role VARCHAR(50) DEFAULT 'student',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
---
Backend Database Configuration
In `backend/main.py`, update the MySQL password:
```python
DB_NAME = "assignment_checker"
MYSQL_USER = "root"
MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"
```
Replace `YOUR_MYSQL_PASSWORD` with the actual MySQL password.
---
Run Backend
```bash
cd backend
env\Scripts\activate
uvicorn main:app --reload
```
Backend URL:
```text
http://127.0.0.1:8000
```
API documentation:
```text
http://127.0.0.1:8000/docs
```
Database test:
```text
http://127.0.0.1:8000/db-test
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
Frontend URL:
```text
http://localhost:5173
```
---
Main API Endpoints
Method	Endpoint	Description
GET	`/`	Backend running check
GET	`/db-test`	Database connection test
POST	`/signup`	Create student or lecturer account
POST	`/login`	User login
POST	`/upload`	Upload PDF/DOCX/TXT assignment
POST	`/submit-text`	Submit pasted assignment text
GET	`/assignments`	Get assignment list based on role
GET	`/detailed-plagiarism/{id}`	Detailed plagiarism result
GET	`/check-ai/{id}`	AI/Human/Mixed writing analysis
GET	`/full-report/{id}`	Full plagiarism and AI report
DELETE	`/assignments/{id}`	Delete assignment based on permission
---
Testing Flow
Student
Create a Student account
Login
Upload a PDF/DOCX/TXT file or paste text
View own uploaded files
Delete own uploaded files
Lecturer
Create a Lecturer account
Login
Upload or paste assignment text
View all submitted assignments
Click Check Report
View plagiarism, originality, matched sentences, and AI writing analysis
Delete assignments if needed
---
Important Notes
This system checks plagiarism by comparing assignments stored in the local MySQL database.
It does not scan the entire internet.
AI-writing results are estimated using rule-based text analysis.
AI percentage should be used as decision-support, not final academic proof.
Students cannot view plagiarism reports.
Lecturers can view all reports and submissions.
---
Limitations
No internet plagiarism checking
No JWT authentication
No email verification
No PDF report download
No advanced semantic plagiarism model
Local database comparison only
---
Future Improvements
Add online plagiarism checking using a plagiarism API or search API
Add JWT-based authentication
Add PDF report download
Add matched text highlighting
Add lecturer dashboard charts
Add student-wise report history
Add admin panel if required
Add more advanced AI detection model
---
