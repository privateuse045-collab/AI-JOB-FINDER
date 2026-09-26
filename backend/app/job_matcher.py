import re


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


# -----------------------------------------------------------------
# GENERIC ROLE / DOMAIN KNOWLEDGE REGISTRY
# -----------------------------------------------------------------

# Maps canonical role names to:
# 1. direct_keywords: keywords indicating a direct target-role match
# 2. related_domain_keywords: technical disciplines, concepts, or sub-systems
# 3. genuine_technical_keywords: verified technical indicators that confirm
#    the acronym is used in its authentic engineering sense
# 4. negative_keywords: terms indicating the acronym/title is used in an
#    unrelated non-technical domain (e.g. entertainment, finance, marketing)
ROLE_DOMAIN_REGISTRY = {
    "bms": {
        "direct_keywords": [
            "bms",
            "building management system",
            "building management systems",
            "building management",
        ],
        "related_domain_keywords": [
            "building automation",
            "building automation system",
            "building automation systems",
            "controls engineering",
            "controls engineer",
            "control systems engineer",
            "control engineer",
            "hvac controls",
            "hvac control",
            "hvac",
            "ddc",
            "ddc controller",
            "plc",
            "scada",
            "bacnet",
            "modbus",
            "lon",
            "knx",
            "elv",
            "extra low voltage",
            "access control",
            "cctv",
            "fire alarm",
            "grms",
            "testing and commissioning",
            "commissioning engineer",
            "commissioning",
            "system integration",
            "instrumentation and control",
        ],
        "genuine_technical_keywords": [
            "building management system",
            "building automation",
            "ddc",
            "bacnet",
            "modbus",
            "hvac controls",
            "hvac control",
            "plc",
            "scada",
            "commissioning",
            "elv",
            "access control",
            "grms",
            "fire alarm",
            "instrumentation",
        ],
        "negative_keywords": [
            "brandlabs",
            "bms live",
            "bookmyshow",
            "entertainment",
            "bachelor of management studies",
            "bachelor of management",
            "mutual fund",
            "mutual funds",
            "rta operations",
            "rta",
            "aif",
            "pms operations",
            "banking operations",
            "wealth management",
            "equity",
            "portfolio management",
            "operations executive",
            "customer success",
            "marketing executive",
            "human resources",
        ],
    },
    "python": {
        "direct_keywords": [
            "python developer",
            "python engineer",
            "python programmer",
            "python",
        ],
        "related_domain_keywords": [
            "fastapi",
            "django",
            "flask",
            "backend developer",
            "backend engineer",
            "software engineer",
            "rest api",
            "sql",
            "postgresql",
            "docker",
        ],
        "genuine_technical_keywords": [
            "fastapi",
            "django",
            "flask",
            "rest api",
            "postgresql",
            "docker",
        ],
        "negative_keywords": [
            "snake",
            "monty python",
        ],
    },
}


def _contains_keyword(text, keyword):
    """
    Search for keyword in text with word boundary protection.
    Uses non-alphanumeric lookaround to cleanly handle hyphenated,
    underscored, or slashed titles like 'Engineer_BMS' or 'HAS/BMS'.
    """
    if not text or not keyword:
        return False
    pattern = r"(?<![a-zA-Z0-9])" + re.escape(keyword) + r"(?![a-zA-Z0-9])"
    return bool(re.search(pattern, text, re.IGNORECASE))


def _get_role_domain_config(preferred_role):
    """
    Return role-matching configuration for any preferred role.
    If the role is registered in ROLE_DOMAIN_REGISTRY, returns its rules.
    Otherwise, derives direct keywords from preferred_role and SKILL_ALIASES.
    """
    if not preferred_role:
        return {
            "direct_keywords": [],
            "related_domain_keywords": [],
            "genuine_technical_keywords": [],
            "negative_keywords": [],
        }

    role_norm = normalize_skill(preferred_role)
    role_canonical = canonical_skill(role_norm)

    if role_canonical in ROLE_DOMAIN_REGISTRY:
        return ROLE_DOMAIN_REGISTRY[role_canonical]

    # Generic fallback for unregistered roles
    direct = {role_norm, role_canonical}
    for alias, canonical in SKILL_ALIASES.items():
        if canonical == role_canonical:
            direct.add(alias)

    return {
        "direct_keywords": list(direct),
        "related_domain_keywords": [],
        "genuine_technical_keywords": list(direct),
        "negative_keywords": [],
    }


def _get_role_keywords(preferred_role):
    """
    Return a frozenset of domain-relevant search keywords
    derived from preferred_role, direct keywords, and related domain concepts.
    Preserved for backwards compatibility with existing callers.
    """
    if not preferred_role:
        return frozenset()

    config = _get_role_domain_config(preferred_role)
    keywords = set(config["direct_keywords"]) | set(config["related_domain_keywords"])
    return frozenset(keywords)


# -----------------------------------------------------------------
# CORE MATCHING
# -----------------------------------------------------------------

def calculate_job_match(user_skills, job, preferred_role=""):
    """
    Calculate a local job match score without using Gemini.

    SCORING ARCHITECTURE
    --------------------
    1. Candidate Skill Compatibility (up to 35 pts):
       Evaluates actual skills entered by the candidate against
       skills detected in the job text.
       IMPORTANT: preferred_role is NOT injected into candidate skills.
       matching_skills strictly reflects actual user skill overlap.

    2. Direct Target-Role Match (up to 40 pts):
       Awarded when the job TITLE directly matches the target role
       (e.g., 'BMS Commissioning Engineer' for a 'BMS' candidate).
       If direct target role appears in description only, awards 10 pts.

    3. Related Technical Domain Relevance (up to 25 pts):
       Recognizes related technical concepts (e.g., building automation,
       controls engineer, DDC, SCADA, HVAC controls for BMS).
       - In job TITLE: +15 pts
       - In job description: +10 pts

    4. False-Positive Protection:
       When acronyms like 'BMS' appear in non-technical contexts
       (e.g., 'BMS Live' entertainment, 'Bachelor of Management Studies',
       finance/RTA operations), false-positive detection suppresses
       role and domain points unless genuine technical engineering
       evidence is confirmed.

    BACKWARD COMPATIBILITY
    ----------------------
    When preferred_role is empty, uses 100% pure skill-based scoring
    identical to the original implementation.
    """

    # ---------------------------------------------------------
    # 1. Normalize user's actual skills (do NOT inject role)
    # ---------------------------------------------------------

    user_skill_set = {
        canonical_skill(skill)
        for skill in user_skills
        if skill
    }

    # ---------------------------------------------------------
    # 2. Searchable job text
    # ---------------------------------------------------------

    job_title = str(job.get("title", "")).lower()
    job_desc = str(job.get("description", "")).lower()
    job_text = f"{job_title} {job_desc}"

    # ---------------------------------------------------------
    # 3. Detect known skills in the job
    # ---------------------------------------------------------

    job_skills = []

    for skill in KNOWN_SKILLS:
        normalized_skill = normalize_skill(skill)

        if _contains_keyword(job_text, normalized_skill):
            canonical = canonical_skill(skill)

            if canonical not in job_skills:
                job_skills.append(canonical)

    # ---------------------------------------------------------
    # 4. Find matching & missing skills (strictly user's skills)
    # ---------------------------------------------------------

    matching_skills = [
        skill
        for skill in user_skill_set
        if skill in job_skills
    ]

    missing_skills = [
        skill
        for skill in job_skills
        if skill not in user_skill_set
    ]

    # ---------------------------------------------------------
    # 5. Base skill score (0 - 100%)
    # ---------------------------------------------------------

    if job_skills:
        skill_score = (len(matching_skills) / len(job_skills)) * 100.0
    else:
        skill_score = 0.0

    # ---------------------------------------------------------
    # 6. Fallback if no preferred_role is specified
    # ---------------------------------------------------------

    if not preferred_role:
        return {
            "match_score": round(skill_score),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
        }

    # ---------------------------------------------------------
    # 7. Role & Domain Relevance Evaluation
    # ---------------------------------------------------------

    role_config = _get_role_domain_config(preferred_role)
    direct_kws = role_config["direct_keywords"]
    related_kws = role_config["related_domain_keywords"]
    genuine_tech_kws = role_config["genuine_technical_keywords"]
    negative_kws = role_config["negative_keywords"]

    # False-positive verification:
    # Triggered if negative indicators are present AND verified
    # genuine technical keywords are absent.
    has_negative_indicators = any(
        _contains_keyword(job_text, neg) for neg in negative_kws
    )
    has_genuine_technical_context = any(
        _contains_keyword(job_text, gen) for gen in genuine_tech_kws
    )
    is_false_positive = has_negative_indicators and not has_genuine_technical_context

    # Direct role evaluation
    role_in_title = False
    role_in_desc = False
    if not is_false_positive:
        role_in_title = any(
            _contains_keyword(job_title, kw) for kw in direct_kws
        )
        role_in_desc = any(
            _contains_keyword(job_desc, kw) for kw in direct_kws
        )

    # Related domain evaluation
    domain_in_title = False
    domain_in_desc = False
    if not is_false_positive:
        domain_in_title = any(
            _contains_keyword(job_title, kw) for kw in related_kws
        )
        domain_in_desc = any(
            _contains_keyword(job_desc, kw) for kw in related_kws
        )

    # ---------------------------------------------------------
    # 8. Score Component Calculation
    # ---------------------------------------------------------

    # Component A: Candidate skill match (up to 35 pts)
    skill_comp = (skill_score / 100.0) * 35.0

    # Component B: Direct target role (up to 40 pts)
    if role_in_title:
        role_comp = 40.0
    elif role_in_desc:
        role_comp = 10.0
    else:
        role_comp = 0.0

    # Component C: Related technical domain (up to 25 pts)
    domain_comp = 0.0
    if domain_in_title:
        domain_comp += 15.0
    if domain_in_desc:
        domain_comp += 10.0
    domain_comp = min(25.0, domain_comp)

    # False-positive penalty: zero out role and domain points
    if is_false_positive:
        role_comp = 0.0
        domain_comp = 0.0
        skill_comp = 0.0

    combined_score = min(
        100,
        round(skill_comp + role_comp + domain_comp)
    )

    # ---------------------------------------------------------
    # 9. Return structured result
    # ---------------------------------------------------------

    return {
        "match_score": combined_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
    }


def rank_jobs(user_skills, jobs, preferred_role=""):
    """
    Calculate local match scores for all jobs
    and return them in descending order.

    preferred_role is forwarded to calculate_job_match() to allow
    role relevance, related domain concepts, and false-positive
    protection to guide scoring.
    """

    ranked_jobs = []

    for job in jobs:

        match = calculate_job_match(
            user_skills,
            job,
            preferred_role
        )

        job_result = job.copy()
        job_result.update(match)

        ranked_jobs.append(job_result)

    # Highest score first
    ranked_jobs.sort(
        key=lambda j: j["match_score"],
        reverse=True
    )

    return ranked_jobs


# =================================================================
# SELF-TEST (python app\job_matcher.py)
# =================================================================

if __name__ == "__main__":

    test_preferred_role = "BMS"

    # User profile skills (note: BMS is preferred role, not in skills)
    test_user_skills = [
        "Access control",
        "SQL",
    ]

    test_jobs = [
        {
            "title": "BMS Commissioning Engineer",
            "company": "BuildTech",
            "location": "Mumbai",
            "description": (
                "Job Details for BMS Commissioning Engineer Department: BA "
                "DDC, BACnet, HVAC Controls, PLC, SCADA, Commissioning."
            ),
        },
        {
            "title": "Presales Engineer_BMS / ELV / HVAC",
            "company": "SecureTech",
            "location": "Mumbai",
            "description": (
                "Presales Engineer for Navi Mumbai location. "
                "BMS, ELV, CCTV, Fire Alarm, HVAC."
            ),
        },
        {
            "title": "Senior Engineer - GRMS/HAS/BMS",
            "company": "Integrated Systems",
            "location": "Mumbai",
            "description": (
                "Lead the technical development of BMS, GRMS, HAS, "
                "Building Management System and SCADA systems."
            ),
        },
        {
            "title": "Senior Executive - Brandlabs (BMS Live)",
            "company": "BookMyShow",
            "location": "Mumbai",
            "description": (
                "BookMyShow entertainment platform. Manage brand partnerships "
                "and live event marketing for BMS Live."
            ),
        },
        {
            "title": "AIF RTA Operations executive",
            "company": "Finance Corp",
            "location": "Mumbai",
            "description": (
                "Executive, AIF RTA Operations. Mutual fund operations, "
                "Bachelor of Management Studies (BMS) preferred."
            ),
        },
        {
            "title": "Business Project Manager",
            "company": "Howell Protection Systems India Pvt. Ltd.",
            "location": "Mumbai",
            "description": (
                "Assistant Manager / Manager - Business Development. "
                "Howell Protection Systems. ELV, BMS integration."
            ),
        },
        {
            "title": "Senior Controls Engineer",
            "company": "ARUP",
            "location": "Mumbai",
            "description": (
                "Senior Controls Engineer. Inclusive employer. Design and "
                "engineering of control systems and building automation."
            ),
        },
    ]

    print("=" * 70)
    print(f"Preferred Role : {test_preferred_role}")
    print(f"User Skills    : {test_user_skills}")
    print("=" * 70)

    results = rank_jobs(
        test_user_skills,
        test_jobs,
        test_preferred_role
    )

    for i, job in enumerate(results, 1):
        print(f"\n[{i}] {job['title']}")
        print(f"    Company          : {job['company']}")
        print(f"    Match Score      : {job['match_score']} %")
        print(f"    Matching Skills  : {job['matching_skills']}")
        print(f"    Missing Skills   : {job['missing_skills']}")