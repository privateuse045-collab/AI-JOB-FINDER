def normalize_skill(skill):
    """
    Convert skill into a standard format
    for easier comparison.
    """
    return skill.strip().lower()


# Technical skills supported by the job matcher
KNOWN_SKILLS = [
    # Programming / Software
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

    # BMS / Building Automation
    "bms",
    "building management system",
    "building automation",
    "building automation system",
    "hvac",
    "hvac controls",
    "controls engineering",
    "automation system design",

    # PLC / Automation
    "plc",
    "plc programming",
    "scada",
    "ddc",
    "ddc controller",
    "testing and commissioning",
    "commissioning",

    # Communication Protocols
    "bacnet",
    "bacnet/ip",
    "modbus",
    "lon",
    "knx",

    # Security / ELV
    "access control",
    "cctv",
    "fire alarm",
    "elv",
    "security systems",
    "security system",
    "video surveillance",
    "intrusion detection",

    # Electrical / MEP
    "electrical maintenance",
    "electrical systems",
    "mechanical systems",
    "mep",
    "plumbing systems",
    "fire safety systems",

    # Service / Field Skills
    "field service",
    "field service troubleshooting",
    "troubleshooting",
    "client management",
    "technical support",
    "maintenance",
    "preventive maintenance",
    "amc",
    "spare sales",

    # Project / Engineering
    "project management",
    "system integration",
    "commissioning and handover",
    "team leadership",
]


# Skill aliases:
# Different job descriptions may use different names
# for the same skill.
SKILL_ALIASES = {
    "access control system": "access control",
    "access-control": "access control",
    "building management": "bms",
    "building management system": "bms",
    "building automation system": "building automation",
    "hvac control": "hvac controls",
    "hvac controls system": "hvac controls",
    "programmable logic controller": "plc",
    "plc programming": "plc",
    "supervisory control and data acquisition": "scada",
    "direct digital control": "ddc",
    "closed circuit television": "cctv",
    "electronic security": "security systems",
    "extra low voltage": "elv",
    "bacnet/ip": "bacnet",
}


def canonical_skill(skill):
    """
    Convert a skill to its standard/canonical form.
    """
    skill = normalize_skill(skill)

    return SKILL_ALIASES.get(
        skill,
        skill
    )


def calculate_job_match(user_skills, job):
    """
    Calculate a local skill-match score
    without using Gemini.
    """

    # ---------------------------------------------------------
    # 1. Normalize user's skills
    # ---------------------------------------------------------

    user_skill_set = {
        canonical_skill(skill)
        for skill in user_skills
        if skill
    }

    # ---------------------------------------------------------
    # 2. Create searchable job text
    # ---------------------------------------------------------

    job_text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()

    # ---------------------------------------------------------
    # 3. Detect known skills in the job
    # ---------------------------------------------------------

    job_skills = []

    for skill in KNOWN_SKILLS:

        normalized_skill = normalize_skill(skill)

        if normalized_skill in job_text:

            canonical = canonical_skill(skill)

            if canonical not in job_skills:
                job_skills.append(canonical)

    # ---------------------------------------------------------
    # 4. Find matching skills
    # ---------------------------------------------------------

    matching_skills = [
        skill
        for skill in user_skill_set
        if skill in job_skills
    ]

    # ---------------------------------------------------------
    # 5. Find missing skills
    # ---------------------------------------------------------

    missing_skills = [
        skill
        for skill in job_skills
        if skill not in user_skill_set
    ]

    # ---------------------------------------------------------
    # 6. Calculate score
    # ---------------------------------------------------------

    if job_skills:

        score = round(
            (len(matching_skills) / len(job_skills)) * 100
        )

    else:

        score = 0

    # ---------------------------------------------------------
    # 7. Return result
    # ---------------------------------------------------------

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
        "Access control",
        "SQL",
        "BMS",
    ]

    test_jobs = [
        {
            "title": "BMS Engineer",
            "company": "Test Company",
            "location": "Mumbai",
            "description": """
                BMS Building Management System
                Access Control
                HVAC Controls
                BACnet
                SCADA
            """,
        },
        {
            "title": "Python Developer",
            "company": "Another Company",
            "location": "Mumbai",
            "description": """
                Python FastAPI SQL Git Docker
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