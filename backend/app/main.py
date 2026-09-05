from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware
from app.job_matcher import rank_jobs
from app.database import SessionLocal
from app.models import UserProfile as UserProfileModel
import sqlite3
import re
import json
import os

from app.gemini_service import ask_gemini
from app.adzuna_service import search_jobs


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Job Finder",
    description="AI-powered job and career assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_NAME = os.path.join(
    os.path.dirname(__file__),
    "ai_job_finder.db"
)


def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # Existing practice table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_role TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score REAL NOT NULL,
            user_answer TEXT NOT NULL
        )
    """)

    # New user profile table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience REAL NOT NULL,
            location TEXT NOT NULL,
            preferred_role TEXT NOT NULL,
            expected_salary TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Make sure database/tables exist
init_database()


# ============================================================
# REQUEST MODELS
# ============================================================

class AIRequest(BaseModel):
    prompt: str


class CareerProfile(BaseModel):
    name: str
    education: str
    experience: str
    skills: list[str]
    location: str
    preferred_role: str
    expected_salary: str


class UserProfile(BaseModel):
    name: str
    skills: list[str]
    experience: Literal[
        "Fresher",
        "0-1 Year",
        "1-2 Years",
        "2-3 Years",
        "3-5 Years",
        "5-10 Years",
        "10+ Years",
    ]
    location: str
    preferred_role: str
    expected_salary: str


class SkillGapRequest(BaseModel):
    skills: list[str]
    target_role: str
    experience: str


class TrainingRequest(BaseModel):
    skill: str
    level: str = "Beginner"


class TrainingPlanRequest(BaseModel):
    current_skills: list[str]
    missing_skills: list[str]
    target_role: str
    experience: str
    available_hours_per_week: int


class DailyTrainingRequest(BaseModel):
    target_role: str
    current_skills: list[str]
    missing_skills: list[str]
    day_number: int
    topic: str
    experience: str


class PracticeGenerateRequest(BaseModel):
    target_role: str
    topic: str
    difficulty: str
    number_of_questions: int


class PracticeEvaluateRequest(BaseModel):
    target_role: str
    topic: str
    question: str
    user_answer: str
    difficulty: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "success": True,
        "message": "AI Job Finder API is running"
    }


# ============================================================
# GEMINI AI TEST
# ============================================================

@app.post("/api/ai/test")
def ai_test(request: AIRequest):

    answer = ask_gemini(request.prompt)

    return {
        "success": True,
        "response": answer
    }


# ============================================================
# CAREER PROFILE ANALYSIS
# ============================================================

@app.post("/api/profile/analyze")
def analyze_profile(profile: CareerProfile):

    prompt = f"""
You are an expert AI Career Coach.

Analyze the following candidate profile.

Candidate Name:
{profile.name}

Education:
{profile.education}

Experience:
{profile.experience}

Skills:
{", ".join(profile.skills)}

Location:
{profile.location}

Preferred Job Role:
{profile.preferred_role}

Expected Salary:
{profile.expected_salary}

Provide the analysis in simple and practical language.

Give the following sections:

1. Candidate Summary
2. Best Suitable Job Roles
3. Strong Skills
4. Skills That Need Improvement
5. Recommended Skills to Learn
6. Career Growth Suggestions
7. How to Reach a Better Salary Package
8. Suggested Learning Roadmap
"""

    answer = ask_gemini(prompt)

    return {
        "success": True,
        "candidate": profile.name,
        "career_analysis": answer
    }


# ============================================================
# SKILL GAP ANALYSIS + PERSONALIZED LEARNING ROADMAP
# ============================================================

@app.post("/api/skill-gap/analyze")
def analyze_skill_gap(request: SkillGapRequest):

    prompt = f"""
You are an expert technical career coach.

Analyze the candidate's current skills against the target job role.

Current Skills:
{", ".join(request.skills)}

Target Job Role:
{request.target_role}

Experience:
{request.experience}

Create a practical and realistic Skill Gap Analysis.

Return ONLY valid JSON in exactly this structure:

{{
    "current_skills": [],
    "missing_skills": [],
    "high_priority_skills": [],
    "medium_priority_skills": [],
    "strong_skills": [],
    "learning_order": [
        {{
            "step": 1,
            "skill": "",
            "reason": "",
            "estimated_time": ""
        }}
    ],
    "practical_projects": [
        {{
            "project": "",
            "skills": [],
            "description": ""
        }}
    ],
    "interview_topics": [],
    "estimated_training_path": ""
}}

Rules:

- Do not assume the candidate knows skills that are not listed.
- current_skills must contain only skills provided by the candidate.
- missing_skills should contain important skills required for the target role.
- high_priority_skills should be the most important missing skills.
- medium_priority_skills should be useful but less urgent.
- strong_skills should contain skills from the candidate that are already useful for the target role.
- learning_order must be practical and sequential.
- Each learning step should contain an estimated learning time.
- practical_projects should help the candidate gain job-ready experience.
- interview_topics should contain important interview preparation areas.
- estimated_training_path should be a short practical summary.
- Keep everything simple and realistic.
- Return JSON only.
"""

    try:

        answer = ask_gemini(prompt)

        clean_response = answer.strip()

        # Remove markdown code fences
        if clean_response.startswith("```"):
            clean_response = re.sub(
                r"```(?:json)?",
                "",
                clean_response,
                flags=re.IGNORECASE
            ).strip()

        if clean_response.endswith("```"):
            clean_response = clean_response[:-3].strip()

        result = json.loads(clean_response)

        return {
            "success": True,
            "target_role": request.target_role,
            "experience": request.experience,
            "skill_gap_analysis": result,
            "gemini_used": True
        }

    except Exception as error:

        print("Gemini Skill Gap analysis unavailable.")
        print("Gemini error:", error)

        # ----------------------------------------------------
        # Safe fallback
        # ----------------------------------------------------

        return {
            "success": True,
            "target_role": request.target_role,
            "experience": request.experience,
            "skill_gap_analysis": {
                "current_skills": request.skills,
                "missing_skills": [],
                "high_priority_skills": [],
                "medium_priority_skills": [],
                "strong_skills": request.skills,
                "learning_order": [],
                "practical_projects": [],
                "interview_topics": [],
                "estimated_training_path":
                    "AI analysis is temporarily unavailable. "
                    "Please try again later."
            },
            "gemini_used": False
        }

# ============================================================
# TRAINING PLAN
# ============================================================

@app.post("/api/training/plan")
def create_training_plan(request: TrainingPlanRequest):

    prompt = f"""
You are an expert AI technical trainer and career coach.

Create a personalized training plan for this candidate.

Target Job Role:
{request.target_role}

Current Skills:
{", ".join(request.current_skills)}

Missing Skills:
{", ".join(request.missing_skills)}

Experience:
{request.experience}

Available Study Time:
{request.available_hours_per_week} hours per week

Create a practical training plan based ONLY on the skills and information provided.

Use these sections:

1. Training Goal
2. Current Skill Level
3. Priority Skills to Learn
4. Week-by-Week Training Plan
5. Daily Learning Activities
6. Practical Projects
7. Practice Questions
8. Interview Preparation
9. Weekly Progress Check
10. Final Job-Readiness Checklist
"""

    answer = ask_gemini(prompt)

    return {
        "success": True,
        "target_role": request.target_role,
        "training_plan": answer
    }


# ============================================================
# DAILY TRAINING
# ============================================================

@app.post("/api/training/daily")
def create_daily_training(request: DailyTrainingRequest):

    prompt = f"""
You are an expert AI technical trainer.

Create today's personalized learning session.

Target Job Role:
{request.target_role}

Experience:
{request.experience}

Current Skills:
{", ".join(request.current_skills)}

Missing Skills:
{", ".join(request.missing_skills)}

Training Day:
Day {request.day_number}

Today's Topic:
{request.topic}

Use these sections:

1. Today's Learning Goal
2. Why This Topic Matters
3. What to Learn Today
4. Simple Explanation
5. Practical Example
6. Hands-On Task
7. Practice Questions
8. One Interview Question
9. Today's Checklist
10. What to Study Next
"""

    answer = ask_gemini(prompt)

    return {
        "success": True,
        "day": request.day_number,
        "topic": request.topic,
        "daily_training": answer
    }


# ============================================================
# PRACTICE QUESTION GENERATION
# ============================================================

@app.post("/api/practice/generate")
def generate_practice(request: PracticeGenerateRequest):

    prompt = f"""
You are an expert technical trainer.

Create practice questions for:

Target Job Role:
{request.target_role}

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Number of Questions:
{request.number_of_questions}

Generate exactly {request.number_of_questions} questions.

Include:
- Conceptual questions
- Practical questions
- Problem-solving questions

Do NOT provide answers.

Number the questions clearly.
"""

    answer = ask_gemini(prompt)

    return {
        "success": True,
        "target_role": request.target_role,
        "topic": request.topic,
        "difficulty": request.difficulty,
        "practice_questions": answer
    }


# ============================================================
# PRACTICE EVALUATION
# ============================================================

@app.post("/api/practice/evaluate")
def evaluate_practice(request: PracticeEvaluateRequest):

    prompt = f"""
You are an expert technical interviewer and trainer.

Evaluate the candidate's answer.

Target Job Role:
{request.target_role}

Topic:
{request.topic}

Difficulty:
{request.difficulty}

Question:
{request.question}

Candidate's Answer:
{request.user_answer}

Use exactly these sections:

1. Score out of 10
2. What Was Correct
3. What Was Missing
4. What Needs Improvement
5. Correct Understanding
6. Interview Tip
7. Recommended Next Step

Keep the feedback simple and educational.

Do not insult or discourage the candidate.
"""

    answer = ask_gemini(prompt)

    score_match = re.search(
        r"Score out of 10.*?(\d+(?:\.\d+)?)\s*/\s*10",
        answer,
        re.IGNORECASE | re.DOTALL
    )

    if score_match:
        score = float(score_match.group(1))
    else:
        score = 0.0

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO practice_results
        (target_role, topic, difficulty, score, user_answer)
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.target_role,
        request.topic,
        request.difficulty,
        score,
        request.user_answer
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "topic": request.topic,
        "score": score,
        "evaluation": answer,
        "message": "Practice result saved successfully"
    }


# ============================================================
# PROGRESS
# ============================================================

@app.get("/api/progress")
def get_progress():

    connection = get_db_connection()

    summary = connection.execute("""
        SELECT
            COUNT(*),
            COALESCE(AVG(score), 0),
            COALESCE(MAX(score), 0)
        FROM practice_results
    """).fetchone()

    results = connection.execute("""
        SELECT
            topic,
            difficulty,
            score
        FROM practice_results
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    connection.close()

    history = []

    for result in results:
        history.append({
            "topic": result["topic"],
            "difficulty": result["difficulty"],
            "score": result["score"]
        })

    return {
        "success": True,
        "total_attempts": summary[0],
        "average_score": round(summary[1], 2),
        "best_score": summary[2],
        "history": history
    }


# ============================================================
# AI PROGRESS ANALYSIS
# ============================================================

@app.get("/api/progress/analyze")
def analyze_progress():

    connection = get_db_connection()

    results = connection.execute("""
        SELECT topic, difficulty, score
        FROM practice_results
        ORDER BY id ASC
    """).fetchall()

    connection.close()

    if not results:
        return {
            "success": False,
            "message": "No practice results available yet."
        }

    progress_text = ""

    for result in results:
        progress_text += (
            f"Topic: {result['topic']}, "
            f"Difficulty: {result['difficulty']}, "
            f"Score: {result['score']}/10\n"
        )

    prompt = f"""
You are an expert AI career coach.

Analyze this candidate's practice performance.

Practice History:
{progress_text}

Identify the candidate's learning progress.

Use exactly these sections:

1. Overall Performance
2. Strong Topics
3. Weak Topics
4. Topics That Need More Practice
5. Recommended Next Topic
6. Recommended Difficulty
7. Learning Advice
8. Job Readiness Observation

Important rules:

- Consider higher scores as stronger performance.
- Consider scores below 6 as areas needing improvement.
- Do not claim the candidate is job-ready based only on this small dataset.
- Clearly mention that the analysis is based only on the available practice history.
- Give practical recommendations.
"""

    analysis = ask_gemini(prompt)

    return {
        "success": True,
        "practice_attempts": len(results),
        "analysis": analysis
    }


# ============================================================
# ADZUNA JOB SEARCH
# ============================================================

@app.get("/api/jobs/search")
def jobs_search(
    keyword: str = Query(..., description="Job title or skill"),
    location: str = Query("India", description="Job location")
):

    jobs = search_jobs(keyword, location)

    return {
        "success": True,
        "keyword": keyword,
        "location": location,
        "count": len(jobs),
        "jobs": jobs
    }


# ============================================================
# SAVE USER PROFILE - SQLALCHEMY
# ============================================================

@app.post("/api/profile")
def create_profile(profile: UserProfile):

    db = SessionLocal()

    try:

        new_profile = UserProfileModel(
            name=profile.name,
            skills=json.dumps(profile.skills),
            experience=profile.experience,
            location=profile.location,
            preferred_role=profile.preferred_role,
            expected_salary=profile.expected_salary
        )

        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        return {
            "success": True,
            "message": "User profile saved successfully",
            "profile": profile.model_dump(),
            "id": new_profile.id
        }

    finally:
        db.close()


# ============================================================
# GET SAVED USER PROFILE - SQLALCHEMY
# ============================================================

@app.get("/api/profile")
def get_profile():

    db = SessionLocal()

    try:

        profile = (
            db.query(UserProfileModel)
            .order_by(UserProfileModel.id.desc())
            .first()
        )

        if profile is None:
            return {
                "success": False,
                "message": "No user profile found"
            }

        return {
            "success": True,
            "profile": {
                "id": profile.id,
                "name": profile.name,
                "skills": json.loads(profile.skills),
                "experience": profile.experience,
                "location": profile.location,
                "preferred_role": profile.preferred_role,
                "expected_salary": profile.expected_salary
            }
        }

    finally:
        db.close()


# ============================================================
# AUTOMATIC JOB MATCHING
# ============================================================

class JobMatchRequest(BaseModel):
    skills: list[str]
    experience: str
    location: str
    preferred_role: str
    expected_salary: str


@app.post("/api/jobs/match")
def match_jobs(request: JobMatchRequest):

    # Search jobs using the user's preferred role and location
    jobs = search_jobs(
        request.preferred_role,
        request.location
    )

    matched_jobs = []

    for job in jobs:

        title = job.get("title", "")
        company = job.get("company", "")
        job_location = job.get("location", "")
        description = job.get("description", "")
        url = job.get("url", "")

        prompt = f"""
You are an expert AI Job Matching System.

Compare the candidate with the job.

CANDIDATE PROFILE
-----------------
Preferred Role: {request.preferred_role}
Experience: {request.experience}
Location: {request.location}
Skills: {", ".join(request.skills)}
Expected Salary: {request.expected_salary}

JOB
---
Title: {title}
Company: {company}
Location: {job_location}
Description:
{description}

Analyze the job and return ONLY valid JSON in this exact format:

{{
  "match_score": 0,
  "matching_skills": [],
  "missing_skills": [],
  "recommendation": ""
}}

Rules:

- match_score must be between 0 and 100.
- matching_skills must contain skills from the candidate that are relevant to the job.
- missing_skills must contain important skills mentioned or clearly required by the job but absent from the candidate profile.
- recommendation should be short and practical.
- Do not add markdown.
- Return JSON only.
"""

        try:
            ai_response = ask_gemini(prompt)

            # Remove possible markdown code fences
            clean_response = ai_response.strip()

            if clean_response.startswith("```"):
                clean_response = re.sub(
                    r"```(?:json)?",
                    "",
                    clean_response,
                    flags=re.IGNORECASE
                ).strip()

            if clean_response.endswith("```"):
                clean_response = clean_response[:-3].strip()

            analysis = json.loads(clean_response)

        except Exception as error:

            analysis = {
                "match_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendation": "Unable to analyze this job."
            }

        matched_jobs.append({
            "title": title,
            "company": company,
            "location": job_location,
            "url": url,
            "match_score": analysis.get("match_score", 0),
            "matching_skills": analysis.get("matching_skills", []),
            "missing_skills": analysis.get("missing_skills", []),
            "recommendation": analysis.get("recommendation", "")
        })

    # Highest matching jobs first
    matched_jobs.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return {
        "success": True,
        "candidate": {
            "preferred_role": request.preferred_role,
            "location": request.location,
            "experience": request.experience
        },
        "jobs_found": len(matched_jobs),
        "matched_jobs": matched_jobs
    }



# ============================================================
# AUTOMATIC JOB MATCHING FROM SAVED PROFILE
# LOCAL MATCHER + TOP 3 GEMINI ANALYSIS
# ============================================================

@app.post("/api/jobs/match-profile")
def match_jobs_from_saved_profile():

    # --------------------------------------------------------
    # 1. Get latest saved profile using SQLAlchemy
    # --------------------------------------------------------

    db = SessionLocal()

    try:
        profile = (
            db.query(UserProfileModel)
            .order_by(UserProfileModel.id.desc())
            .first()
        )
    finally:
        db.close()

    # --------------------------------------------------------
    # 2. Check whether profile exists
    # --------------------------------------------------------

    if profile is None:
        return {
            "success": False,
            "message": "No saved user profile found. Please create a profile first."
        }

    # --------------------------------------------------------
    # 3. Convert saved skills into Python list
    # --------------------------------------------------------

    try:
        skills = json.loads(profile.skills)
    except Exception:
        skills = []

    # --------------------------------------------------------
    # 4. Search jobs
    # --------------------------------------------------------

    jobs = search_jobs(
        profile.preferred_role,
        profile.location
    )

    if not jobs:
        return {
            "success": True,
            "profile_used": {
                "name": profile.name,
                "preferred_role": profile.preferred_role,
                "location": profile.location,
                "experience": profile.experience,
                "skills": skills
            },
            "jobs_found": 0,
            "matched_jobs": [],
            "gemini_used": False,
            "message": "No jobs found for the selected role and location."
        }

    # --------------------------------------------------------
    # 5. LOCAL MATCHING
    # --------------------------------------------------------

    ranked_jobs = rank_jobs(
        skills,
        jobs
    )

    # --------------------------------------------------------
    # 6. Select TOP 3 jobs for Gemini
    # --------------------------------------------------------

    top_jobs = ranked_jobs[:3]

    # --------------------------------------------------------
    # 7. Analyze TOP 3 using Gemini
    # --------------------------------------------------------

    gemini_used = False

    for job in top_jobs:

        title = job.get("title", "")
        company = job.get("company", "")
        job_location = job.get("location", "")
        description = job.get("description", "")

        prompt = f"""
You are an expert AI Job Matching System.

Compare the candidate profile with the job.

CANDIDATE PROFILE
-----------------
Name: {profile.name}
Preferred Role: {profile.preferred_role}
Experience: {profile.experience} years
Location: {profile.location}
Skills: {", ".join(skills)}
Expected Salary: {profile.expected_salary}

JOB
---
Title: {title}
Company: {company}
Location: {job_location}

Description:
{description}

Return ONLY valid JSON:

{{
  "match_score": 0,
  "matching_skills": [],
  "missing_skills": [],
  "recommendation": ""
}}

Rules:

- match_score must be between 0 and 100.
- Consider skills, experience, role and job requirements.
- matching_skills should contain skills the candidate has.
- missing_skills should contain important skills required by the job.
- recommendation should be short and practical.
- Return JSON only.
"""

        try:

            ai_response = ask_gemini(prompt)

            clean_response = ai_response.strip()

            if clean_response.startswith("```"):
                clean_response = re.sub(
                    r"```(?:json)?",
                    "",
                    clean_response,
                    flags=re.IGNORECASE
                ).strip()

            if clean_response.endswith("```"):
                clean_response = clean_response[:-3].strip()

            analysis = json.loads(clean_response)

            job["match_score"] = analysis.get(
                "match_score",
                job.get("match_score", 0)
            )

            job["matching_skills"] = analysis.get(
                "matching_skills",
                job.get("matching_skills", [])
            )

            job["missing_skills"] = analysis.get(
                "missing_skills",
                job.get("missing_skills", [])
            )

            job["recommendation"] = analysis.get(
                "recommendation",
                "Good match based on your profile."
            )

            gemini_used = True

        except Exception as e:

            print(
                f"Gemini analysis failed for {title}: {e}"
            )

            # IMPORTANT:
            # Keep local matching result if Gemini fails.

            job["recommendation"] = (
                "Match calculated using your skills and job requirements."
            )

    # --------------------------------------------------------
    # 8. Keep remaining jobs with local matching
    # --------------------------------------------------------

    for job in ranked_jobs[3:]:

        if not job.get("recommendation"):
            job["recommendation"] = (
                "Match calculated using your skills and job requirements."
            )

    # --------------------------------------------------------
    # 9. Re-sort after Gemini analysis
    # --------------------------------------------------------

    ranked_jobs.sort(
        key=lambda job: job.get("match_score", 0),
        reverse=True
    )

    # --------------------------------------------------------
    # 10. Return results
    # --------------------------------------------------------

    return {
        "success": True,
        "profile_used": {
            "name": profile.name,
            "preferred_role": profile.preferred_role,
            "location": profile.location,
            "experience": profile.experience,
            "skills": skills
        },
        "jobs_found": len(ranked_jobs),
        "matched_jobs": ranked_jobs,
        "gemini_used": gemini_used
    }


# ============================================================
# AI TRAINING
# ============================================================

@app.post("/api/training/generate")
def generate_training(request: TrainingRequest):

    prompt = f"""
You are an expert technical trainer.

Create a practical learning lesson for the following skill.

Skill:
{request.skill}

Level:
{request.level}

Create the lesson using exactly these sections:

1. Topic
2. What You Will Learn
3. Concept Explanation
4. Why This Skill Is Important
5. Practical Example
6. Code Example
7. Practice Task
8. Interview Questions
9. Next Step

Rules:

- Keep the explanation simple and beginner-friendly.
- Focus on practical job-related knowledge.
- Use Python examples when the skill is related to Python.
- Code should be short and easy to understand.
- Do not assume knowledge that the learner has not provided.
- Return ONLY valid JSON.

Return exactly this structure:

{{
  "topic": "",
  "what_you_will_learn": [],
  "concept_explanation": "",
  "why_important": "",
  "practical_example": "",
  "code_example": "",
  "practice_task": "",
  "interview_questions": [],
  "next_step": ""
}}
"""

    try:

        ai_response = ask_gemini(prompt)

        clean_response = ai_response.strip()

        # Remove markdown code fences
        if clean_response.startswith("```"):
            clean_response = re.sub(
                r"```(?:json)?",
                "",
                clean_response,
                flags=re.IGNORECASE
            ).strip()

        if clean_response.endswith("```"):
            clean_response = clean_response[:-3].strip()

        training = json.loads(clean_response)

        return {
            "success": True,
            "skill": request.skill,
            "level": request.level,
            "training": training
        }

    except Exception as e:

        return {
            "success": False,
            "skill": request.skill,
            "level": request.level,
            "message": "Unable to generate training lesson.",
            "error": str(e)
        }