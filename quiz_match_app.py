import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("flattened_policy_stances.csv")

data = load_data()

# Define updated topics and colors
topics = [
    "Housing",
    "Healthcare",
    "Education",
    "Taxation & Public Finance",
    "Economy & Business",
    "Employment & Skills",
    "Transport & Connectivity",
    "Social Care & Community Wellbeing",
    "Governance & Political Reform",
    "Environment & Sustainability"
]

topic_colors = {
    "Housing": "#e6194b",
    "Healthcare": "#3cb44b",
    "Education": "#ffe119",
    "Taxation & Public Finance": "#4363d8",
    "Economy & Business": "#f58231",
    "Employment & Skills": "#911eb4",
    "Transport & Connectivity": "#46f0f0",
    "Social Care & Community Wellbeing": "#f032e6",
    "Governance & Political Reform": "#bcf60c",
    "Environment & Sustainability": "#fabebe"
}

# Map policy statements to topics
topic_blocks = {
    topic: data[data["topic"] == topic]["policy_statement"].unique()
    for topic in topics
}

# Title and instructions
st.title("Election Manifesto Quiz")
st.write("Answer the following policy questions to find candidates who match your views.")

# Sidebar topic selection
selected_topics = []
st.sidebar.markdown("<h3>Select which topics to include in your results:</h3>", unsafe_allow_html=True)
if st.sidebar.button("Reset topic selections"):
    for t in topics:
        st.session_state[f"toggle_{t}"] = False
if st.sidebar.button("Select all topics"):
    for t in topics:
        st.session_state[f"toggle_{t}"] = True

for t in topics:
    color = topic_colors.get(t, "#333")
    if st.sidebar.checkbox(label=t, value=True, key=f"toggle_{t}"):
        selected_topics.append(t)
        st.sidebar.markdown(
            f"<div style='background-color:{color}; color:white; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; margin-bottom:6px;'>{t}</div>",
            unsafe_allow_html=True
        )

# Topic importance sliders
importance_labels = ["Not at all important", "Slightly important", "Moderately important", "Very important", "Vital"]
weights = {}
for topic in selected_topics:
    color = topic_colors.get(topic, "#333333")
    st.markdown(f"<div style='background-color:{color}; color:white; padding:10px; margin:10px 0; border-radius:6px; font-weight:bold'>{topic}</div>", unsafe_allow_html=True)
    weights[topic] = st.select_slider(
        label="How important is this topic to you?",
        label_visibility="collapsed",
        options=importance_labels,
        value="Moderately important",
        key=f"slider_{topic}"
    )

# Get filtered statements
filtered_statements = []
for topic in selected_topics:
    filtered_statements.extend(topic_blocks[topic])

# Get user input
user_answers = {}
with st.form("quiz_form"):
    for topic in selected_topics:
        color = topic_colors.get(topic, "#000000")
        st.markdown(f"<h3 style='color:{color}'>{topic}</h3>", unsafe_allow_html=True)
        for statement in topic_blocks[topic]:
            if statement in filtered_statements:
                user_input = st.radio(
                    label=statement,
                    label_visibility="collapsed",
                    options=["Agree", "Neutral", "Disagree"],
                    key=statement
                )
                user_answers[statement] = user_input
    submitted = st.form_submit_button("Find My Matches")

# Scoring
reverse_scores = {"Agree": 1, "Neutral": 0, "Disagree": -1}

if submitted:
    if not selected_topics:
        st.warning("Please select at least one topic to see candidate matches.")

    st.header("Candidate Matches")
    candidate_scores = {}
    label_to_weight = {
        "Not at all important": 0,
        "Slightly important": 2,
        "Moderately important": 5,
        "Very important": 8,
        "Vital": 10
    }

    for name in data["name"].unique():
        candidate_data = data[data["name"] == name]
        score = 0
        max_score = 0

        for _, row in candidate_data.iterrows():
            statement = row["policy_statement"]
            topic_weight = 1
            for topic in selected_topics:
                if statement in topic_blocks[topic]:
                    topic_weight = label_to_weight[weights[topic]]
                    break

            if statement in user_answers:
                user_val = reverse_scores.get(user_answers[statement], 0)
                candidate_val = row["stance_score"]
                score += user_val * candidate_val * topic_weight
                max_score += 4 * topic_weight

        match_percent = round((score / max_score) * 100, 1) if max_score > 0 else 0
        candidate_scores[name] = match_percent

    # Show top matches
    sorted_matches = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    match_df = pd.DataFrame(sorted_matches[:10], columns=["Candidate", "Match %"])
    fig, ax = plt.subplots()
    sns.barplot(data=match_df, x="Match %", y="Candidate", ax=ax, palette="RdYlGn_r")
    ax.set_xlim(0, 100)
    st.pyplot(fig)

    # Show detailed match quotes
    st.markdown("<h2 style='margin-top:2em'>Detailed Results</h2>", unsafe_allow_html=True)
    for name, score in sorted_matches[:10]:
        st.markdown(f"<h3><strong>{name}</strong>: {score}% match</h3>", unsafe_allow_html=True)
        with st.expander("View supporting quotes"):
            if "filtered_statements" in locals() and filtered_statements:
                quotes = data[
                    (data["name"] == name) &
                    (data["quote"].notna()) &
                    (data["policy_statement"].isin(filtered_statements))
                ]
            else:
                quotes = pd.DataFrame()
            for _, row in quotes.iterrows():
                if row["quote"]:
                    color = next((c for t, c in topic_colors.items() if row['policy_statement'] in topic_blocks[t]), "#000")
                    st.markdown(f"<span style='color:{color}; font-weight:bold'>{row['policy_statement']}</span><br><blockquote>{row['quote']}</blockquote>", unsafe_allow_html=True)


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    








