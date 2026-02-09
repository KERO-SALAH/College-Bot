import os
import re
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ======================
# App
# ======================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "data", "files")

# ======================
# Helpers
# ======================

# كل أسماء المواد واحتمالات كتابتها
SUBJECTS = {
    "algorithm": [
        "algorithm", "algorithms", "algo",
        "الالجوريزم", "الخوارزميات", "خوارزميات"
    ],
    "math": [
        "math", "mathematics", "ماث", "رياضة", "رياضيات"
    ],
    "ds": [
        "data structure", "ds",
        "داتا ستراكشر", "هياكل البيانات"
    ]
}

# تحويل الأرقام المكتوبة
ORDINALS = {
    1: ["1", "one", "first", "الأولى", "الاولى", "اولى"],
    2: ["2", "two", "second", "الثانية", "الثانيه"],
    3: ["3", "three", "third", "الثالثة", "الثالثه"],
    4: ["4", "four", "الرابعة", "الرابعه"],
    5: ["5", "five", "الخامسة", "الخامسه"]
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())

def extract_subject(text: str):
    for subject, keywords in SUBJECTS.items():
        for k in keywords:
            if k in text:
                return subject
    return None

def extract_lecture_number(text: str):
    # 1️⃣ دور على رقم صريح (10, 12, 3 ...)
    match = re.search(r"\b(\d{1,2})\b", text)
    if match:
        return int(match.group(1))

    # 2️⃣ لو مفيش رقم، دور على كلمات (الأولى – الثانية – first ...)
    for number, keywords in ORDINALS.items():
        for k in keywords:
            if re.search(rf"\b{k}\b", text):
                return number

    return None

def extract_type(text: str):
    if "محاضرة" in text or "lecture" in text:
        return "lecture"
    return None

def find_matching_file(subject, lecture_number):
    if not subject or not lecture_number:
        return None

    for file in os.listdir(FILES_DIR):
        name = file.lower()
        if (
            subject in name and
            f"lecture_{lecture_number}" in name
        ):
            return file
    return None

# ======================
# API
# ======================

class RequestBody(BaseModel):
    message: str

@app.post("/request")
def handle_request(body: RequestBody):
    text = normalize(body.message)

    subject = extract_subject(text)
    lecture_number = extract_lecture_number(text)
    lecture_type = extract_type(text)

    if not subject:
        return {
            "type": "error",
            "message": "مش فاهم اسم المادة 😕 (مثال: algorithm / math)"
        }

    if not lecture_number:
        return {
            "type": "error",
            "message": "مش فاهم رقم المحاضرة 😕 (مثال: الأولى / 1 / first)"
        }

    file = find_matching_file(subject, lecture_number)

    if not file:
        return {
            "type": "error",
            "message": f"محاضرة {lecture_number} لمادة {subject} مش موجودة."
        }

    return {
        "type": "file",
        "message": f"تمام ✅ دي محاضرة {lecture_number} من مادة {subject}",
        "download_url": f"/file/{file}"
    }

@app.get("/file/{filename}")
def get_file(filename: str):
    path = os.path.join(FILES_DIR, filename)

    if not os.path.exists(path):
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )

    return FileResponse(path, filename=filename)
