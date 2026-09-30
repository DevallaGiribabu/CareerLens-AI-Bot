from parsers.pdf_parser import extract_text_from_pdf

resume_text = extract_text_from_pdf("data/uploads/resume.pdf")
print("=" * 50)
print("RESUME TEXT")
print("=" * 50)
print(resume_text)

jd_text = extract_text_from_pdf("data/uploads/jd.pdf")
print("\n" + "=" * 50)
print("JOB DESCRIPTION")
print("=" * 50)
print(jd_text)
