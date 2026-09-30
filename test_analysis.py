from parsers.pdf_parser import extract_text_from_pdf
from analyzer.skill_extractor import extract_skills
from analyzer.matcher import compare_skills
from analyzer.scorer import calculate_score

resume_text = extract_text_from_pdf("data/uploads/resume.pdf")
jd_text = extract_text_from_pdf("data/uploads/jd.pdf")

resume_skills = extract_skills(resume_text)
jd_skills = extract_skills(jd_text)

matched, missing = compare_skills(resume_skills, jd_skills)
score = calculate_score(resume_skills, jd_skills)

print("\n========== CAREERLENS AI ==========")
print("\nResume Skills:")
print(resume_skills)
print("\nJD Skills:")
print(jd_skills)
print("\nMatched Skills:")
print(matched)
print("\nMissing Skills:")
print(missing)
print(f"\nOverall Match Score: {score}/100")
