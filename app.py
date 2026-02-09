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
# SUBJECTS (FULL)
# ======================
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
        "الخوازرميات", "الخوارزمياتت",
        "تحليل الخوارزميات", "تصميم وتحليل الخوارزميات",
        "الجو", "algo"
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
        "theory of computation", "theroy of computation",
        "toc", "t.o.c", "tooc", "auto",

        "finite automata", "dfa", "nfa", "pda",
        "pushdown automata", "turing machine",

        "اوتوماتا", "أوتوماتا", "اوتوماته",
        "نظرية الحوسبة", "نظرية الحوسبه",
        "نظرية الحسابات", "نظرية الالات",
        "لغات شكلية", "لغات صورية"
    ],

    # ================= Artificial Intelligence =================
    "ai": [
        "ai", "a.i", "artificial intelligence",
        "artifical intelligence", "artificial inteligence",
        "machine intelligence", "intelligent systems",

        "ذكاء اصطناعي", "الذكاء الاصطناعي",
        "الزكاء الاصطناعي", "الذكاء الاصتناعي",
        "ذكاء صناعي", "زكاء اصطناعي",
        "aii", "aie"
    ],

    # ================= Software Engineering =================
    "software": [
        "software", "softwear", "sofware", "soft ware",
        "software engineering", "softwear engineering",
        "software eng", "se", "s.e",

        "software development", "sw development",

        "هندسة البرمجيات", "هندسه البرمجيات",
        "هندسة البرمجات",
        "تطوير البرمجيات", "تطوير البرمجات",
        "سوفت وير", "سوفتوير"
    ],

    # ================= Image Processing =================
    "image_processing": [
        "image processing", "img processing",
        "image proccessing", "image procesing",
        "digital image processing", "dip", "ip",

        "image analysis", "img analysis",

        "معالجة الصور", "معالجه الصور",
        "معالجة الصوره", "معالجة الصورر",
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
        "كمبيوتر فيجن", "كومبيوتر فيجن"
    ]
}

# ======================
# NUMBER NORMALIZATION
# ======================
ARABIC_DIGITS = {
    "٠": "0","١": "1","٢": "2","٣": "3","٤": "4",
    "٥": "5","٦": "6","٧": "7","٨": "8","٩": "9"
}

ORDINAL_WORDS = {
    10: ["العاشرة","عاشر","ten","tenth","x"],
    9: ["التاسعة","تاسع","nine","ninth"],
    8: ["الثامنة","ثامن","eight","eighth"],
    7: ["السابعة","سابع","seven","seventh"],
    6: ["السادسة","سادس","six","sixth"],
    5: ["الخامسة","خامس","five","fifth"],
    4: ["الرابعة","رابع","four","fourth"],
    3: ["الثالثة","ثالث","three","third"],
    2: ["الثانية","ثاني","two","second"],
    1: ["الأولى","اولى","أولى","first","one"]
}

# ======================
# HELPERS
# ======================
def normalize(text: str) -> str:
    text = text.lower()
    for ar, en in ARABIC_DIGITS.items():
        text = text.replace(ar, en)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_subject(text: str):
    for subject, keywords in SUBJECTS.items():
        for k in keywords:
            if k in text:
                return subject
    return None

def extract_lecture_number(text: str):
    # 1. أولاً: ابحث عن الكلمات النصية (العاشرة، العاشرة، إلخ) 
    # لأنها أكثر تحديداً ولن تختلط مع الأرقام العادية
    for num in sorted(ORDINAL_WORDS.keys(), reverse=True):
        for word in ORDINAL_WORDS[num]:
            if re.search(rf"\b{word}\b", text):
                return num

    # 2. ثانياً: ابحث عن الأرقام (1, 2, 10...)
    # استخدمنا \b لضمان أن الرقم يقف وحده (Word Boundary)
    # واستخدمنا (?:...) لعدم التقاط الرقم جزئياً
    match = re.search(r"\b([1-9][0-9]?)\b", text)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 50:
            return num
            
    return None

def find_matching_file(subject, lecture_number):
    if not subject or not lecture_number:
        return None

    pattern = re.compile(
        rf"{re.escape(subject)}_lecture_{lecture_number}\b"
    )

    for file in os.listdir(FILES_DIR):
        name = file.lower()
        if pattern.search(name):
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

    if not subject:
        return {"type": "error", "message": "مش فاهم اسم المادة 😕"}

    if not lecture_number:
        return {"type": "error", "message": "مش فاهم رقم المحاضرة 😕"}

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
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(path, filename=filename)

@app.get("/")
def home():
    return {"status": "College Bot API is running"}
