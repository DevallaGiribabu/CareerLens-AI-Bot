import unittest

from app.services.analyzer import analyze_resume_and_jd


class AnalyzerTests(unittest.TestCase):
    def test_detects_common_skills_and_missing_gaps(self):
        resume = "Python, SQL, FastAPI, Machine Learning, AI, Power BI, Git"
        jd = "We need a Python developer with SQL, FastAPI, Docker, AWS, AI, and Machine Learning skills."

        result = analyze_resume_and_jd(resume, jd)

        self.assertIn("python", result["matched_skills"])
        self.assertIn("sql", result["matched_skills"])
        self.assertIn("fastapi", result["matched_skills"])
        self.assertIn("docker", result["missing_skills"])
        self.assertIn("aws", result["missing_skills"])
        self.assertGreater(result["score"], 0)

    def test_handles_artificial_intelligence_aliases(self):
        resume = "Experienced in Artificial Intelligence, Python, and SQL"
        jd = "Role requires AI, Python, and SQL"

        result = analyze_resume_and_jd(resume, jd)

        self.assertIn("python", result["matched_skills"])
        self.assertIn("sql", result["matched_skills"])


if __name__ == "__main__":
    unittest.main()
