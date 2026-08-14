import os

import snowflake.connector
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

def get_snowflake_connection():

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    return conn


# ============================================================
# GET STUDENT PERFORMANCE
# ============================================================

def get_student_progress():

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT SUBJECT, SCORE
            FROM STUDENT_PROGRESS
            WHERE SCORE IS NOT NULL
            ORDER BY SCORE DESC
        """)

        rows = cursor.fetchall()

        return rows

    finally:

        cursor.close()
        conn.close()


# ============================================================
# ANALYZE PERFORMANCE
# ============================================================

def analyze_performance(rows):

    if not rows:
        return None

    valid_rows = [
        row for row in rows
        if len(row) >= 2 and row[1] is not None
    ]

    if not valid_rows:
        return None

    # Convert scores to float
    cleaned_rows = [
        (str(row[0]), float(row[1]))
        for row in valid_rows
    ]

    # Average score
    scores = [
        score for subject, score in cleaned_rows
    ]

    average_score = sum(scores) / len(scores)

    # Highest score
    strongest_subject = max(
        cleaned_rows,
        key=lambda x: x[1]
    )

    # Lowest score
    weakest_subject = min(
        cleaned_rows,
        key=lambda x: x[1]
    )

    return {
        "rows": cleaned_rows,
        "average": average_score,
        "strongest": strongest_subject,
        "weakest": weakest_subject
    }


# ============================================================
# GET GROQ CLIENT
# ============================================================

def get_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    return Groq(api_key=api_key)


# ============================================================
# AI STUDY AGENT
# ============================================================

def study_agent(prompt):

    client = get_groq_client()

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": """
You are an AI Study Assistant for a first-year
Computer Science Engineering student.

Your job is to:

1. Analyze student performance.
2. Explain concepts simply.
3. Create personalized study plans.
4. Recommend practice strategies.
5. Give motivational guidance.

IMPORTANT:
When a weakest subject is explicitly provided,
you MUST respect that calculation.
Do not replace it with another subject.

Keep answers simple, clear and beginner-friendly.
"""
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
# GENERATE PERSONALIZED RECOMMENDATION
# ============================================================

def generate_recommendation(rows):

    analysis = analyze_performance(rows)

    if analysis is None:

        return (
            "No valid student performance data "
            "is available."
        )

    cleaned_rows = analysis["rows"]
    average = analysis["average"]
    strongest = analysis["strongest"]
    weakest = analysis["weakest"]

    # --------------------------------------------------------
    # IMPORTANT:
    # Python determines the priority subject.
    # AI does NOT decide this.
    # --------------------------------------------------------

    priority_subject = weakest[0]
    priority_score = weakest[1]

    prompt = f"""
You are helping a first-year CSE student.

Here is the student's performance:

{cleaned_rows}

Average score:
{average:.1f}

Strongest subject:
{strongest[0]} - {strongest[1]:.0f}

Weakest subject:
{weakest[0]} - {weakest[1]:.0f}

IMPORTANT INSTRUCTION:

The student's FIRST study priority has already been
calculated by the application.

FIRST PRIORITY SUBJECT:
{priority_subject}

FIRST PRIORITY SCORE:
{priority_score:.0f}

You MUST recommend {priority_subject} as the FIRST
subject to study.

Do NOT choose another subject as the first priority.

Now provide:

1. First subject to study.
2. Why it needs the most attention.
3. A simple daily study plan.
4. Important topics to study.
5. Practice recommendations.
6. How to improve the score.
7. A short motivational message.

Keep the explanation simple and suitable for
a first-year Computer Science Engineering student.
"""

    return study_agent(prompt)


# ============================================================
# ASK AI A QUESTION
# ============================================================

def ask_ai(question, rows=None):

    analysis = analyze_performance(rows)

    if analysis:

        performance_text = "\n".join(
            [
                f"{subject}: {score:.0f}"
                for subject, score
                in analysis["rows"]
            ]
        )

        average = analysis["average"]

        strongest = analysis["strongest"]

        weakest = analysis["weakest"]

        priority_subject = weakest[0]

        context = f"""
Student Performance:

{performance_text}

Average Score:
{average:.1f}

Strongest Subject:
{strongest[0]} - {strongest[1]:.0f}

Weakest Subject:
{weakest[0]} - {weakest[1]:.0f}

Calculated First Priority:
{priority_subject}
"""

    else:

        context = """
No student performance data is available.
"""

    prompt = f"""
You are an AI Study Assistant.

{context}

Student question:

{question}

IMPORTANT:

If the student asks:

"Which subject should I study first?"

The answer MUST be:

{priority_subject if analysis else "Use the available performance data."}

Do not select another subject.

For other questions, answer clearly and simply.

Consider the student's performance when
giving study advice.
"""

    return study_agent(prompt)


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("          AI STUDY ASSISTANT")
    print("=" * 50)
    print()

    try:

        # Get data from Snowflake
        rows = get_student_progress()

        # Display scores
        print("===== STUDENT PERFORMANCE =====")
        print()

        for subject, score in rows:

            print(
                f"{subject}: {score}"
            )

        print()

        # Analyze performance
        analysis = analyze_performance(rows)

        if analysis:

            print(
                f"Average Score: "
                f"{analysis['average']:.1f}"
            )

            print(
                f"Strongest Subject: "
                f"{analysis['strongest'][0]} "
                f"({analysis['strongest'][1]:.0f})"
            )

            print(
                f"Weakest Subject: "
                f"{analysis['weakest'][0]} "
                f"({analysis['weakest'][1]:.0f})"
            )

            print(
                f"Study First: "
                f"{analysis['weakest'][0]}"
            )

        print()
        print("=" * 50)

        # Ask user
        question = input(
            "Ask your question: "
        )

        # Generate AI answer
        answer = ask_ai(
            question,
            rows
        )

        print()
        print("========== AI RESPONSE ==========")
        print()
        print(answer)

        print()
        print("=" * 50)

    except Exception as e:

        print()
        print("ERROR:")
        print(e)