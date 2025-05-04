# 📌 Job Posting Recommendations
st.subheader("📌 Job Posting Recommendations")

# Load cleaned job postings dataset
try:
    postings_df = pd.read_csv("postings_5000_clean.csv")
    postings_df.columns = postings_df.columns.str.strip().str.title()  # Normalize column names

    # Extract top matched job
    top_role = df.iloc[0]['Job']  # The job role with highest match %

    # Filter matching job titles in the postings
    matching_postings = postings_df[
        postings_df['Job Title'].str.contains(top_role, case=False, na=False)
    ]

    if not matching_postings.empty:
        st.markdown(f"**Top Job Postings for `{top_role}`:**")
        for _, row in matching_postings.head(5).iterrows():
            job_title = row.get('Job Title', 'N/A')
            company = row.get('Company', 'N/A')
            location = row.get('Location', 'N/A')
            url = row.get('URL', '#')
            st.markdown(f"🔹 [{job_title} at {company} – {location}]({url})")
    else:
        st.info(f"No job postings found for **{top_role}**.")

except Exception as e:
    st.error(f"Error loading job postings: {e}")
