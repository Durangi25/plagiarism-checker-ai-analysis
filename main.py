from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import fitz
from docx import Document
from io import BytesIO
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter
import hashlib
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3308,
        user="root",
        password="1234",
        database="assignment_checker"
    )


def create_required_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(150) UNIQUE,
            password_hash VARCHAR(255),
            role VARCHAR(50) DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            extracted_text LONGTEXT,
            text_length INT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.on_event("startup")
def startup_event():
    create_required_tables()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"


class LoginRequest(BaseModel):
    email: str
    password: str


class TextSubmissionRequest(BaseModel):
    title: str
    text: str


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return f"{salt}:{password_hash}"


def verify_password(password, stored_password):
    try:
        salt, stored_hash = stored_password.split(":")
        new_hash = hash_password(password, salt).split(":")[1]
        return new_hash == stored_hash
    except Exception:
        return False


@app.get("/")
def home():
    return {"message": "Plagiarism Checker Backend Running"}


@app.get("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        conn.close()
        return {"message": "Database connected successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/signup")
def signup_user(user: SignupRequest):
    if len(user.name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Name must have at least 2 characters"
        )

    if len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must have at least 6 characters"
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        password_hash = hash_password(user.password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (
            user.name.strip(),
            user.email.strip().lower(),
            password_hash,
            user.role.lower()
        ))

        conn.commit()
        user_id = cursor.lastrowid

        return {
            "message": "User created successfully",
            "user": {
                "id": user_id,
                "name": user.name.strip(),
                "email": user.email.strip().lower(),
                "role": user.role.lower()
            }
        }

    except mysql.connector.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please use another email."
        )

    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"MySQL error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Signup error: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.post("/login")
def login_user(user: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email, password_hash, role
        FROM users
        WHERE email = %s
    """, (user.email.strip().lower(),))

    db_user = cursor.fetchone()

    cursor.close()
    conn.close()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"],
            "role": db_user["role"]
        }
    }


def extract_text_from_pdf(file_bytes):
    text = ""
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf_document:
        text += page.get_text()

    pdf_document.close()
    return text


def extract_text_from_docx(file_bytes):
    text = ""
    document = Document(BytesIO(file_bytes))

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_text_from_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore")


def save_assignment(filename, extracted_text):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assignments (filename, extracted_text, text_length)
        VALUES (%s, %s, %s)
    """, (filename, extracted_text, len(extracted_text)))

    conn.commit()
    assignment_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return assignment_id


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()
    filename_lower = file.filename.lower()

    if filename_lower.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx"):
        extracted_text = extract_text_from_docx(file_bytes)
    elif filename_lower.endswith(".txt"):
        extracted_text = extract_text_from_txt(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are allowed"
        )

    if extracted_text.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="No text found in the uploaded file"
        )

    assignment_id = save_assignment(file.filename, extracted_text)

    return {
        "message": "File uploaded and saved successfully",
        "assignment_id": assignment_id,
        "filename": file.filename,
        "text_length": len(extracted_text),
        "extracted_text_preview": extracted_text[:1000]
    }


@app.post("/submit-text")
def submit_text_assignment(request: TextSubmissionRequest):
    if request.text.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Assignment text cannot be empty"
        )

    if len(request.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Please enter at least 50 characters for better checking accuracy"
        )

    filename = request.title.strip() or "Pasted Assignment"
    assignment_id = save_assignment(filename, request.text)

    return {
        "message": "Text submitted and saved successfully",
        "assignment_id": assignment_id,
        "filename": filename,
        "text_length": len(request.text),
        "extracted_text_preview": request.text[:1000]
    }


@app.get("/assignments")
def get_assignments():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, text_length, uploaded_at
        FROM assignments
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": row[0],
            "filename": row[1],
            "text_length": row[2],
            "uploaded_at": str(row[3])
        }
        for row in rows
    ]


def get_assignment_by_id(assignment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, extracted_text
        FROM assignments
        WHERE id = %s
    """, (assignment_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row


def get_other_assignments(assignment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, extracted_text
        FROM assignments
        WHERE id != %s
    """, (assignment_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def count_words(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return len(words)


def calculate_sentence_similarity(sentence1, sentence2):
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([sentence1, sentence2])

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return similarity

    except Exception:
        return 0


@app.get("/detailed-plagiarism/{assignment_id}")
def detailed_plagiarism_check(assignment_id: int):
    current_assignment = get_assignment_by_id(assignment_id)

    if current_assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    current_id = current_assignment[0]
    current_filename = current_assignment[1]
    current_text = current_assignment[2]

    total_words = count_words(current_text)

    if total_words == 0:
        raise HTTPException(
            status_code=400,
            detail="No readable text found"
        )

    other_assignments = get_other_assignments(assignment_id)

    if len(other_assignments) == 0:
        return {
            "assignment_id": current_id,
            "filename": current_filename,
            "total_words": total_words,
            "matched_words": 0,
            "plagiarism_percentage": 0,
            "originality_percentage": 100,
            "matched_assignment_id": None,
            "matched_filename": None,
            "matched_sources": [],
            "message": "No other assignments available for comparison"
        }

    current_sentences = split_sentences(current_text)

    matched_weighted_words = 0
    matched_sources = []

    similarity_threshold = 0.70

    for current_sentence in current_sentences:
        current_sentence_clean = clean_text(current_sentence)
        sentence_word_count = count_words(current_sentence_clean)

        if sentence_word_count < 5:
            continue

        best_match = None
        best_score = 0

        for other_assignment in other_assignments:
            other_id = other_assignment[0]
            other_filename = other_assignment[1]
            other_text = other_assignment[2]

            other_sentences = split_sentences(other_text)

            for other_sentence in other_sentences:
                other_sentence_clean = clean_text(other_sentence)

                if count_words(other_sentence_clean) < 5:
                    continue

                score = calculate_sentence_similarity(
                    current_sentence_clean,
                    other_sentence_clean
                )

                if score > best_score:
                    best_score = score
                    best_match = {
                        "matched_assignment_id": other_id,
                        "matched_filename": other_filename,
                        "submitted_sentence": current_sentence,
                        "matched_sentence": other_sentence,
                        "similarity_percentage": round(score * 100, 2)
                    }

        if best_match and best_score >= similarity_threshold:
            weighted_words = sentence_word_count * best_score
            matched_weighted_words += weighted_words

            best_match["matched_words"] = round(weighted_words, 2)
            best_match["sentence_word_count"] = sentence_word_count

            matched_sources.append(best_match)

    plagiarism_percentage = round((matched_weighted_words / total_words) * 100, 2)
    originality_percentage = round(100 - plagiarism_percentage, 2)

    if len(matched_sources) > 0:
        top_match = max(matched_sources, key=lambda item: item["similarity_percentage"])
    else:
        top_match = None

    return {
        "assignment_id": current_id,
        "filename": current_filename,
        "total_words": total_words,
        "matched_words": round(matched_weighted_words, 2),
        "plagiarism_percentage": plagiarism_percentage,
        "originality_percentage": originality_percentage,
        "matched_assignment_id": top_match["matched_assignment_id"] if top_match else None,
        "matched_filename": top_match["matched_filename"] if top_match else None,
        "matched_sources": matched_sources[:20],
        "message": "Detailed plagiarism check completed"
    }


@app.get("/check-plagiarism/{assignment_id}")
def check_plagiarism(assignment_id: int):
    return detailed_plagiarism_check(assignment_id)


def split_paragraphs(text):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return paragraphs if paragraphs else [text]


def calculate_ai_score(paragraph):
    sentences = re.split(r'[.!?]+', paragraph)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = re.findall(r'\b[a-zA-Z]+\b', paragraph.lower())

    if len(words) < 20:
        return 50

    total_words = len(words)
    total_sentences = max(len(sentences), 1)

    average_sentence_length = total_words / total_sentences
    vocabulary_richness = len(set(words)) / total_words

    word_counts = Counter(words)
    repeated_words = sum(count for count in word_counts.values() if count > 1)
    repetition_ratio = repeated_words / total_words

    sentence_lengths = []

    for sentence in sentences:
        sentence_words = re.findall(r'\b[a-zA-Z]+\b', sentence)
        sentence_lengths.append(len(sentence_words))

    if len(sentence_lengths) > 1:
        mean_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum(
            (length - mean_length) ** 2
            for length in sentence_lengths
        ) / len(sentence_lengths)
    else:
        variance = 0

    ai_score = 50

    if 18 <= average_sentence_length <= 30:
        ai_score += 15

    if variance < 25:
        ai_score += 15

    if repetition_ratio > 0.35:
        ai_score += 10

    if vocabulary_richness > 0.60:
        ai_score -= 10

    if average_sentence_length < 10:
        ai_score -= 15

    if variance > 80:
        ai_score -= 15

    ai_connector_words = [
        "furthermore",
        "moreover",
        "therefore",
        "in conclusion",
        "additionally",
        "overall",
        "significantly"
    ]

    paragraph_lower = paragraph.lower()
    connector_count = 0

    for connector in ai_connector_words:
        if connector in paragraph_lower:
            connector_count += 1

    if connector_count >= 2:
        ai_score += 10

    return max(0, min(100, ai_score))


def classify_paragraph(paragraph):
    ai_score = calculate_ai_score(paragraph)

    if ai_score >= 70:
        return "AI", ai_score
    elif ai_score <= 40:
        return "Human", ai_score
    else:
        return "Mixed", ai_score


@app.get("/check-ai/{assignment_id}")
def check_ai_percentage(assignment_id: int):
    assignment = get_assignment_by_id(assignment_id)

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    assignment_id = assignment[0]
    filename = assignment[1]
    text = assignment[2]

    paragraphs = split_paragraphs(text)

    human_words = 0
    ai_words = 0
    mixed_words = 0
    total_words = 0
    paragraph_results = []

    for paragraph in paragraphs:
        words = re.findall(r'\b[a-zA-Z]+\b', paragraph)
        word_count = len(words)

        if word_count == 0:
            continue

        label, ai_score = classify_paragraph(paragraph)

        total_words += word_count

        if label == "Human":
            human_words += word_count
        elif label == "AI":
            ai_words += word_count
        else:
            mixed_words += word_count

        paragraph_results.append({
            "paragraph_preview": paragraph[:150],
            "word_count": word_count,
            "classification": label,
            "ai_score": round(ai_score, 2)
        })

    if total_words == 0:
        raise HTTPException(
            status_code=400,
            detail="No readable text found"
        )

    human_percentage = round((human_words / total_words) * 100, 2)
    ai_percentage = round((ai_words / total_words) * 100, 2)
    mixed_percentage = round((mixed_words / total_words) * 100, 2)

    return {
        "assignment_id": assignment_id,
        "filename": filename,
        "total_words": total_words,
        "human_percentage": human_percentage,
        "ai_percentage": ai_percentage,
        "human_ai_mixed_percentage": mixed_percentage,
        "message": "AI writing analysis completed",
        "paragraph_results": paragraph_results[:10],
        "note": "AI percentage is an estimated value, not final proof."
    }


@app.get("/full-report/{assignment_id}")
def full_report(assignment_id: int):
    plagiarism_result = detailed_plagiarism_check(assignment_id)
    ai_result = check_ai_percentage(assignment_id)

    return {
        "assignment_id": assignment_id,
        "plagiarism_result": plagiarism_result,
        "ai_writing_result": ai_result,
        "message": "Full report generated successfully"
    }


@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM assignments
        WHERE id = %s
    """, (assignment_id,))

    assignment = cursor.fetchone()

    if assignment is None:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    cursor.execute("""
        DELETE FROM assignments
        WHERE id = %s
    """, (assignment_id,))

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Assignment deleted successfully",
        "assignment_id": assignment_id
    }