import os
import mysql.connector
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
ssl_ca_path = os.path.join(current_dir, os.getenv("TIDB_SSL_CA"))

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_tidb_connection():
    return mysql.connector.connect(
        host=os.getenv("TIDB_HOST"),
        port=int(os.getenv("TIDB_PORT")),
        user=os.getenv("TIDB_USERNAME"),
        password=os.getenv("TIDB_PASSWORD"),
        database=os.getenv("TIDB_DATABASE"),
        ssl_ca=ssl_ca_path, 
        # ssl_verify_cert=True,
        # ssl_verify_identity=True
        autocommit=True
    )

def insert_job_description(cursor, jd_content, jd_data):
    jd_hash = compute_hash(jd_content)
    print("jd_data", jd_data)

    sql = """
    INSERT INTO job_descriptions 
    (job_title, company, location, education_requirement, salary, responsibilities, required_skills, preferred_skills, experience, jd_hash) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
    """
    values = (
        jd_data.get("job_title"),
        jd_data.get("company"),
        jd_data.get("location"),
        jd_data.get("education_requirement"),
        jd_data.get("salary"),
        json.dumps(jd_data.get("responsibilities", [])),
        json.dumps(jd_data.get("required_skills", [])),
        json.dumps(jd_data.get("preferred_skills", [])),
        json.dumps(jd_data.get("experience", {})),
        jd_hash,
    )
    print('value: ',values)
    cursor.execute(sql, values)
    return cursor.lastrowid


def insert_candidate(cursor, job_id, resume_data):
    sql = """
    INSERT INTO candidates 
    (job_id, name, email, phone, education, work_experience, skills, certifications, languages) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        job_id,
        resume_data.get("name"),
        resume_data.get("email"),
        resume_data.get("phone"),
        json.dumps(resume_data.get("education", [])),
        json.dumps(resume_data.get("work_experience", [])),
        json.dumps(resume_data.get("skills", [])),
        json.dumps(resume_data.get("certifications", [])),
        json.dumps(resume_data.get("languages", [])),
    )
    cursor.execute(sql, values)

def update_candidate_match_score(cursor, candidate_id, match_score):
    query = """
    UPDATE candidates
    SET match_score = %s
    WHERE id = %s
    """
    cursor.execute(query, (match_score, candidate_id))
