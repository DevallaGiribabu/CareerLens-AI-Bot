def _section_score(resume_text):
    text = (resume_text or "").lower()
    sections = ["skills", "experience", "education", "projects", "summary", "objective"]
    found = sum(1 for section in sections if section in text)
    return round((found / len(sections)) * 100)


def _keyword_alignment_score(resume_text, jd_text):
    resume = (resume_text or "").lower()
    jd = (jd_text or "").lower()

    jd_words = [word for word in jd.replace("-", " ").split() if len(word) > 3]
    if not jd_words:
        return 100

    matched = sum(1 for word in jd_words if word in resume)
    return round((matched / len(jd_words)) * 100)


def calculate_score(resume_skills, jd_skills, resume_text="", jd_text=""):
    if not jd_skills:
        return 0

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = resume_set.intersection(jd_set)

    keyword_match = (len(matched) / len(jd_set)) * 100
    section_score = _section_score(resume_text)
    alignment_score = _keyword_alignment_score(resume_text, jd_text)

    ats_score = (
        keyword_match * 0.40 +
        section_score * 0.20 +
        alignment_score * 0.40
    )

    return max(0, min(100, round(ats_score)))
