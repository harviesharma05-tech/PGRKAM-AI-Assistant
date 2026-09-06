from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import re
import unicodedata

app = FastAPI(
    title="PGRKAM AI Smart Assistant",
    version="1.0.0"
)

# For local development. Restrict this to your frontend domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Official/source-based knowledge supplied for this project.
# Do not invent vacancies, dates, eligibility or schemes.
# -------------------------------------------------------------------

KNOWLEDGE_BASE = [
    {
        "service": "Government Jobs",
        "intent": "Government Jobs",
        "information": (
            "PGRKAM facilitates job seekers for placement in government jobs "
            "according to their aptitude and skills."
        ),
        "action": "Guide user to the Government Jobs service.",
    },
    {
        "service": "Private Jobs",
        "intent": "Private Jobs",
        "information": (
            "PGRKAM facilitates job seekers for placement in private jobs "
            "according to their aptitude and skills."
        ),
        "action": "Guide user to the Private Jobs service.",
    },
    {
        "service": "Overseas Employment",
        "intent": "Overseas Employment",
        "information": (
            "PGRKAM facilitates job seekers for placement in overseas employment. "
            "The Foreign Study and Placement Cell facilitates foreign study and "
            "placement for Punjab youth in a fair and transparent manner."
        ),
        "action": "Guide user to the Overseas Employment service.",
    },
    {
        "service": "Foreign Study",
        "intent": "Foreign Study",
        "information": (
            "PGRKAM facilitates Punjab youth in overseas study and related "
            "ancillary activities."
        ),
        "action": "Guide user to the Foreign Study service.",
    },
    {
        "service": "Self Employment",
        "intent": "Self Employment",
        "information": (
            "The Society aims to facilitate wage and self-employment for "
            "unemployed people of Punjab."
        ),
        "action": "Guide user to the Self Employment service.",
    },
    {
        "service": "Skill Training",
        "intent": "Skill Training",
        "information": (
            "PGRKAM aims to improve employability through skill training "
            "and skill up-gradation."
        ),
        "action": "Guide user to the Skill Training service.",
    },
    {
        "service": "Job Melas",
        "intent": "Job Melas",
        "information": (
            "PGRKAM facilitates registration of job seekers and job providers "
            "and organizing job fairs/job melas online."
        ),
        "action": "Guide user to the Job Melas service.",
    },
    {
        "service": "Job Helpline",
        "intent": "Job Helpline",
        "information": (
            "Punjab Job Helpline is intended to reach households and provide "
            "employment facilitation."
        ),
        "action": "Guide user to the Job Helpline.",
    },
    {
        "service": "Counselling and Guidance",
        "intent": "Counselling and Guidance",
        "information": (
            "PGRKAM provides counselling and guidance as part of its "
            "employment-related services."
        ),
        "action": "Guide the user to counselling/help.",
    },
    {
        "service": "Armed Forces",
        "intent": "Armed Forces",
        "information": (
            "PGRKAM provides services related to induction into the armed forces."
        ),
        "action": "Guide the user to the Armed Forces service.",
    },
]

# These are INTERNAL service IDs, not claimed to be real website routes.
# Replace them with official/authorized PGRKAM URLs when integration access exists.
SERVICE_IDS = {
    "Government Jobs": "government_jobs",
    "Private Jobs": "private_jobs",
    "Overseas Employment": "overseas_employment",
    "Foreign Study": "foreign_study",
    "Self Employment": "self_employment",
    "Skill Training": "skill_training",
    "Job Melas": "job_melas",
    "Job Helpline": "job_helpline",
    "Counselling and Guidance": "counselling_guidance",
    "Armed Forces": "armed_forces",
}


class ChatRequest(BaseModel):
    query: str
    profile: Optional[dict] = None


def normalize_query(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def detect_language(query: str) -> str:
    q = query.lower()

    if re.search(r"[\u0A00-\u0A7F]", query):
        return "Punjabi"

    if re.search(r"[\u0900-\u097F]", query):
        return "Hindi"

    # Roman Hindi/Hinglish/Punjabi is detected heuristically.
    if any(word in q.split() for word in [
        "main", "mujhe", "chahta", "chahti", "naukri",
        "sarkari", "videsh", "mein", "karna", "karni",
        "chahiye", "hai", "hoon", "job", "karna"
    ]):
        return "Hinglish"

    if re.search(r"[a-zA-Z]", query):
        return "English"

    return "Other"


def detect_service(query: str) -> str:
    q = normalize_query(query)

    # More specific intents first.
    if any(x in q for x in [
        "dubai", "uae", "abroad", "overseas", "foreign job",
        "work abroad", "work in another country", "विदेश में नौकरी"
    ]):
        return "Overseas Employment"

    if any(x in q for x in [
        "study abroad", "foreign study", "study overseas",
        "विदेश में पढ़ाई", "विदेश में पढ़ना"
    ]):
        return "Foreign Study"

    if any(x in q for x in [
        "government job", "government jobs", "govt job", "govt jobs",
        "sarkari job", "sarkari naukri", "सरकारी नौकरी"
    ]):
        return "Government Jobs"

    if any(x in q for x in [
        "private job", "private jobs", "private naukri",
        "प्राइवेट नौकरी"
    ]):
        return "Private Jobs"

    if any(x in q for x in [
        "self employment", "self-employment", "business",
        "startup", "apna business", "स्वरोजगार"
    ]):
        return "Self Employment"

    if any(x in q for x in [
        "skill training", "skill development", "training", "upskill",
        "कौशल प्रशिक्षण"
    ]):
        return "Skill Training"

    if any(x in q in []):
        return "Job Melas"

    if any(x in q for x in [
        "job mela", "job fair", "रोजगार मेला"
    ]):
        return "Job Melas"

    if any(x in q for x in [
        "army", "navy", "air force", "armed forces", "defence job"
    ]):
        return "Armed Forces"

    if any(x in q for x in [
        "helpline", "job help", "employment help"
    ]):
        return "Job Helpline"

    if any(x in q for x in [
        "counselling", "counseling", "career guidance",
        "career advice", "career help"
    ]):
        return "Counselling and Guidance"

    return "Counselling and Guidance"


def extract_profile(query: str) -> dict:
    q = normalize_query(query)

    profile = {
        "age": None,
        "education": None,
        "location": None,
        "sector": None,
        "goal": None,
    }

    age_match = re.search(
        r"(?:i am|i'm|age is|age|meri age|umar)\s*(?:is|=|:)?\s*(\d{1,2})",
        q
    )
    if age_match:
        age = int(age_match.group(1))
        if 13 <= age <= 100:
            profile["age"] = age

    # Also support "21 years old".
    if profile["age"] is None:
        age_match = re.search(r"\b(\d{1,2})\s*(?:years?|yrs?)\s*old\b", q)
        if age_match:
            age = int(age_match.group(1))
            if 13 <= age <= 100:
                profile["age"] = age

    education_patterns = [
        ("B.Tech", ["b.tech", "btech", "b tech"]),
        ("M.Tech", ["m.tech", "mtech", "m tech"]),
        ("12th", ["12th", "12 th", "class 12", "12 pass", "twelfth"]),
        ("10th", ["10th", "10 th", "class 10", "10 pass", "tenth"]),
        ("Graduate", ["graduate", "graduation"]),
        ("Postgraduate", ["postgraduate", "post graduation"]),
        ("Diploma", ["diploma"]),
    ]

    for education, patterns in education_patterns:
        if any(p in q for p in patterns):
            profile["education"] = education
            break

    if "punjab" in q or "ਪੰਜਾਬ" in query:
        profile["location"] = "Punjab"

    if any(x in q for x in [
        "government", "govt", "sarkari", "सरकारी"
    ]):
        profile["sector"] = "Government"
    elif "private" in q or "प्राइवेट" in query:
        profile["sector"] = "Private"
    elif any(x in q for x in [
        "dubai", "uae", "abroad", "overseas", "foreign"
    ]):
        profile["sector"] = "Overseas"

    if any(x in q for x in [
        "job", "jobs", "naukri", "employment", "work", "नौकरी", "रोजगार"
    ]):
        profile["goal"] = "Employment"
    elif any(x in q for x in [
        "business", "startup", "self employment", "स्वरोजगार"
    ]):
        profile["goal"] = "Self Employment"

    return profile


def merge_profile(old: dict, new: dict) -> dict:
    merged = dict(old or {})
    for key in ["age", "education", "location", "sector", "goal"]:
        if new.get(key) is not None:
            merged[key] = new[key]
        elif key not in merged:
            merged[key] = None
    return merged


def get_service_info(service: str) -> dict:
    for item in KNOWLEDGE_BASE:
        if item["service"] == service:
            return item
    return KNOWLEDGE_BASE[-1]


def score_services(query: str, profile: dict, detected_service: str):
    q = normalize_query(query)
    results = []

    for item in KNOWLEDGE_BASE:
        score = 0.0
        service = item["service"]

        if service == detected_service:
            score += 1.0

        # Lightweight deterministic relevance layer.
        if service == "Government Jobs" and any(
            x in q for x in ["government", "govt", "sarkari", "सरकारी"]
        ):
            score += 0.35

        if service == "Private Jobs" and "private" in q:
            score += 0.35

        if service == "Overseas Employment" and any(
            x in q for x in ["dubai", "uae", "abroad", "overseas", "foreign job"]
        ):
            score += 0.35

        if service == "Foreign Study" and any(
            x in q for x in ["study abroad", "foreign study", "study overseas"]
        ):
            score += 0.35

        if service == "Self Employment" and any(
            x in q for x in ["business", "startup", "self employment", "स्वरोजगार"]
        ):
            score += 0.35

        if service == "Skill Training" and any(
            x in q for x in ["training", "skill", "upskill"]
        ):
            score += 0.35

        if service == "Job Melas" and any(
            x in q for x in ["job mela", "job fair", "रोजगार मेला"]
        ):
            score += 0.35

        if service == "Armed Forces" and any(
            x in q for x in ["army", "navy", "air force", "armed forces"]
        ):
            score += 0.35

        if service == "Job Helpline" and "helpline" in q:
            score += 0.35

        if service == "Counselling and Guidance" and any(
            x in q for x in ["counselling", "counseling", "guidance", "career advice"]
        ):
            score += 0.35

        # Profile relevance.
        if profile.get("sector") == "Government" and service == "Government Jobs":
            score += 0.12

        if profile.get("sector") == "Private" and service == "Private Jobs":
            score += 0.12

        if profile.get("sector") == "Overseas" and service == "Overseas Employment":
            score += 0.12

        results.append({
            "service": service,
            "score": round(score, 3),
            "reason": item["information"],
            "action": item["action"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def make_navigation(service: str) -> dict:
    # Internal ID only. The frontend uses it as a service target.
    return {
        "service": service,
        "service_id": SERVICE_IDS.get(service, "services"),
        "type": "service_target",
    }


def create_answer(service: str, profile: dict, info: dict) -> str:
    age = profile.get("age")
    education = profile.get("education")

    lines = [
        f"Relevant Service: {service}",
        "",
        f"PGRKAM's {service} service is the most relevant option based on your query.",
    ]

    if age is not None or education is not None:
        lines += [
            "",
            "Your Profile:",
            f"Age: {age if age is not None else 'Not provided'}",
            f"Qualification: {education if education is not None else 'Not provided'}",
        ]

    lines += [
        "",
        info["information"],
        "",
        f"Next Step: {info['action']}",
        "",
        "For specific vacancies, dates or eligibility, verify the latest official PGRKAM information and official notification."
    ]

    return "\n".join(lines)


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "PGRKAM AI Smart Assistant",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):
    query = request.query.strip()

    if not query:
        return {
            "status": "error",
            "message": "Please enter a query."
        }

    previous_profile = request.profile or {}
    new_profile = extract_profile(query)
    profile = merge_profile(previous_profile, new_profile)

    detected_service = detect_service(query)
    recommendations = score_services(
        query,
        profile,
        detected_service
    )

    best = recommendations[0]
    info = get_service_info(best["service"])

    # Conservative confidence label.
    if best["score"] >= 1.20:
        confidence = "High"
    elif best["score"] >= 0.70:
        confidence = "Medium"
    else:
        confidence = "Low"

    # If confidence is low, do not pretend to know the answer.
    if confidence == "Low":
        answer = (
            "I'm not confident enough to recommend a specific option. "
            "Please use PGRKAM counselling/help for guidance."
        )
    else:
        answer = create_answer(
            best["service"],
            profile,
            info
        )

    return {
        "status": "success",
        "language": detect_language(query),
        "intent": detected_service,
        "service": best["service"],
        "recommended_service": best["service"],
        "confidence": confidence,
        "match_score": best["score"],
        "profile": profile,
        "reason": best["reason"],
        "next_action": best["action"],
        "navigation": make_navigation(best["service"]),
        "recommendations": recommendations[:3],
        "answer": answer,
    }
