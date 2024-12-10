from fastapi import FastAPI, File, UploadFile
import pdfplumber
import os
import re
from datetime import datetime

app = FastAPI()

SKILLS_KEYWORDS = [
    "Python", "JavaScript", "Java", "C++", "HTML", "CSS", "React", "Angular",
    "Node.js", "SQL", "NoSQL", "AWS", "Azure", "Docker", "Kubernetes",
    "Linux", "Git", "CI/CD", "Machine Learning", "Data Analysis", "Django",
    "Flask", "REST APIs", "GraphQL", "C#", "C", "MySQL", "PostgreSQL", "SQL",
    "MongoDB", "GitHub", "Frontend", "Backend", "PHP", ".NET", "Framework",
    "TypeScript", "Arduino", "Bases de Datos", "TensorFlow", "PyTorch",
    "OpenCV", "Hadoop", "Spark", "Tableau", "Power BI", "MATLAB", "Scikit-learn",
    "Pandas", "NumPy", "Keras", "Scrum", "Agile", "JIRA", "Bitbucket",
    "Firebase", "Heroku", "Spring Boot", "Bootstrap", "SASS", "LESS", 
    "Webpack", "Babel", "Flutter", "Swift", "Objective-C", "Kotlin",
    "Unity", "Unreal Engine", "VR/AR", "SQL Server", "Oracle", "Redis",
    "Elasticsearch", "Apache Kafka", "GraphQL", "SOAP", "Terraform",
    "Ansible", "Puppet", "Chef", "Jenkins", "Travis CI", "CircleCI",
    "GCP (Google Cloud Platform)", "Vagrant", "Cybersecurity", "Penetration Testing",
    "Encryption", "OAuth", "JWT", "SAML", "RSA", "Cryptography", "CloudFormation",
    "Network Security", "Virtualization", "VMware", "Hyper-V", "Mobile Development",
    "Game Development", "AI (Artificial Intelligence)", "NLP (Natural Language Processing)",
    "Computer Vision", "Big Data", "ETL", "Data Warehousing", "Business Intelligence",
    "DevOps", "System Design", "Software Architecture", "API Design", "UML", "Wireframing",
    "Figma", "Adobe XD", "Sketch", "Prototyping", "Testing", "Unit Testing",
    "Integration Testing", "End-to-End Testing", "QA Automation", "Selenium", "Cypress",
    "Appium", "Robot Framework", "Performance Testing", "Load Balancing", "Cloud Security"
    
]

# Diccionario de habilidades agrupadas por categoría
SKILLS_CATEGORIES = {
    "Mobile Development": [
        "Flutter", "Swift", "Objective-C", "Kotlin", "React Native", "Mobile Development", "Android", "iOS"
    ],
    "Web Development": [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Node.js", "PHP", "TypeScript", "Django", "Flask", "Bootstrap", "SASS", "LESS", "Vue.js"
    ],
    "Data Science": [
        "Data Analysis", "Pandas", "NumPy", "MATLAB", "Tableau", "Power BI", "Scikit-learn", "Hadoop", "Spark", "ETL", "Big Data", "Data Warehousing", "Business Intelligence"
    ],
    "Machine Learning": [
        "Machine Learning", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "AI (Artificial Intelligence)", "NLP (Natural Language Processing)", "Computer Vision"
    ],
    "Databases": [
        "SQL", "NoSQL", "MySQL", "PostgreSQL", "MongoDB", "SQL Server", "Oracle", "Redis", "Elasticsearch", "Firebase"
    ],
    "Cloud": [
        "AWS", "Azure", "GCP (Google Cloud Platform)", "Heroku", "CloudFormation", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD", "CircleCI", "Vagrant"
    ],
    "DevOps": [
        "DevOps", "Linux", "Git", "JIRA", "Bitbucket", "Scrum", "Agile", "Docker", "Kubernetes", "Ansible", "Puppet", "Chef", "Jenkins", "Travis CI", "CircleCI"
    ],
    "Game Development": [
        "Unity", "Unreal Engine", "Game Development", "VR/AR"
    ],
    "Cybersecurity": [
        "Cybersecurity", "Penetration Testing", "Encryption", "OAuth", "JWT", "SAML", "RSA", "Cryptography", "Cloud Security", "Network Security"
    ],
    "System Design & Architecture": [
        "System Design", "Software Architecture", "API Design", "UML", "Wireframing"
    ],
    "Testing & QA": [
        "Unit Testing", "Integration Testing", "End-to-End Testing", "QA Automation", "Selenium", "Cypress", "Appium", "Robot Framework", "Performance Testing", "Load Balancing"
    ],
    "Frontend": [
        "Frontend", "HTML", "CSS", "JavaScript", "React", "Vue.js", "Bootstrap", "SASS", "LESS"
    ],
    "Backend": [
        "Backend", "Node.js", "PHP", "Django", "Flask", "Java", "C#", ".NET", "Spring Boot"
    ]
}

COMMON_JOB_TITLES = [
    "Software Engineer", "Data Scientist", "Web Developer", "Project Manager",
    "System Analyst", "Full Stack Developer", "Machine Learning Engineer",
    "Data Analyst", "Backend Developer", "Frontend Developer", "DevOps Engineer", 
    "Mechatronics Enginner", "IT Enginner", "Development","Developer", "Enginnering Intern",

]


def extract_skills_category(text:str, categories: dict) -> dict:
    skill_count = { category: 0 for category in categories}
    for category, skills in categories.items():
        for skill in skills:
            if skill.lower() in text.lower():
                skill_count[category]+= 1
    return skill_count

def calculate_average_duration(text):
    year_pattern = r"(\b\d{4}\b)\s*[-–]\s*(\b\d{4}\b|\bPresent\b)"
    matches = re.findall(year_pattern, text)

    durations = []
    for start, end in matches:
        start_year = int(start)
        end_year = datetime.now().year if end.lower() == "present" else int(end)
        durations.append(end_year -  start_year)

    if durations:
        return sum(durations)/len(durations)
    
    return 0


def extract_job_titles(text):
    roles_found = [role for role in COMMON_JOB_TITLES if role.lower() in text.lower()]
    return roles_found

def extract_skills(text:str, keywords:list) -> list:
    skills_found = []
    for keyword in keywords:
        if keyword.lower() in text.lower():
            skills_found.append(keyword)
    return skills_found

@app.post("/information-cv")

async def proccess_information_cv(file: UploadFile = File(...)):
    temp_file_path = f"./temp_{file.filename}"

    try:
        with open(temp_file_path, "wb") as f:
             f.write(await file.read())
            
        with pdfplumber.open(temp_file_path) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages ])

        skills_count = extract_skills_category(text, SKILLS_CATEGORIES)
        skills = extract_skills(text, SKILLS_KEYWORDS)
        roles = extract_job_titles(text)
        average_duration = calculate_average_duration(text)
        return {
                "skills": skills,
                "skills_count": skills_count,
                "job_titles": roles,
                "duration_in_jobs": average_duration
                }
    except Exception as  e:
        return {"Error": e}
    finally: 
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)