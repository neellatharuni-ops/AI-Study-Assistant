import os
import snowflake.connector
from dotenv import load_dotenv
from groq import Groq

# Load .env
load_dotenv()

# ==========================================
# 1. CONNECT TO SNOWFLAKE
# ==========================================

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

print("Connected to Snowflake successfully!")

cursor = conn.cursor()

# ==========================================
# 2. GET STUDENT DATA
# ==========================================

cursor.execute("""
    SELECT SUBJECT, SCORE
    FROM STUDENT_PROGRESS
""")

rows = cursor.fetchall()

print("\n===== STUDENT DATA =====")

for row in rows:
    print(f"{row[0]} : {row[1]}")

# ==========================================
# 3. PREPARE DATA FOR AI
# ==========================================

student_data = ""

for subject, score in rows:
    student_data += f"{subject}: {score}\n"

# ==========================================
# 4. CONNECT TO GROQ
# ==========================================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("\nERROR: GROQ_API_KEY not found.")
    cursor.close()
    conn.close()
    exit()

client = Groq(api_key=groq_api_key)

print("\nConnected to Groq successfully!")

# ==========================================
# 5. SEND DATA TO AI
# ==========================================

prompt = f"""
You are an AI Study Assistant for a first-year CSE student.

Here is the student's academic progress:

{student_data}

Analyze the student's performance.

Give the following:

1. Strongest subject
2. Weakest subject
3. Subject that needs the most attention
4. A simple study plan
5. Three specific suggestions for improvement
6. A short motivational message

Keep the explanation simple and easy for a college student to understand.
"""

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# ==========================================
# 6. DISPLAY AI RESPONSE
# ==========================================

print("\n========================================")
print("       AI STUDY RECOMMENDATION")
print("========================================\n")

print(response.choices[0].message.content)

# ==========================================
# 7. CLOSE CONNECTIONS
# ==========================================

cursor.close()
conn.close()

print("\n========================================")
print("Connections closed.")
print("========================================")