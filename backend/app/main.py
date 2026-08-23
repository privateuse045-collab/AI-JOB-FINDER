from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import re

from gemini_service import ask_gemini


app = FastAPI(
    title="AI Job Finder",
    description="AI-powered job and career assistant",
    version="1.0.0"
)


DATABASE_NAME = "ai_job_finder.db"


def init_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


init_database()


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


class SkillGapRequest(BaseModel):
    skills: list[str]
    target_role: str
    experience: str


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


@app.get("/")
def home():
    return {
        "message": "AI Job Finder API is running"
    }


@app.post("/api/ai/test")
def ai_test(request: AIRequest):

    answer = ask_gemini(request.prompt)

    return {
        "success": True,
        "response": answer
    }


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

Provide a practical Skill Gap Analysis.

Use these sections:

1. Current Skills
2. Missing Skills
3. High Priority Skills
4. Medium Priority Skills
5. Skills That Are Already Strong
6. Recommended Learning Order
7. Practical Projects to Build
8. Interview Topics to Prepare
9. Estimated Training Path

Keep the answer simple, clear, and practical.

Do not assume that the candidate already knows skills that are not listed.
"""

    answer = ask_gemini(prompt)

    return {
        "success": True,
        "target_role": request.target_role,
        "skill_gap_analysis": answer
    }


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

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
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


@app.get("/api/progress")
def get_progress():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(AVG(score), 0),
            COALESCE(MAX(score), 0)
        FROM practice_results
    """)

    summary = cursor.fetchone()

    cursor.execute("""
        SELECT
            topic,
            difficulty,
            score
        FROM practice_results
        ORDER BY id DESC
        LIMIT 20
    """)

    results = cursor.fetchall()

    connection.close()

    history = []

    for result in results:
        history.append({
            "topic": result[0],
            "difficulty": result[1],
            "score": result[2]
        })

    return {
        "success": True,
        "total_attempts": summary[0],
        "average_score": round(summary[1], 2),
        "best_score": summary[2],
        "history": history
    }


@app.get("/api/progress/analyze")
def analyze_progress():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT topic, difficulty, score
        FROM practice_results
        ORDER BY id ASC
    """)

    results = cursor.fetchall()

    connection.close()

    if not results:
        return {
            "success": False,
            "message": "No practice results available yet."
        }

    progress_text = ""

    for topic, difficulty, score in results:
        progress_text += (
            f"Topic: {topic}, "
            f"Difficulty: {difficulty}, "
            f"Score: {score}/10\n"
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