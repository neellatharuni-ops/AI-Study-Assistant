import streamlit as st
import os
from dotenv import load_dotenv

# Import functions from your project
from study_agent import get_student_progress, study_agent
from rag import retrieve_relevant_content


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📚 AI Study Assistant")
st.subheader("Personalized AI-powered learning assistant")

st.markdown(
    """
    This application analyzes your academic performance,
    identifies subjects that need attention, and uses AI
    to provide personalized study recommendations.
    """
)

st.divider()


# ============================================================
# LOAD STUDENT DATA
# ============================================================

try:
    rows = get_student_progress()

except Exception as e:
    st.error("Unable to retrieve student data from Snowflake.")
    st.exception(e)
    st.stop()


# ============================================================
# HANDLE EMPTY DATA
# ============================================================

if not rows:
    st.warning("⚠️ No student performance data found in Snowflake.")

    st.info(
        "Please add student records to the STUDENT_PROGRESS table."
    )

    st.stop()


# ============================================================
# REMOVE INVALID SCORES
# ============================================================

valid_rows = [
    row for row in rows
    if len(row) >= 2 and row[1] is not None
]


if not valid_rows:
    st.error(
        "Student records were found, but no valid scores are available."
    )

    st.stop()


# ============================================================
# PROCESS SCORES
# ============================================================

scores = [
    float(row[1])
    for row in valid_rows
]


average_score = sum(scores) / len(scores)


strongest_subject = max(
    valid_rows,
    key=lambda x: float(x[1])
)


weakest_subject = min(
    valid_rows,
    key=lambda x: float(x[1])
)


# ============================================================
# PERFORMANCE DASHBOARD
# ============================================================

st.header("📊 Your Performance")


col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Average Score",
        f"{average_score:.1f}"
    )


with col2:
    st.metric(
        "Strongest Subject",
        f"{strongest_subject[0]} ({strongest_subject[1]})"
    )


with col3:
    st.metric(
        "Needs Most Attention",
        f"{weakest_subject[0]} ({weakest_subject[1]})"
    )


st.divider()


# ============================================================
# SUBJECT PERFORMANCE
# ============================================================

st.header("📚 Subject Performance")


for row in valid_rows:

    subject = row[0]
    score = float(row[1])

    col1, col2 = st.columns([2, 5])

    with col1:
        st.write(f"**{subject}**")

    with col2:
        st.progress(
            min(int(score), 100)
        )

        st.caption(
            f"Score: {score:.0f}/100"
        )


st.divider()


# ============================================================
# AI STUDY RECOMMENDATION
# ============================================================

st.header("🤖 AI Study Recommendation")


if st.button(
    "Generate Personalized Study Recommendation",
    type="primary"
):

    with st.spinner("Analyzing your performance with AI..."):

        try:

            prompt = f"""
You are an AI Study Assistant.

Analyze the student's performance below:

{valid_rows}

Average score: {average_score:.1f}

Strongest subject:
{strongest_subject[0]} - {strongest_subject[1]}

Weakest subject:
{weakest_subject[0]} - {weakest_subject[1]}

Provide:

1. Subject the student should study first.
2. Why that subject needs attention.
3. A simple daily study plan.
4. Topics the student should prioritize.
5. Practice suggestions.
6. A short motivational message.

Keep the explanation simple and suitable for a first-year
Computer Science engineering student.
"""

            response = study_agent(prompt)

            st.success("AI recommendation generated!")

            st.markdown(response)

        except Exception as e:

            st.error(
                "Unable to generate AI recommendation."
            )

            st.exception(e)


st.divider()


# ============================================================
# RAG STUDY MATERIAL SEARCH
# ============================================================

st.header("🔎 Ask Your Study Material")


st.write(
    "Ask a question and retrieve relevant information "
    "from your study materials."
)


question = st.text_input(
    "Enter your question",
    placeholder="Example: What is normalization?"
)


if st.button("Search Study Material"):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            try:

                content = retrieve_relevant_content(
                    question
                )

                st.success(
                    "Relevant study material found!"
                )

                st.subheader(
                    "📖 Retrieved Content"
                )

                st.write(content)

            except Exception as e:

                st.error(
                    "Unable to search study materials."
                )

                st.exception(e)


st.divider()


# ============================================================
# ASK AI ABOUT YOUR STUDIES
# ============================================================

st.header("💬 Ask AI Study Assistant")


user_question = st.text_input(
    "Ask anything about your studies",
    placeholder="Example: Which subject should I study first?"
)


if st.button("Ask AI"):

    if not user_question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "AI is thinking..."
        ):

            try:

                # Include student performance in the AI context
                context = f"""
Student performance:

{valid_rows}

Average score: {average_score:.1f}

Strongest subject:
{strongest_subject[0]} - {strongest_subject[1]}

Weakest subject:
{weakest_subject[0]} - {weakest_subject[1]}
"""

                prompt = f"""
You are an AI Study Assistant helping a first-year
Computer Science engineering student.

{context}

Student question:
{user_question}

Give a clear, simple and useful answer.

If the question is about study planning,
consider the student's performance.
"""

                response = study_agent(prompt)

                st.subheader(
                    "🤖 AI Response"
                )

                st.write(response)

            except Exception as e:

                st.error(
                    "Unable to generate AI response."
                )

                st.exception(e)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Study Assistant | Python • Groq LLM • Snowflake • RAG • Streamlit"
)