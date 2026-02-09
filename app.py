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

    # ================= Algorithms =================
    "algorithm": [
        "algorithm", "algorithms", "algoritm", "algoritms",
        "algorthim", "algorthims", "algorhythm", "algorythm",
        "algo", "alg", "algoo", "algorit",
        "analysis of algorithm", "design and analysis of algorithms",
        "daa", "daaa",

        "algorithmz", "algorithims", "algorithem",

        "الالجوريزم", "الالگوريزم", "الالوجريزم",
        "الجواريزم", "الاجوريزم", "الاجوريثم",
        "الخوارزميات", "الخوارزميأت", "الخوارزميات",
        "خوارزميات", "خوارزميه", "خوارزمي",
        "الخوازرميات", "الخوارزمياتت"
    ],

    # ================= Math =================
    "math": [
        "math", "maths", "mathematics", "mathematic",
        "mathemathics", "mathmatic", "mathimatics",
        "applied math", "discrete math",
        "discret math", "descrete math", "disc math",
        "calc", "calculus", "calculs",
        "linear algebra", "lin algebra",

        "ماث", "مات", "ماثس",
        "رياضة", "رياضيات", "رياظيات", "رياضيت",
        "رياضه", "رياضيأت",
        "رياضة متقطعة", "رياضة متقطعه",
        "ديسكريت ماث", "دسكريت ماث", "دسكريت",
        "تفاضل", "تكامل", "جبر"
    ],

    # ================= Data Structures =================
    "ds": [
        "data structure", "data structures",
        "data stucture", "data stracture",
        "data structre", "data sturcture",
        "data strcture", "data strucure",
        "ds", "d.s", "dsa",

        "داتا ستراكشر", "داتا ستركتشر", "داتا ستراكتشر",
        "داتا ستراكتور", "داتا ستركتور",
        "داتا ستراكشرز", "داتاستراكشر",
        "هياكل البيانات", "هياكل البينات",
        "هيكل البيانات", "هيكل الداتا"
    ],

    # ================= Automata / TOC =================
    "automata": [
        "automata", "automatas", "automatta",
        "automata theory", "automata theroy",
        "theory of computation", "theory of computation",
        "theroy of computation", "theory computation",
        "toc", "t.o.c", "tooc",

        "finite automata", "finite automatta",
        "dfa", "nfa", "pda",
        "pushdown automata", "push down automata",
        "turing machine", "turing mashine",

        "اوتوماتا", "أوتوماتا", "اوتوماته",
        "نظرية الحوسبة", "نظرية الحوسبه",
        "نظرية الحسابات",
        "نظرية الالات", "نظريه الالات",
        "لغات شكلية", "لغات شكليه", "لغات صورية"
    ],

    # ================= Artificial Intelligence =================
    "ai": [
        "ai", "a.i", "artificial intelligence",
        "artifical intelligence", "artificial inteligence",
        "artificial intellegence", "artifical inteligence",
        "machine intelligence",
        "intelligent systems",

        "ذكاء اصطناعي", "الذكاء الاصطناعي",
        "الزكاء الاصطناعي", "الذكاء الاصتناعي",
        "ذكاء صناعي", "زكاء اصطناعي",
        "aii", "aie"
    ],

    # ================= Software Engineering =================
    "software": [
        "software", "softwear", "sofware", "soft ware",
        "software engineering", "softwear engineering",
        "sofware engineering", "software eng",
        "se", "s.e",

        "software development", "soft dev",
        "sw development",

        "هندسة البرمجيات", "هندسه البرمجيات",
        "هندسة البرمجات",
        "تطوير البرمجيات", "تطوير البرمجات",
        "سوفت وير", "سوفتوير", "سوفت ويرر"
    ],

    # ================= Image Processing =================
    "image_processing": [
        "image processing", "img processing",
        "image proccessing", "image procesing",
        "image proccesing",
        "digital image processing", "dip",

        "image analysis", "img analysis",

        "معالجة الصور", "معالجه الصور",
        "معالجة الصوره", "معالجة الصورر",
        "معالجة صوره",
        "ديجيتال ايمدج بروسيسنج",
        "ايمدج بروسيسنج"
    ],

    # ================= Computer Vision =================
    "computer_vision": [
        "computer vision", "computer vission",
        "computer vison", "cmp vision",
        "cv", "c.v",

        "machine vision",

        "رؤية الحاسوب", "رؤية الحاسب",
        "رؤية الكمبيوتر", "روية الحاسوب",
        "رؤيه الحاسوب",
        "كمبيوتر فيجن", "كومبيوتر فيجن",
        "كمبيوتر ڤيجن"
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
