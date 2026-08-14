
import os

import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
from groq import Groq

# ============================================================
# LOAD LOCAL ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GET SECRET
# Works with:
# 1. Streamlit Cloud Secrets
# 2. Local .env file
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
            "Missing Snowflake secrets: "
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
# GET STUDENT PROGRESS FROM SNOWFLAKE
# ============================================================

def get_student_progress():

    conn = None
    cursor = None

    try:

        conn = get_snowflake_connection()

        cursor = conn.cursor()

        # Explicit database + schema + table
        cursor.execute("""
            SELECT SUBJECT, SCORE
            FROM AI_STUDY_DB.PUBLIC.STUDENT_PROGRESS
            WHERE SCORE IS NOT NULL
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
# GET STUDENT DATA AS DICTIONARY
# ============================================================

def get_student_data():

    rows = get_student_progress()

    student_data = {}

    for row in rows:

        subject = row[0]
        score = row[1]

        if subject is not None and score is not None:

            student_data[str(subject)] = float(score)

    return student_data


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():

    api_key = get_secret("GROQ_API_KEY")

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file or Streamlit Secrets."
        )

    client = Groq(
        api_key=api_key
    )

    return client


# ============================================================
# GENERATE AI RESPONSE
# ============================================================

def generate_ai_response(
    question,
    student_data,
    retrieved_context=""
):

    client = get_groq_client()

    # --------------------------------------------------------
    # STUDENT PERFORMANCE
    # --------------------------------------------------------

    if student_data:

        performance_text = "\n".join(
            f"{subject}: {score:g}"
            for subject, score in student_data.items()
        )

        # Find weakest subject
        weakest_subject = min(
            student_data,
            key=student_data.get
        )

        weakest_score = student_data[weakest_subject]

        # Find strongest subject
        strongest_subject = max(
            student_data,
            key=student_data.get
        )

        strongest_score = student_data[strongest_subject]

    else:

        performance_text = "No student performance data available."

        weakest_subject = "Unknown"
        weakest_score = 0

        strongest_subject = "Unknown"
        strongest_score = 0

    # --------------------------------------------------------
    # STUDY MATERIAL
    # --------------------------------------------------------

    if retrieved_context:

        study_material = retrieved_context

    else:

        study_material = "No additional study material was retrieved."

    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an AI Study Assistant for a first-year CSE student.

The student's current academic performance is:

{performance_text}

Weakest subject:
{weakest_subject} with score {weakest_score:g}

Strongest subject:
{strongest_subject} with score {strongest_score:g}

Relevant study material:

{study_material}

Student's question:

{question}

Follow these rules carefully:

1. Answer the student's question clearly.
2. Use simple language suitable for a first-year CSE student.
3. If study material is provided, use it when answering academic questions.
4. Do not invent student scores.
5. If the student asks which subject to study first,
   recommend the subject with the LOWEST score.
6. If multiple subjects have the same lowest score,
   mention all of them.
7. Give practical study advice.
8. If the question is about a concept, explain it with a simple example.
9. Do not claim that a subject is weak if its score is not the lowest.
10. Keep the answer focused and useful.
"""

    # --------------------------------------------------------
    # GROQ REQUEST
    # --------------------------------------------------------

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are a helpful, accurate and "
                    "student-friendly AI Study Assistant."
                )
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.2
    )

    return response.choices[0].message.content


# ============================================================
# MAIN STUDY AGENT
# ============================================================

def study_agent(
    question,
    retrieved_context=""
):

    student_data = get_student_data()

    answer = generate_ai_response(
        question=question,
        student_data=student_data,
        retrieved_context=retrieved_context
    )

    return answer


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("===================================")
    print("       AI STUDY ASSISTANT")
    print("===================================")
    print()

    try:

        # ----------------------------------------------------
        # GET STUDENT DATA
        # ----------------------------------------------------

        student_data = get_student_data()

        print("===== STUDENT DATA =====")

        if student_data:

            for subject, score in student_data.items():

                print(
                    f"{subject} : {score:g}"
                )

        else:

            print(
                "No student performance data found."
            )

        print()

        # ----------------------------------------------------
        # FIND WEAKEST SUBJECT
        # ----------------------------------------------------

        if student_data:

            weakest_subject = min(
                student_data,
                key=student_data.get
            )

            weakest_score = student_data[
                weakest_subject
            ]

            print(
                f"Weakest subject: "
                f"{weakest_subject} "
                f"({weakest_score:g})"
            )

        print()

        # ----------------------------------------------------
        # ASK QUESTION
        # ----------------------------------------------------

        question = input(
            "Ask your question: "
        )

        # ----------------------------------------------------
        # GENERATE RESPONSE
        # ----------------------------------------------------

        answer = study_agent(
            question
        )

        print()
        print("========== AI RESPONSE ==========")
        print()
        print(answer)
        print()
        print("===================================")

    except Exception as e:

        print()
        print("ERROR:")
        print(e)
        print()

