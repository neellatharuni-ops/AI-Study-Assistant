
import streamlit as st

from study_agent import (
    get_student_progress,
    study_agent
)

from rag import retrieve_context


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

st.subheader(
    "Personalized AI-powered learning assistant"
)

st.write(
    """
Analyze your academic performance, identify the subjects
that need more attention, and get personalized AI-powered
study recommendations.
"""
)

st.divider()


# ============================================================
# LOAD STUDENT DATA
# ============================================================

try:

    rows = get_student_progress()

except Exception as e:

    st.error(
        "Unable to retrieve student data from Snowflake."
    )

    st.exception(e)

    st.stop()


# ============================================================
# CHECK DATA
# ============================================================

if not rows:

    st.warning(
        "No student performance data found in Snowflake."
    )

    st.info(
        "Please check the STUDENT_PROGRESS table."
    )

    st.stop()


# ============================================================
# PROCESS STUDENT DATA
# ============================================================

student_scores = {}

for row in rows:

    if len(row) < 2:
        continue

    subject = row[0]
    score = row[1]

    if subject is None or score is None:
        continue

    try:

        score = float(score)

        student_scores[str(subject)] = score

    except (ValueError, TypeError):

        continue


# ============================================================
# VALIDATE SCORES
# ============================================================

if not student_scores:

    st.error(
        "Student records were found, but no valid scores are available."
    )

    st.stop()


# ============================================================
# CALCULATE PERFORMANCE
# ============================================================

scores = list(
    student_scores.values()
)

average_score = (
    sum(scores) / len(scores)
)


strongest_subject = max(
    student_scores,
    key=student_scores.get
)

strongest_score = student_scores[
    strongest_subject
]


weakest_subject = min(
    student_scores,
    key=student_scores.get
)

weakest_score = student_scores[
    weakest_subject
]


# ============================================================
# PERFORMANCE DASHBOARD
# ============================================================

st.header("📊 Your Performance")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Average Score",
        f"{average_score:.1f}/100"
    )


with col2:

    st.metric(
        "Strongest Subject",
        strongest_subject,
        f"{strongest_score:.0f}/100"
    )


with col3:

    st.metric(
        "Needs Most Attention",
        weakest_subject,
        f"{weakest_score:.0f}/100"
    )


st.divider()


# ============================================================
# SUBJECT PERFORMANCE
# ============================================================

st.header("📚 Subject Performance")


for subject, score in student_scores.items():

    st.write(
        f"**{subject} — {score:.0f}/100**"
    )

    st.progress(
        min(
            max(
                int(score),
                0
            ),
            100
        )
    )


st.divider()


# ============================================================
# AUTOMATIC AI STUDY RECOMMENDATION
# ============================================================

st.header("🤖 AI Study Recommendation")


if st.button(
    "Generate My Study Plan",
    type="primary"
):

    with st.spinner(
        "AI is analyzing your performance..."
    ):

        recommendation_prompt = f"""
You are an AI academic study assistant.

Analyze the student's performance below.

Scores:
{student_scores}

Average score:
{average_score:.1f}

Strongest subject:
{strongest_subject} ({strongest_score:.0f}/100)

Weakest subject:
{weakest_subject} ({weakest_score:.0f}/100)

Provide a practical study recommendation.

Your response must include:

1. Which subject the student should study first.
2. Why that subject should be the first priority.
3. A recommended study duration.
4. Which topic should be studied next.
5. A simple 3-step daily study plan.
6. How the student can improve the weakest subject.
7. One motivating sentence.

Keep the answer simple and suitable for a college student.
"""

        try:

            response = study_agent(
                recommendation_prompt
            )

            st.success(
                "Personalized study plan generated!"
            )

            st.markdown(
                response
            )

        except Exception as e:

            st.error(
                "Unable to generate the study recommendation."
            )

            st.exception(e)


st.divider()


# ============================================================
# ASK AI STUDY ASSISTANT
# ============================================================

st.header("💬 Ask Your AI Study Assistant")

question = st.text_input(
    "Ask a question about your studies:",
    placeholder="Example: What is normalization?"
)


if st.button(
    "Ask AI"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            try:

                # ------------------------------------------------
                # RETRIEVE RELEVANT STUDY MATERIAL
                # ------------------------------------------------

                context = retrieve_context(
                    question
                )


                # ------------------------------------------------
                # CREATE PROMPT
                # ------------------------------------------------

                if context:

                    prompt = f"""
You are an AI Study Assistant.

Answer the student's question using the
provided study material whenever possible.

STUDY MATERIAL:
{context}

STUDENT QUESTION:
{question}

STUDENT PERFORMANCE:
{student_scores}

Instructions:

- Give a clear and simple explanation.
- Use the study material as the primary source.
- If the material contains the answer, stay consistent with it.
- Give an example when useful.
- If the question is related to a weak subject,
  encourage the student to practice that topic.
"""

                else:

                    prompt = f"""
You are an AI Study Assistant.

Answer the following student question clearly.

STUDENT QUESTION:
{question}

STUDENT PERFORMANCE:
{student_scores}

The student's weakest subject is:
{weakest_subject}

Give a simple educational explanation.
"""


                # ------------------------------------------------
                # AI RESPONSE
                # ------------------------------------------------

                response = study_agent(
                    prompt
                )


                st.subheader(
                    "🤖 AI Response"
                )

                st.markdown(
                    response
                )


            except Exception as e:

                st.error(
                    "Unable to generate an AI response."
                )

                st.exception(e)


st.divider()


# ============================================================
# STUDENT PERFORMANCE TABLE
# ============================================================

st.header("📋 Performance Summary")


display_data = []


for subject, score in student_scores.items():

    if score >= 75:

        status = "🟢 Strong"

    elif score >= 60:

        status = "🟡 Average"

    else:

        status = "🔴 Needs Improvement"


    display_data.append(
        {
            "Subject": subject,
            "Score": f"{score:.0f}/100",
            "Status": status
        }
    )


st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# STUDY PRIORITY
# ============================================================

st.header("🎯 Study Priority")


if weakest_score < 50:

    priority_message = (
        f"🔴 **High Priority:** Focus on "
        f"**{weakest_subject}** first. "
        f"Your current score is {weakest_score:.0f}/100."
    )

elif weakest_score < 60:

    priority_message = (
        f"🟠 **Medium-High Priority:** Give extra "
        f"attention to **{weakest_subject}**. "
        f"Your current score is {weakest_score:.0f}/100."
    )

elif weakest_score < 75:

    priority_message = (
        f"🟡 **Medium Priority:** Practice "
        f"**{weakest_subject}** regularly to improve."
    )

else:

    priority_message = (
        "🟢 **Good Performance:** You are performing "
        "well across your subjects. Keep practicing!"
    )


st.info(
    priority_message
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📚 AI Study Assistant | "
    "Powered by Snowflake • Groq AI • RAG • Streamlit"
)
