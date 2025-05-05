# SkillMatch Advanced App with PDF Summary, AI Feedback, and Role Tips
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import altair as alt
from io import BytesIO
from collections import Counter
from PIL import Image
from fpdf import FPDF

# --- Logo and Title ---
logo = Image.open("logo.png")
st.image(logo, width=200)
st.title("SkillMatch – Resume Analyzer (Pro Edition)")

# --- Job Roles by Category ---
job_categories = {
    "Tech": {
        "Data Analyst": ["Python", "SQL", "Excel", "Tableau"],
        "Web Developer": ["HTML", "CSS", "JavaScript"]
    },
    "Marketing": {
        "Marketing Analyst": ["Excel", "Google Analytics", "SEO"]
    },
    "Design": {
        "UX Designer": ["Figma", "Wireframing", "User Research"]
    }
}

role_tips = {
    "Data Analyst": "Highlight SQL and Tableau project experience.",
    "Web Developer": "Include GitHub links to live websites.",
    "Marketing Analyst": "Emphasize Google Analytics certification.",
    "UX Designer": "Add case studies showing wireframing and research."
}

course_links = {
    "Python": "https://www.coursera.org/learn/python",
    "SQL": "https://www.khanacademy.org/computing/computer-programming/sql",
    "Excel": "https://www.udemy.com/course/microsoft-excel-all-in-one/",
    "Tableau": "https://www.coursera.org/learn/data-visualization-tableau",
    "Google Analytics": "https://analytics.google.com/analytics/academy/",
    "SEO": "https://www.coursera.org/learn/seo-fundamentals",
    "HTML": "https://www.codecademy.com/learn/learn-html",
    "CSS": "https://www.codecademy.com/learn/learn-css",
    "JavaScript": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
    "Figma": "https://www.coursera.org/projects/introduction-to-figma",
    "Wireframing": "https://www.interaction-design.org/courses/ux-design-process",
    "User Research": "https://www.coursera.org/learn/user-research"
}

# --- Upload Resume ---
st.subheader("📤 Upload Resume (.pdf or .txt)")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
resume_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        resume_text = uploaded_file.read().decode("utf-8").lower()
    elif uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_file:
            resume_text = " ".join([page.get_text() for page in pdf_file]).lower()

    st.subheader("📝 Resume Preview")
    st.text_area("Below is the extracted text:", value=resume_text[:3000], height=200)

# --- Category Selection ---
st.subheader("🎯 Choose Job Category")
selected_category = st.selectbox("Select a category:", list(job_categories.keys()))

# --- Analyze Resume ---
if resume_text and st.button("🔍 Analyze My Resume"):
    jobs = job_categories[selected_category]
    match_data = []
    all_missing_skills = []
    all_matched_skills = []

    full_text = resume_text

    for job, skills in jobs.items():
        matched = [skill for skill in skills if skill.lower() in full_text]
        missing = [skill for skill in skills if skill.lower() not in full_text]
        all_missing_skills.extend(missing)
        all_matched_skills.extend(matched)
        score = len(matched) / len(skills) * 100
        match_data.append({
            "Job": job,
            "Match %": round(score, 1),
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "Role Tips": role_tips.get(job, "No tips available.")
        })

    df = pd.DataFrame(match_data).sort_values(by="Match %", ascending=False)
    avg_score = df["Match %"].mean()

    st.subheader(f"📈 Resume Score: {avg_score:.1f}%")
    st.dataframe(df)

    st.subheader("💬 Career Assistant Feedback")
    top_job = df.iloc[0]
    st.markdown(f"**Best Match:** {top_job['Job']} ({top_job['Match %']}%)")
    st.info(f"✅ Tip: {top_job['Role Tips']}")

    if avg_score >= 80:
        st.success("Great match! You're well-prepared for most roles.")
    elif avg_score >= 60:
        st.warning("Decent fit. You can boost your match by improving missing skills.")
    else:
        st.error("Low match. Add more relevant skills or project work to your resume.")

    st.subheader("📚 Recommended Courses")
    for skill in list(set(all_missing_skills))[:5]:
        if skill in course_links:
            st.markdown(f"- [{skill.title()}]({course_links[skill]})")

    st.subheader("📊 Match Score Chart")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Match %", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("Job", sort="-x"),
        color=alt.value("#4C78A8")
    ).properties(width=600)
    st.altair_chart(chart)

    # --- PDF Generation ---
    class SkillMatchPDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 14)
            self.cell(0, 10, "SkillMatch Resume Analysis Report", ln=True, align="C")
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", 'I', 8)
            self.cell(0, 10, "Generated by SkillMatch", align="C")
        def add_summary(self, name, score, jobs, missing_skills, recommendations):
            self.set_font("Arial", '', 12)
            self.ln(10)
            self.cell(0, 10, f"Candidate Name: {name}", ln=True)
            self.cell(0, 10, f"Overall Resume Score: {score}%", ln=True)
            self.ln(5)
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, "Top Matching Jobs:", ln=True)
            self.set_font("Arial", '', 12)
            for job in jobs:
                self.cell(0, 10, f"- {job}", ln=True)
            self.ln(5)
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, "Top Missing Skills:", ln=True)
            self.set_font("Arial", '', 12)
            if missing_skills:
                self.multi_cell(0, 10, ", ".join(missing_skills))
            else:
                self.cell(0, 10, "None", ln=True)
            self.ln(5)
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, "Recommendations:", ln=True)
            self.set_font("Arial", '', 12)
            for tip in recommendations:
                self.multi_cell(0, 10, f"- {tip}")

    pdf = SkillMatchPDF()
    pdf.add_page()
    pdf.add_summary(
        name="Candidate",
        score=round(avg_score, 1),
        jobs=[f"{row['Job']} ({row['Match %']}%)" for _, row in df.head(3).iterrows()],
        missing_skills=list(set(all_missing_skills))[:5],
        recommendations=[f"Learn {s}" for s in list(set(all_missing_skills))[:5]]
    )
    pdf_output = pdf.output(dest='S').encode('latin-1')
    st.download_button(
        label="📄 Download PDF Summary",
        data=pdf_output,
        file_name="SkillMatch_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("Please upload a resume and select a category to start.")
