SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "rest api",
    "rest apis",
    "graphql",
    "linux",
    "nlp",
    "computer vision",
    "llm",
    "rag",
]


def extract_skills(text):
    text = (text or "").lower()
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return sorted(set(found_skills))
