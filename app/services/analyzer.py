"""
CareerLens AI - Advanced Resume & ATS Analyzer

This module provides a deterministic ATS-style analysis of:
    Resume PDF text
    +
    Job Description PDF text

IMPORTANT:
This is a CareerLens heuristic score.
It is NOT an official score from any ATS vendor.
"""

import re
from typing import Dict, List, Set


# ============================================================
# 1. SKILL DATABASE
# ============================================================

SKILL_ALIASES: Dict[str, List[str]] = {

    # Programming
    "Python": [
        "python",
        "python3",
    ],

    "Java": [
        "java",
    ],

    "C": [
        "c programming",
        "c language",
    ],

    "C++": [
        "c++",
        "cpp",
    ],

    "JavaScript": [
        "javascript",
        "js",
    ],

    "TypeScript": [
        "typescript",
        "ts",
    ],

    # Frontend
    "HTML": [
        "html",
        "html5",
    ],

    "CSS": [
        "css",
        "css3",
    ],

    "React": [
        "react",
        "reactjs",
        "react.js",
    ],

    "Angular": [
        "angular",
        "angularjs",
    ],

    # Backend
    "Node.js": [
        "node.js",
        "nodejs",
        "node js",
    ],

    "Express.js": [
        "express.js",
        "expressjs",
        "express js",
    ],

    "FastAPI": [
        "fastapi",
        "fast api",
    ],

    "Django": [
        "django",
    ],

    "Flask": [
        "flask",
    ],

    # Databases
    "SQL": [
        "sql",
    ],

    "MySQL": [
        "mysql",
    ],

    "PostgreSQL": [
        "postgresql",
        "postgres",
    ],

    "MongoDB": [
        "mongodb",
        "mongo db",
    ],

    "SQLite": [
        "sqlite",
    ],

    "Redis": [
        "redis",
    ],

    # AI / ML
    "Machine Learning": [
        "machine learning",
        "ml",
    ],

    "Deep Learning": [
        "deep learning",
        "dl",
    ],

    "NLP": [
        "natural language processing",
        "nlp",
    ],

    "Computer Vision": [
        "computer vision",
    ],

    "Generative AI": [
        "generative ai",
        "gen ai",
        "genai",
    ],

    "LLM": [
        "large language model",
        "large language models",
        "llm",
        "llms",
    ],

    "RAG": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag",
    ],

    "Prompt Engineering": [
        "prompt engineering",
        "prompt design",
    ],

    # AI libraries
    "Pandas": [
        "pandas",
    ],

    "NumPy": [
        "numpy",
    ],

    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn",
    ],

    "TensorFlow": [
        "tensorflow",
    ],

    "PyTorch": [
        "pytorch",
    ],

    "OpenCV": [
        "opencv",
        "open cv",
    ],

    "Hugging Face": [
        "hugging face",
        "huggingface",
    ],

    "LangChain": [
        "langchain",
    ],

    "LlamaIndex": [
        "llamaindex",
        "llama index",
    ],

    # APIs
    "REST API": [
        "rest api",
        "restful api",
        "rest apis",
        "restful apis",
    ],

    "GraphQL": [
        "graphql",
    ],

    # DevOps / Cloud
    "Git": [
        "git",
    ],

    "GitHub": [
        "github",
        "git hub",
    ],

    "GitLab": [
        "gitlab",
    ],

    "Docker": [
        "docker",
    ],

    "Kubernetes": [
        "kubernetes",
        "k8s",
    ],

    "AWS": [
        "aws",
        "amazon web services",
    ],

    "Azure": [
        "azure",
        "microsoft azure",
    ],

    "GCP": [
        "gcp",
        "google cloud",
        "google cloud platform",
    ],

    "Linux": [
        "linux",
    ],

    # Core CS
    "DSA": [
        "data structures and algorithms",
        "data structures",
        "algorithms",
        "dsa",
    ],

    "OOP": [
        "object oriented programming",
        "object-oriented programming",
        "oop",
    ],

    "Computer Networks": [
        "computer networks",
        "networking",
    ],

    "Operating Systems": [
        "operating systems",
        "operating system",
        "os concepts",
    ],

    # UI / Tools
    "Streamlit": [
        "streamlit",
    ],

    "Jupyter": [
        "jupyter",
        "jupyter notebook",
    ],
}


# ============================================================
# 2. STOP WORDS
# ============================================================

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "these",
    "those",
    "are",
    "you",
    "your",
    "our",
    "will",
    "have",
    "has",
    "had",
    "job",
    "role",
    "work",
    "working",
    "candidate",
    "candidates",
    "required",
    "requirements",
    "requirement",
    "using",
    "use",
    "ability",
    "strong",
    "good",
    "knowledge",
    "experience",
    "skills",
    "skill",
    "responsibilities",
    "description",
    "company",
    "team",
    "teams",
    "years",
    "year",
    "plus",
    "including",
    "preferred",
    "should",
    "must",
    "can",
    "into",
    "about",
    "their",
    "they",
    "them",
    "who",
    "what",
    "where",
    "when",
    "how",
    "our",
    "an",
    "a",
    "to",
    "of",
    "in",
    "on",
    "at",
    "as",
    "or",
    "be",
    "is",
    "it",
    "by",
    "we",
    "i",
    "me",
    "my",
    "also",
    "etc",
}


# ============================================================
# 3. BASIC TEXT HELPERS
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize text for analysis."""

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """Case-insensitive phrase matching."""

    if not text or not phrase:
        return False

    text_lower = text.lower()
    phrase_lower = phrase.lower()

    return phrase_lower in text_lower


def extract_words(text: str) -> Set[str]:
    """Extract useful words from text."""

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}",
        text.lower(),
    )

    result = set()

    for word in words:

        word = word.strip(".,:;()[]{}")

        if word in STOPWORDS:
            continue

        if len(word) < 3:
            continue

        result.add(word)

    return result


# ============================================================
# 4. SKILL EXTRACTION
# ============================================================

def extract_skills(text: str) -> List[str]:
    """
    Extract known technical skills.
    """

    text = normalize_text(text)

    if not text:
        return []

    found = []

    for skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            if contains_phrase(text, alias):
                found.append(skill.lower())
                break

    return sorted(set(found))


# ============================================================
# 5. SKILL COMPARISON
# ============================================================

def compare_skills(
    resume_skills: List[str],
    jd_skills: List[str],
):
    """
    Compare resume skills against JD skills.
    """

    resume_map = {
        str(skill).lower(): str(skill).lower()
        for skill in resume_skills
    }

    jd_map = {
        str(skill).lower(): str(skill).lower()
        for skill in jd_skills
    }

    matched = []
    missing = []

    for key in jd_map:
        if key in resume_map:
            matched.append(jd_map[key])
        else:
            missing.append(jd_map[key])

    return (
        sorted(matched),
        sorted(missing),
    )


# ============================================================
# 6. KEYWORD ANALYSIS
# ============================================================

def extract_keywords(text: str) -> Set[str]:
    """
    Extract general keywords from JD/resume.
    """

    return extract_words(text)


def calculate_keyword_match(
    resume_text: str,
    jd_text: str,
) -> float:

    resume_words = extract_keywords(
        resume_text
    )

    jd_words = extract_keywords(
        jd_text
    )

    if not jd_words:
        return 0.0

    common = resume_words.intersection(
        jd_words
    )

    return (
        len(common) /
        len(jd_words)
    ) * 100


def find_missing_keywords(
    resume_text: str,
    jd_text: str,
) -> List[str]:

    resume_words = extract_keywords(
        resume_text
    )

    jd_words = extract_keywords(
        jd_text
    )

    missing = jd_words - resume_words

    return sorted(
        missing,
        key=len,
        reverse=True,
    )[:20]


# ============================================================
# 7. SECTION ANALYSIS
# ============================================================

SECTION_PATTERNS = {
    "contact": [
        "contact",
        "email",
        "phone",
    ],

    "summary": [
        "summary",
        "profile",
        "objective",
    ],

    "education": [
        "education",
        "academic",
        "qualification",
    ],

    "skills": [
        "skills",
        "technical skills",
        "technologies",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
    ],

    "certifications": [
        "certifications",
        "certificates",
    ],

    "achievements": [
        "achievements",
        "accomplishments",
    ],
}


def detect_sections(
    resume_text: str,
) -> Dict[str, bool]:

    text = resume_text.lower()

    sections = {}

    for section, patterns in SECTION_PATTERNS.items():

        sections[section] = any(
            pattern in text
            for pattern in patterns
        )

    return sections


def calculate_section_score(
    resume_text: str,
) -> float:

    sections = detect_sections(
        resume_text
    )

    important_sections = [
        "contact",
        "education",
        "skills",
        "projects",
    ]

    optional_sections = [
        "summary",
        "experience",
        "certifications",
    ]

    important_count = sum(
        sections[x]
        for x in important_sections
    )

    optional_count = sum(
        sections[x]
        for x in optional_sections
    )

    important_score = (
        important_count /
        len(important_sections)
    ) * 70

    optional_score = (
        optional_count /
        len(optional_sections)
    ) * 30

    return important_score + optional_score


# ============================================================
# 8. CONTACT ANALYSIS
# ============================================================

def analyze_contact_information(
    resume_text: str,
) -> Dict:

    email_found = bool(
        re.search(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            resume_text,
        )
    )

    phone_found = bool(
        re.search(
            r"(?:\+91[\s-]?)?[6-9]\d{9}",
            resume_text,
        )
    )

    linkedin_found = (
        "linkedin.com"
        in resume_text.lower()
    )

    github_found = (
        "github.com"
        in resume_text.lower()
    )

    return {
        "email": email_found,
        "phone": phone_found,
        "linkedin": linkedin_found,
        "github": github_found,
    }


def calculate_contact_score(
    resume_text: str,
) -> float:

    contact = analyze_contact_information(
        resume_text
    )

    score = 0

    if contact["email"]:
        score += 30

    if contact["phone"]:
        score += 30

    if contact["linkedin"]:
        score += 20

    if contact["github"]:
        score += 20

    return score


# ============================================================
# 9. EDUCATION ANALYSIS
# ============================================================

def analyze_education(
    resume_text: str,
    jd_text: str,
) -> Dict:

    resume = resume_text.lower()
    jd = jd_text.lower()

    resume_has_degree = any(
        x in resume
        for x in [
            "b.tech",
            "btech",
            "b.e",
            "bachelor",
            "computer science",
            "engineering",
        ]
    )

    jd_requires_degree = any(
        x in jd
        for x in [
            "b.tech",
            "btech",
            "b.e",
            "bachelor",
            "degree",
            "computer science",
            "engineering",
        ]
    )

    if not jd_requires_degree:
        score = 100

    elif resume_has_degree:
        score = 100

    else:
        score = 0

    return {
        "score": score,
        "resume_has_degree": resume_has_degree,
        "jd_requires_degree": jd_requires_degree,
    }


# ============================================================
# 10. EXPERIENCE ANALYSIS
# ============================================================

def extract_years_required(
    jd_text: str,
) -> float:

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"minimum\s*(?:of\s*)?(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            jd_text.lower(),
        )

        if match:

            try:
                return float(
                    match.group(1)
                )

            except ValueError:
                pass

    return 0.0


def extract_years_resume(
    resume_text: str,
) -> float:

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            resume_text.lower(),
        )

        for value in matches:

            try:
                values.append(
                    float(value)
                )

            except ValueError:
                pass

    return max(values) if values else 0.0


def calculate_experience_score(
    resume_text: str,
    jd_text: str,
) -> float:

    required = extract_years_required(
        jd_text
    )

    resume_years = extract_years_resume(
        resume_text
    )

    # If no experience requirement is explicitly
    # found, don't penalize the candidate.
    if required == 0:
        return 100.0

    if resume_years >= required:
        return 100.0

    if resume_years == 0:
        return 25.0

    return min(
        100.0,
        (resume_years / required) * 100,
    )


# ============================================================
# 11. PROJECT EVIDENCE
# ============================================================

def analyze_project_evidence(
    resume_text: str,
    jd_skills: List[str],
) -> Dict:

    text = resume_text.lower()

    project_section = any(
        x in text
        for x in [
            "projects",
            "project",
            "academic project",
            "personal project",
        ]
    )

    matched_project_skills = []

    for skill in jd_skills:

        if skill.lower() in text:
            matched_project_skills.append(
                skill
            )

    quantified = bool(
        re.search(
            r"\b\d+(?:%|\+|x| users?|projects?|records?|"
            r"requests?|datasets?|accuracy)\b",
            text,
            re.IGNORECASE,
        )
    )

    score = 0

    if project_section:
        score += 50

    if matched_project_skills:
        score += 30

    if quantified:
        score += 20

    return {
        "score": score,
        "project_section": project_section,
        "matched_project_skills": matched_project_skills,
        "quantified_evidence": quantified,
    }


# ============================================================
# 12. ACHIEVEMENT / QUANTIFICATION ANALYSIS
# ============================================================

def calculate_achievement_score(
    resume_text: str,
) -> float:

    action_words = [
        "built",
        "developed",
        "created",
        "implemented",
        "designed",
        "optimized",
        "improved",
        "deployed",
        "automated",
        "trained",
        "developed",
        "integrated",
    ]

    action_count = sum(
        resume_text.lower().count(word)
        for word in action_words
    )

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        resume_text,
    )

    score = 0

    if action_count >= 3:
        score += 50

    elif action_count >= 1:
        score += 25

    if len(numbers) >= 3:
        score += 50

    elif len(numbers) >= 1:
        score += 25

    return min(
        score,
        100,
    )


# ============================================================
# 13. ATS FORMAT ANALYSIS
# ============================================================

def analyze_ats_format(
    resume_text: str,
) -> Dict:

    sections = detect_sections(
        resume_text
    )

    contact_score = calculate_contact_score(
        resume_text
    )

    section_score = calculate_section_score(
        resume_text
    )

    achievement_score = calculate_achievement_score(
        resume_text
    )

    score = (
        contact_score * 0.30
        + section_score * 0.40
        + achievement_score * 0.30
    )

    issues = []

    if not contact_score >= 60:
        issues.append(
            "Add complete contact information including email and phone."
        )

    if not sections["skills"]:
        issues.append(
            "Add a clearly labeled Skills section."
        )

    if not sections["education"]:
        issues.append(
            "Add a clearly labeled Education section."
        )

    if not sections["projects"]:
        issues.append(
            "Add a Projects section with relevant technical work."
        )

    if not sections["experience"]:
        issues.append(
            "Add Experience if you have internships or professional experience."
        )

    if achievement_score < 50:
        issues.append(
            "Use measurable project or achievement results where truthful."
        )

    return {
        "score": round(score),
        "sections": sections,
        "contact": analyze_contact_information(
            resume_text
        ),
        "issues": issues,
    }


# ============================================================
# 14. SKILL PRIORITY
# ============================================================

HIGH_PRIORITY_SKILLS = {
    "python",
    "java",
    "c++",
    "javascript",
    "sql",
    "machine learning",
    "deep learning",
    "fastapi",
    "django",
    "react",
    "docker",
    "aws",
    "azure",
    "gcp",
    "kubernetes",
    "llm",
    "rag",
    "generative ai",
}


def prioritize_missing_skills(
    missing_skills: List[str],
) -> Dict[str, List[str]]:

    high = []
    medium = []
    low = []

    for skill in missing_skills:
        normalized = str(skill).lower()

        if normalized in HIGH_PRIORITY_SKILLS:
            high.append(normalized)

        elif normalized in {
            "git",
            "github",
            "rest api",
            "linux",
            "pandas",
            "numpy",
            "scikit-learn",
            "pytorch",
            "tensorflow",
            "mongodb",
            "postgresql",
        }:
            medium.append(normalized)

        else:
            low.append(normalized)

    return {
        "high": high,
        "medium": medium,
        "low": low,
    }


# ============================================================
# 15. CERTIFICATION RECOMMENDATIONS
# ============================================================

CERTIFICATION_MAP = {
    "aws": "AWS Certified Cloud Practitioner",
    "azure": "Microsoft Azure Fundamentals (AZ-900)",
    "gcp": "Google Cloud Digital Leader",
    "kubernetes": "Kubernetes and Cloud Native Associate (KCNA)",
    "machine learning": "Machine Learning specialization or certification",
    "generative ai": "Generative AI specialization",
    "python": "Python programming certification/course",
    "docker": "Docker/containerization certification or practical course",
    "sql": "SQL/database certification or practical SQL course",
}


def recommend_certifications(
    missing_skills: List[str],
) -> List[str]:

    recommendations = []

    for skill in missing_skills:
        normalized = str(skill).lower()

        if normalized in CERTIFICATION_MAP:
            recommendations.append(CERTIFICATION_MAP[normalized])

    return recommendations[:5]


# ============================================================
# 16. GENERATE SUGGESTIONS
# ============================================================

def generate_suggestions(
    missing_skills: List[str],
    missing_keywords: List[str],
    ats_issues: List[str],
    project_analysis: Dict,
) -> List[str]:

    suggestions = []

    # Skill recommendations
    for skill in missing_skills[:5]:

        suggestions.append(
            f"Consider adding evidence for {skill} if you genuinely have that skill."
        )

    # Keyword recommendations
    if missing_keywords:

        keywords = ", ".join(
            missing_keywords[:5]
        )

        suggestions.append(
            f"Review relevant JD terminology such as: {keywords}."
        )

    # ATS structure
    suggestions.extend(
        ats_issues[:3]
    )

    # Projects
    if project_analysis["score"] < 60:

        suggestions.append(
            "Strengthen project descriptions with technologies, actions, and measurable outcomes."
        )

    return suggestions[:10]


# ============================================================
# 17. FINAL ATS SCORE
# ============================================================

def calculate_advanced_score(
    skill_score: float,
    keyword_score: float,
    education_score: float,
    experience_score: float,
    project_score: float,
    ats_format_score: float,
) -> int:
    """
    CareerLens weighted score.

    Skill Match       = 30%
    Keyword Match     = 20%
    Education Match   = 10%
    Experience Match  = 10%
    Project Evidence  = 10%
    ATS Format        = 20%
    """

    score = (
        skill_score * 0.30
        + keyword_score * 0.20
        + education_score * 0.10
        + experience_score * 0.10
        + project_score * 0.10
        + ats_format_score * 0.20
    )

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )


# ============================================================
# 18. MAIN ANALYZER
# ============================================================

def analyze_resume_and_jd(
    resume_text: str,
    jd_text: str,
) -> Dict:
    """
    Complete CareerLens AI analysis.

    Compatible with main.py:

        analysis["score"]
        analysis["matched_skills"]
        analysis["missing_skills"]
        analysis["suggestions"]
        analysis["certifications"]
    """

    resume_text = normalize_text(
        resume_text
    )

    jd_text = normalize_text(
        jd_text
    )

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not resume_text:

        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [
                "Resume text could not be extracted."
            ],
            "certifications": [],
        }

    if not jd_text:

        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [
                "Job description text could not be extracted."
            ],
            "certifications": [],
        }

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    resume_skills = extract_skills(
        resume_text
    )

    jd_skills = extract_skills(
        jd_text
    )

    matched_skills, missing_skills = compare_skills(
        resume_skills,
        jd_skills,
    )

    # --------------------------------------------------------
    # Skill score
    # --------------------------------------------------------

    if jd_skills:

        skill_score = (
            len(matched_skills)
            / len(jd_skills)
        ) * 100

    else:

        # If no known skills were extracted from JD,
        # don't falsely claim a strong skill match.
        skill_score = 0

    # --------------------------------------------------------
    # Keyword score
    # --------------------------------------------------------

    keyword_score = calculate_keyword_match(
        resume_text,
        jd_text,
    )

    missing_keywords = find_missing_keywords(
        resume_text,
        jd_text,
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education = analyze_education(
        resume_text,
        jd_text,
    )

    education_score = education["score"]

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_score = calculate_experience_score(
        resume_text,
        jd_text,
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    project_analysis = analyze_project_evidence(
        resume_text,
        jd_skills,
    )

    project_score = project_analysis["score"]

    # --------------------------------------------------------
    # ATS format
    # --------------------------------------------------------

    ats_format = analyze_ats_format(
        resume_text,
    )

    ats_format_score = ats_format["score"]

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    final_score = calculate_advanced_score(
        skill_score=skill_score,
        keyword_score=keyword_score,
        education_score=education_score,
        experience_score=experience_score,
        project_score=project_score,
        ats_format_score=ats_format_score,
    )

    # --------------------------------------------------------
    # Missing skill priorities
    # --------------------------------------------------------

    skill_priority = prioritize_missing_skills(
        missing_skills
    )

    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    suggestions = generate_suggestions(
        missing_skills=missing_skills,
        missing_keywords=missing_keywords,
        ats_issues=ats_format["issues"],
        project_analysis=project_analysis,
    )

    # --------------------------------------------------------
    # Certifications
    # --------------------------------------------------------

    certifications = recommend_certifications(
        missing_skills
    )

    # --------------------------------------------------------
    # Debug
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("             CAREERLENS AI ANALYSIS")
    print("=" * 60)

    print("\nResume skills:")
    print(resume_skills)

    print("\nJD skills:")
    print(jd_skills)

    print("\nMatched skills:")
    print(matched_skills)

    print("\nMissing skills:")
    print(missing_skills)

    print("\nSkill score:")
    print(round(skill_score))

    print("\nKeyword score:")
    print(round(keyword_score))

    print("\nEducation score:")
    print(round(education_score))

    print("\nExperience score:")
    print(round(experience_score))

    print("\nProject score:")
    print(round(project_score))

    print("\nATS format score:")
    print(round(ats_format_score))

    print("\nFINAL ATS SCORE:")
    print(final_score)

    print("=" * 60)
    print("\n")

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        # Existing main.py fields
        "score": final_score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "suggestions": suggestions,

        "certifications": certifications,

        # Advanced analysis
        "score_breakdown": {
            "skill_match": round(skill_score),
            "keyword_match": round(keyword_score),
            "education_match": round(education_score),
            "experience_match": round(experience_score),
            "project_evidence": round(project_score),
            "ats_format": round(ats_format_score),
        },

        "skill_priority": skill_priority,

        "missing_keywords": missing_keywords,

        "resume_skills": resume_skills,

        "jd_skills": jd_skills,

        "education_analysis": education,

        "experience": {
            "required_years": extract_years_required(
                jd_text
            ),
            "resume_years": extract_years_resume(
                resume_text
            ),
            "score": round(
                experience_score
            ),
        },

        "project_analysis": project_analysis,

        "ats_analysis": ats_format,

        "metadata": {
            "resume_characters": len(
                resume_text
            ),
            "jd_characters": len(
                jd_text
            ),
            "resume_word_count": len(
                resume_text.split()
            ),
            "jd_word_count": len(
                jd_text.split()
            ),
        },
    }
