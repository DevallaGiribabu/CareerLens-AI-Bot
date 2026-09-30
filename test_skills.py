from parsers.pdf_parser import extract_text_from_pdf
from analyzer.skill_extractor import extract_skills

resume_text = extract_text_from_pdf("data/uploads/resume.pdf")
jd_text = extract_text_from_pdf("data/uploads/jd.pdf")

resume_skills = extract_skills(resume_text)
jd_skills = extract_skills(jd_text)

print("RESUME SKILLS:")
print(resume_skills)
print()
print("JD SKILLS:")
print(jd_skills)
