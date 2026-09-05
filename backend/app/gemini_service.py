import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


def match_job_with_user(user_skills, job):
    prompt = f"""
You are an AI Job Matching Assistant.

Compare the user's skills with the job requirements.

USER SKILLS:
{user_skills}

JOB TITLE:
{job.get("title", "")}

COMPANY:
{job.get("company", "")}

LOCATION:
{job.get("location", "")}

JOB DESCRIPTION:
{job.get("description", "")}

Return ONLY the following format.
Do not add any extra text before or after it.

Match Score: 0-100%

Matching Skills:
- skill

Missing Skills:
- skill

Recommendation:
short recommendation

Training Suggestions:
- topic
- topic
"""

    try:
        result = ask_gemini(prompt)

        if not result:
            return {
                "match_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendation": "Gemini returned an empty response.",
                "training_suggestions": []
            }

        return parse_gemini_response(result)

    except Exception as e:
        print(f"Gemini analysis error: {e}")

        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "Unable to analyze this job.",
            "training_suggestions": []
        }


def parse_gemini_response(text):
    """
    Convert Gemini's text response into structured data.
    """

    lines = text.splitlines()

    match_score = 0
    matching_skills = []
    missing_skills = []
    recommendation = ""
    training_suggestions = []

    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Match Score
        if line.lower().startswith("match score"):
            try:
                score_text = line.split(":", 1)[1]
                score_text = (
                    score_text
                    .replace("%", "")
                    .strip()
                )

                match_score = int(float(score_text))

            except (ValueError, IndexError):
                match_score = 0

        # Sections
        elif line.lower().startswith("matching skills"):
            current_section = "matching"

        elif line.lower().startswith("missing skills"):
            current_section = "missing"

        elif line.lower().startswith("recommendation"):
            current_section = "recommendation"

            if ":" in line:
                recommendation = line.split(":", 1)[1].strip()

        elif line.lower().startswith("training suggestions"):
            current_section = "training"

        # Bullet points
        elif line.startswith("-"):
            value = line[1:].strip()

            if current_section == "matching":
                matching_skills.append(value)

            elif current_section == "missing":
                missing_skills.append(value)

            elif current_section == "training":
                training_suggestions.append(value)

        # Recommendation continuation
        elif current_section == "recommendation":
            if recommendation:
                recommendation += " " + line
            else:
                recommendation = line

    return {
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "training_suggestions": training_suggestions
    }


if __name__ == "__main__":
    answer = ask_gemini(
        "Hello Gemini! Tell me in one sentence what you can do."
    )

    print("\nGemini Response:")
    print(answer)