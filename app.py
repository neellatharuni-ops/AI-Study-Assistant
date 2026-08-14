
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
This application analyzes your academic performance,
identifies subjects that need attention, and uses AI
to provide personalized study recommendations.
"""
)

st.divider()


# ============================================================
# GET STUDENT PROGRESS FROM SNOWFLAKE
# ============================================================

try:

    rows = get_student_progress()

except Exception as e:

    st.error("Unable to retrieve student data from Snowflake.")

    st.exception(e)

    st.stop()


# ============================================================
# TEMPORARY DEBUG INFORMATION
# ============================================================

st.write(
    "DEBUG: Snowflake rows returned:",
    rows
)


# ============================================================
# CHECK WHETHER DATA EXISTS
# ============================================================

if not rows:

    st.warning(
        "No student performance data found in Snowflake."
    )

    st.info(
        "Please check the STUDENT_PROGRESS table and "
        "your Streamlit Cloud Snowflake secrets."
    )

    st.stop()


# ============================================================
# PROCESS VALID SCORES
# ============================================================

valid_rows = []

for row in rows:

    if len(row) >= 2:

        subject = row[0]
        score = row[1]

        if subject is not None and score is not None:

            try:

                score = float(score)

                valid_rows.append(
                    (
                        str(subject),
                        score
                    )
                )

            except (ValueError, TypeError):

                continue


# ============================================================
# CHECK VALID SCORES
# ============================================================

if not valid_rows:

    st.error(
        "Student records were found, but no valid scores are available."
    )

    st.stop()


# ============================================================
# CREATE SCORE DICTIONARY
# ============================================================

student_scores = {}

for subject, score in valid_rows:

    student_scores[subject] = score


# ============================================================
# CALCULATE AVERAGE
# ============================================================

scores = list(
    student_scores.values()
)

average_score = (
    sum(scores) / len(scores)
)


# ============================================================
# STRONGEST AND WEAKEST SUBJECT
# ============================================================

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
        f"{average_score:.1f}"
    )


with col2:

    st.metric(
        "Strongest Subject",
        strongest_subject,
        f"{strongest_score:.0f}"
    )


with col3:

    st.metric(
        "Needs Most Attention",
        weakest_subject,
        f"{weakest_score:.0f}"
    )


st.divider()


# ============================================================
# SUBJECT PERFORMANCE
# ============================================================

st.header("📚 Subject Performance")


for subject, score in student_scores.items():

    col1, col2 = st.columns(
        [2, 5]
    )

    with col1:

        st.write(
            f"**{subject}**"
        )

    with col2:

        st.progress(
            min(
                max(
                    int(score),
                    0
                ),
                100
            )
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
    "Generate My Study Recommendation",
    type="primary"
):

    with st.spinner(
        "Analyzing your performance..."
    ):

        try:

            question = f"""
Analyze my academic performance.

My scores are:

{student_scores}

My average score is {average_score:.1f}.

My strongest subject is
{strongest_subject} with a score of
{strongest_score:.0f}.

My weakest subject is
{weakest_subject} with a score of
{weakest_score:.0f}.

Tell me:

1. Which subject should I study first?
2. Why should I study it first?
3. How much time should I spend on it?
4. What should I study next?
5. Give me a simple daily study plan.
"""

            response = study_agent(
                question
            )

            st.success(
                "Recommendation generated!"
            )

            st.markdown(
                response
            )

        except Exception as e:

            st.error(
                "Unable to generate AI recommendation."
            )

            st.exception(e)


st.divider()


# ============================================================
# ASK AI
# ============================================================

st.header("💬 Ask Your AI Study Assistant")


question = st.text_input(
    "Ask a question about your studies:",
    placeholder="Example: Which subject should I study first?"
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
            "Thinking..."
        ):

            try:

                # ------------------------------------------------
                # RETRIEVE RELEVANT STUDY MATERIAL
                # ------------------------------------------------

                try:

                    context = retrieve_context(
                        question
                    )

                except Exception:

                    context = ""


                # ------------------------------------------------
                # GENERATE AI RESPONSE
                # ------------------------------------------------

                response = study_agent(
                    question,
                    context
                )

                st.subheader(
                    "🤖 AI Response"
                )

                st.markdown(
                    response
                )

            except Exception as e:

                st.error(
                    "Unable to generate response."
                )

                st.exception(e)


# ============================================================
# STUDENT DATA TABLE
# ============================================================

st.divider()

st.header("📋 Student Performance Data")


display_data = []

for subject, score in student_scores.items():

    display_data.append(
        {
            "Subject": subject,
            "Score": score
        }
    )


st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📚 AI Study Assistant | "
    "Powered by Snowflake, Groq AI, RAG and Streamlit"
)
