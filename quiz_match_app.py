import streamlit as st
import pandas as pd

# Load the flattened CSV from GPT tagging
@st.cache_data
def load_data():
    return pd.read_csv("flattened_policy_stances.csv")

data = load_data()

# Map each policy to a topic (inferred from order)
topics = [
    "Healthcare", "Education", "Environment",
    "Government economic role", "Transparency & public engagement", "Taxation"
]
topic_blocks = {
    "Healthcare": data["policy_statement"].unique()[:5],
    "Education": data["policy_statement"].unique()[5:10],
    "Environment": data["policy_statement"].unique()[10:15],
    "Government economic role": data["policy_statement"].unique()[15:20],
    "Transparency & public engagement": data["policy_statement"].unique()[20:25],
    "Taxation": data["policy_statement"].unique()[25:30]
}

# Title and instructions
st.title("Election Manifesto Quiz")
st.write("Answer the following policy questions to find candidates who match your views.")

topic_colors = {
    "Healthcare": "#1f77b4",
    "Education": "#2ca02c",
    "Environment": "#17becf",
    "Government economic role": "#ff7f0e",
    "Transparency & public engagement": "#9467bd",
    "Taxation": "#d62728"
}

# Select topics and set importance sliders
st.header("Set Topic Importance")
st.markdown("**Use the sliders below to show how important each topic is to you.**")
selected_topics_html = "".join([
    f"<div style='background-color:{topic_colors[t]}; color:white; padding:6px; margin:2px; border-radius:6px'>{t}</div>"
    for t in topics
])


selected_topics = []
st.sidebar.markdown("<h3 style='margin-bottom:10px;'>Select which topics to include in your results:</h3>", unsafe_allow_html=True)
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
        st.sidebar.markdown(f"<div style='background-color:{color}; color:white; padding:8px 12px; border-radius:20px; font-weight:bold; display:inline-block; margin-bottom:6px;'>{t}</div>", unsafe_allow_html=True)
importance_labels = ["Not at all important", "Slightly important", "Moderately important", "Very important", "Vital"]
weights = {}
topic_colors = {
    "Healthcare": "#1f77b4",
    "Education": "#2ca02c",
    "Environment": "#17becf",
    "Government economic role": "#ff7f0e",
    "Transparency & public engagement": "#9467bd",
    "Taxation": "#d62728"
}

for topic in selected_topics:
    color = topic_colors.get(topic, "#333333")
    st.markdown(f"<div style='background-color:{color}; color:white; padding:10px; margin:10px 0; border-radius:6px; font-weight:bold'>{topic}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:18px; font-weight:bold;'>How important is {topic} to you?</div>", unsafe_allow_html=True)
    weights[topic] = st.select_slider(
        label="How important is this topic to you?",
        label_visibility="collapsed",
        options=importance_labels,
        value="Moderately important",
        help=f"Set how much this topic should influence your match results.",
        format_func=lambda x: x,
        key=f"slider_{topic}"
    )
        

# Get filtered statements based on selected topics
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
                st.markdown(f"### {statement}")
                user_input = st.radio(
                    label=statement,
                    label_visibility="collapsed",
                    options=["Agree", "Neutral", "Disagree"],
                    key=statement
                )
                user_answers[statement] = user_input
    submitted = st.form_submit_button("Find My Matches")

# Stance mapping
reverse_scores = {
    "Agree": 1,
    "Neutral": 0,
    "Disagree": -1
}

# Score candidates
if submitted:
    import matplotlib.pyplot as plt
    import seaborn as sns

    st.header("Candidate Matches")
    candidate_scores = {}
    topic_recommendations = {topic: [] for topic in selected_topics}

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

        
        
    # Sort and show top matches
    sorted_matches = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

    # Display bar chart of top matches
    match_df = pd.DataFrame(sorted_matches[:10], columns=["Candidate", "Match %"])
    fig, ax = plt.subplots()
    sns.barplot(data=match_df, x="Match %", y="Candidate", hue="Candidate", ax=ax, palette="RdYlGn_r", legend=False)
    ax.set_xlim(0, 100)
    st.pyplot(fig)

    # Show individual matches with traffic lights
    import os
    st.markdown("<h2 style='margin-top:2em'>Detailed Results</h2>", unsafe_allow_html=True)
    for name, score in sorted_matches[:10]:
        photo_path = data[data["name"] == name]["photo_path"].dropna().unique()
        if len(photo_path) > 0:
            st.image(photo_path[0], width=100)
        color = "🟢" if score >= 70 else "🟠" if score >= 40 else "🔴"
        st.markdown(f"""
        <h3 style='margin-bottom: 0.2em;'>{color} <strong>{name}</strong>: <span style='color: #333;'>{score}% match</span></h3>
        </div>""", unsafe_allow_html=True)
        with st.expander("View supporting quotes"):
            quotes = data[(data["name"] == name) & (data["quote"].notna()) & (data["policy_statement"].isin(filtered_statements))]
            for _, row in quotes.iterrows():
                if row["quote"]:
                    statement_color = next((c for t, c in topic_colors.items() if row['policy_statement'] in topic_blocks[t]), "#000")
                    st.markdown(f"<span style='color:{statement_color}; font-weight:bold'>{row['policy_statement']}</span><br><blockquote>{row['quote']}</blockquote>", unsafe_allow_html=True)

    # General topic-based suggestions (now placed after detailed results)
    st.header("General Suggestions Based on Topic Sliders")
    st.markdown("""
    These recommendations highlight candidates who have generally positive alignment on each topic.
    **The average stance score** is calculated from the AI's interpretation of how supportive the candidate is on related issues:
    - `+2 = Strongly support`, `+1 = Support`, `0 = Neutral`, `-1 = Oppose`, `-2 = Strongly oppose`

    So a candidate with a high average score (e.g. 1.2) is overall supportive on that topic.
    If you've marked a topic as **'Vital'**, we flag partial mismatches to help you stay aligned with your priorities.
    """)
    for topic in selected_topics:
        top_candidates = []
        topic_statements = topic_blocks[topic]
        for other_name in data["name"].unique():
            candidate_data = data[(data["name"] == other_name) & (data["policy_statement"].isin(topic_statements))]
            avg_score = candidate_data["stance_score"].mean()
            if avg_score > 0.5:
                top_candidates.append((other_name, round(avg_score, 2)))

        if top_candidates:
            color = topic_colors.get(topic, "#000")
            st.markdown(f"<h3 style='color:{color}'>{topic}</h3>", unsafe_allow_html=True)
            for n, avg in sorted(top_candidates, key=lambda x: x[1], reverse=True)[:3]:
                color = "🟢" if avg >= 1.0 else "🟠" if avg >= 0.5 else "🔴"
                if weights[topic] == "Vital" and avg < 1.0:
                    st.warning(f"⚠️ {n} may not fully align with your priority on **{topic}**.")
                st.markdown(f"- **{color} {n}** — *avg score: {avg}*", unsafe_allow_html=True)

    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    


    








