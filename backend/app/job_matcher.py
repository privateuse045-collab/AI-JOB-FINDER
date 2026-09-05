def normalize_skill(skill):
    """
    Convert skill into a standard format
    for easier comparison.
    """
    return skill.strip().lower()


def calculate_job_match(user_skills, job):
    """
    Calculate a basic local skill-match score
    without using Gemini.
    """

    # Convert user skills into lowercase
    user_skill_set = {
        normalize_skill(skill)
        for skill in user_skills
        if skill
    }

    # Get job description
    job_text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()

    # Common technical skills
    known_skills = [
        "python",
        "fastapi",
        "django",
        "flask",
        "java",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "git",
        "github",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "rest api",
        "html",
        "css",
        "linux",
    ]

    # Find skills mentioned in the job
    job_skills = []

    for skill in known_skills:
        if skill in job_text:
            job_skills.append(skill)

    # Matching skills
    matching_skills = []

    for skill in user_skill_set:
        if skill in job_skills:
            matching_skills.append(skill)

    # Missing skills
    missing_skills = [
        skill
        for skill in job_skills
        if skill not in user_skill_set
    ]

    # Calculate score
    if job_skills:
        score = round(
            (len(matching_skills) / len(job_skills)) * 100
        )
    else:
        score = 0

    return {
        "match_score": score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
    }


def rank_jobs(user_skills, jobs):
    """
    Calculate local match scores for all jobs
    and return them in descending order.
    """

    ranked_jobs = []

    for job in jobs:

        match = calculate_job_match(
            user_skills,
            job
        )

        job_result = job.copy()

        job_result.update(match)

        ranked_jobs.append(job_result)

    # Highest score first
    ranked_jobs.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return ranked_jobs


if __name__ == "__main__":

    test_user_skills = [
        "Python",
        "FastAPI",
        "SQL",
        "Git",
        "REST API",
    ]

    test_jobs = [
        {
            "title": "Python FastAPI Developer",
            "company": "Test Company",
            "location": "Mumbai",
            "description": """
                Python FastAPI REST API SQL Git
                PostgreSQL Docker
            """,
        },
        {
            "title": "Java Developer",
            "company": "Another Company",
            "location": "Pune",
            "description": """
                Java Spring Boot MySQL
            """,
        },
    ]

    results = rank_jobs(
        test_user_skills,
        test_jobs
    )

    for job in results:
        print("\n-----------------------------")
        print("Title:", job["title"])
        print("Company:", job["company"])
        print("Match Score:", job["match_score"], "%")
        print(
            "Matching Skills:",
            job["matching_skills"]
        )
        print(
            "Missing Skills:",
            job["missing_skills"]
        )