import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import altair as alt
from io import BytesIO
from collections import Counter
# Show logo image at the top
from PIL import Image

# Show logo
logo = Image.open("logo.png")
st.image(logo, width=200)

# Job roles and required skills
jobs = {
    "Data Analyst": ["Python", "SQL", "Excel", "Tableau"],
    "Marketing Analyst": ["Excel", "Google Analytics", "SEO"],
    "Web Developer": ["HTML", "CSS", "JavaScript"],
    "UX Designer": ["Figma", "Wireframing", "User Research"]
}

# App title
st.title("SkillMatch – Resume Analyzer")

# Upload section
st.subheader("Upload Resume File (.pdf or .txt)")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
resume_text = ""

# Read text from uploaded file
if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        resume_text = uploaded_file.read().decode("utf-8").lower()
    elif uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_file:
            text = ""
            for page in pdf_file:
                text += page.get_text()
            resume_text = text.lower()

# Analyze and display results
if resume_text:
    if st.button("Find Matching Jobs"):
        match_data = []
        all_missing_skills = []

        for job, skills in jobs.items():
            matched = [skill for skill in skills if skill.lower() in resume_text]
            missing = [skill for skill in skills if skill.lower() not in resume_text]
            all_missing_skills.extend(missing)
            score = len(matched) / len(skills) * 100
            match_data.append({
                "Job": job,
                "Match %": round(score, 1),
                "Matched Skills": ", ".join(matched),
                "Missing Skills": ", ".join(missing)
            })

        df = pd.DataFrame(match_data).sort_values(by="Match %", ascending=False)

        # 🧠 Resume Score Summary
        avg_score = df["Match %"].mean()
        st.subheader(f"🧠 Resume Score: {avg_score:.1f}%")
        if avg_score >= 80:
            st.success("Great job! You're highly aligned with most roles.")
        elif avg_score >= 60:
            st.warning("You're on the right track. A few skills may need improvement.")
        else:
            st.error("Consider adding more relevant skills to your resume.")

        # 📌 Top 3 Job Matches
        st.subheader("Top Job Matches")
        for _, row in df.head(3).iterrows():
            st.markdown(f"**{row['Job']}** – {row['Match %']}% match")
            st.markdown(f"Matched Skills: {row['Matched Skills'] or 'None'}")
            st.markdown(f"Missing Skills: {row['Missing Skills'] or 'None'}")
            st.markdown("---")

        # 📊 Match Score Chart
        st.subheader("Match Score Visualization")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Match %", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Job", sort="-x"),
            color=alt.value("#4C78A8")
        ).properties(width=600)
        st.altair_chart(chart)

        # 🔍 Skill Gap Analysis
        st.subheader("🔍 Skill Gap Analysis")
        skill_counts = Counter(all_missing_skills)
        top_missing = [skill for skill, _ in skill_counts.most_common(5)]
        if top_missing:
            st.markdown("**Top Missing Skills Across All Jobs:**")
            st.markdown(", ".join(top_missing))
            st.info("Consider learning or adding these skills to improve your resume match.")
        else:
            st.success("Your resume covers nearly all key skills!")

        # 📥 Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Match Results")
        st.download_button(
            label="📥 Download Match Report (Excel)",
            data=output.getvalue(),
            file_name="match_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Please upload a resume to begin.")
