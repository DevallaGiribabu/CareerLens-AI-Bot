def compare_skills(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(resume_set.intersection(jd_set))
    missing = sorted(jd_set - resume_set)

    return matched, missing
