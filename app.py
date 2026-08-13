import streamlit as st
from study_agent import study_agent, get_student_data, generate_study_plan


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("🤖 AI Study Assistant")

st.write(
    "Personalized learning assistant powered by "
    "Snowflake, RAG and Groq AI."
)


# ==========================================
# GET STUDENT DATA
# ==========================================

try:
    rows = get_student_data()

except Exception as e:
    st.error(f"Unable to load student data: {e}")
    st.stop()


# ==========================================
# CONVERT DATA
# ==========================================

subjects = []
scores = []

for subject, score in rows:
    subjects.append(subject)
    scores.append(score)


# ==========================================
# CALCULATE PERFORMANCE
# ==========================================

average_score = sum(scores) / len(scores)

strongest_subject = max(
    rows,
    key=lambda x: x[1]
)

weakest_subject = min(
    rows,
    key=lambda x: x[1]
)


# ==========================================
# DASHBOARD
# ==========================================

st.header("📊 Student Performance")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Average Score",
        f"{average_score:.1f}/100"
    )


with col2:

    st.metric(
        "Strongest Subject",
        strongest_subject[0],
        f"{strongest_subject[1]}/100"
    )


with col3:

    st.metric(
        "Needs Most Attention",
        weakest_subject[0],
        f"{weakest_subject[1]}/100"
    )


# ==========================================
# PERFORMANCE CHART
# ==========================================

st.subheader("📈 Subject Scores")

chart_data = {
    "Subject": subjects,
    "Score": scores
}

st.bar_chart(
    chart_data,
    x="Subject",
    y="Score"
)


# ==========================================
# SUBJECT DETAILS
# ==========================================

st.subheader("📚 Subject Performance")


for subject, score in rows:

    st.write(
        f"**{subject} — {score}/100**"
    )

    st.progress(
        min(score / 100, 1.0)
    )


# ==========================================
# AI STUDY ASSISTANT
# ==========================================

st.header("💬 Ask Your AI Study Assistant")


question = st.text_area(
    "Ask a question about your studies:",
    placeholder="Example: Explain normalization in simple words"
)


if st.button("🤖 Ask AI"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching study material and analyzing your performance..."
        ):

            try:

                answer = study_agent(question)

                st.subheader("🤖 AI Response")

                st.write(answer)

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )


# ==========================================
# AI STUDY PLAN
# ==========================================

st.header("📅 AI Study Plan")


st.write(
    "Generate a personalized 7-day study plan "
    "based on your performance."
)


if st.button("📅 Generate My 7-Day Study Plan"):

    with st.spinner(
        "Creating your personalized study plan..."
    ):

        try:

            plan = generate_study_plan()

            st.subheader(
                "📚 Your Personalized 7-Day Plan"
            )

            st.write(plan)

        except Exception as e:

            st.error(
                f"Unable to generate study plan: {e}"
            )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Study Assistant | "
    "Python • Snowflake • SQL • RAG • Groq • Streamlit"
)