
import os
import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
from groq import Groq

# Load local .env file
load_dotenv()


# ============================================================
# GET CONFIGURATION
# Works both locally (.env) and on Streamlit Cloud (Secrets)
# ============================================================

def get_secret(name):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return os.getenv(name)


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

def get_snowflake_connection():
    account = get_secret("SNOWFLAKE_ACCOUNT")
    user = get_secret("SNOWFLAKE_USER")
    password = get_secret("SNOWFLAKE_PASSWORD")
    warehouse = get_secret("SNOWFLAKE_WAREHOUSE")
    database = get_secret("SNOWFLAKE_DATABASE")
    schema = get_secret("SNOWFLAKE_SCHEMA")

    missing = []

    if not account:
        missing.append("SNOWFLAKE_ACCOUNT")

    if not user:
        missing.append("SNOWFLAKE_USER")

    if not password:
        missing.append("SNOWFLAKE_PASSWORD")

    if not warehouse:
        missing.append("SNOWFLAKE_WAREHOUSE")

    if not database:
        missing.append("SNOWFLAKE_DATABASE")

    if not schema:
        missing.append("SNOWFLAKE_SCHEMA")

    if missing:
        raise ValueError(
            "Missing Snowflake configuration: "
            + ", ".join(missing)
        )

    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema
    )

    return conn


# ============================================================
# GET STUDENT PROGRESS
# ============================================================

def get_student_progress():
    conn = None
    cursor = None

    try:
        conn = get_snowflake_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUBJECT, SCORE
            FROM STUDENT_PROGRESS
            ORDER BY SUBJECT
        """)

        rows = cursor.fetchall()

        return rows

    except Exception as e:
        print("Snowflake error:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# GET GROQ CLIENT
# ============================================================

def get_groq_client():
    api_key = get_secret("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    return Groq(api_key=api_key)


# ============================================================
# GET STUDENT DATA
# ============================================================

def get_student_data():
    rows = get_student_progress()

    student_data = {}

    for row in rows:
        subject = row[0]
        score = row[1]

        if subject is not None and score is not None:
            student_data[subject] = float(score)

    return student_data


# ============================================================
# GENERATE AI RESPONSE
# ============================================================

def generate_ai_response(question, student_data, retrieved_context=""):
    client = get_groq_client()

    if not student_data:
        performance_text = "No student performance data is available."
    else:
        performance_text = "\n".join(
            f"{subject}: {score}"
            for subject, score in student_data.items()
        )

    prompt = f"""
You are an AI Study Assistant for a first-year CSE student.

Student performance:
{performance_text}

Relevant study material:
{retrieved_context}

Student question:
{question}

Instructions:

1. Answer the student's question clearly and simply.
2. If the question is about a study topic, use the relevant study material.
3. Consider the student's performance when giving recommendations.
4. Identify weak subjects correctly.
5. Do not invent student scores.
6. If the student asks which subject to study first, recommend the
   subject with the LOWEST valid score.
7. Give practical and beginner-friendly advice.
8. Use simple language suitable for a first-year CSE student.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI Study Assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# ============================================================
# MAIN STUDY AGENT
# ============================================================

def study_agent(question, retrieved_context=""):
    student_data = get_student_data()

    return generate_ai_response(
        question,
        student_data,
        retrieved_context
    )


# ============================================================
# COMMAND-LINE MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("===================================")
    print("       AI STUDY ASSISTANT")
    print("===================================")
    print()

    try:
        student_data = get_student_data()

        if student_data:

            print("===== STUDENT DATA =====")

            for subject, score in student_data.items():
                print(f"{subject} : {score:g}")

            print()

        else:
            print("No student performance data found.")
            print()

        question = input("Ask your question: ")

        answer = study_agent(question)

        print()
        print("========== AI RESPONSE ==========")
        print()
        print(answer)
        print()
        print("==================================")

    except Exception as e:

        print()
        print("ERROR:")
        print(e)
        print()
