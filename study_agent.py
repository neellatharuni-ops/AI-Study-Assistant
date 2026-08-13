import os
import snowflake.connector
from dotenv import load_dotenv
from groq import Groq

from rag import retrieve_context

load_dotenv()


# ==========================================
# GET STUDENT DATA FROM SNOWFLAKE
# ==========================================

def get_student_data():

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUBJECT, SCORE
        FROM STUDENT_PROGRESS
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# ==========================================
# AI STUDY AGENT
# ==========================================

def study_agent(question):

    rows = get_student_data()

    student_data = ""

    for subject, score in rows:
        student_data += f"{subject}: {score}\n"

    # Get relevant study material
    study_context = retrieve_context(question)

    # Connect to Groq
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are an AI Study Assistant for a first-year CSE student.

STUDENT PERFORMANCE:

{student_data}

RELEVANT STUDY MATERIAL:

{study_context}

STUDENT QUESTION:

{question}

INSTRUCTIONS:

1. Answer the student's question clearly.
2. Use the study material when relevant.
3. Use the student's performance to personalize the advice.
4. Do not invent information from the study material.
5. Explain difficult concepts in simple language.
6. Give examples when useful.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ==========================================
# GENERATE 7-DAY STUDY PLAN
# ==========================================

def generate_study_plan():

    rows = get_student_data()

    student_data = ""

    for subject, score in rows:
        student_data += f"{subject}: {score}\n"

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are an AI Study Planner.

The student's current scores are:

{student_data}

Create a practical 7-day study plan.

Rules:

1. Give the weakest subjects more study time.
2. Give the lowest-scoring subject the highest priority.
3. Include all subjects.
4. Give specific topics to study.
5. Include practice and revision.
6. Keep the plan suitable for a first-year CSE student.
7. Make the plan easy to follow.

Format:

DAY 1:
Subject:
Topics:
Study Time:
Practice:

DAY 2:
Subject:
Topics:
Study Time:
Practice:

Continue until DAY 7.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ==========================================
# TEST FROM TERMINAL
# ==========================================

if __name__ == "__main__":

    print("\n===================================")
    print("       AI STUDY ASSISTANT")
    print("===================================")

    question = input(
        "\nAsk your question: "
    )

    answer = study_agent(question)

    print("\n========== AI RESPONSE ==========\n")

    print(answer)

    print("\n===================================")