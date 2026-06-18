import streamlit as st
from pypdf import PdfReader
from google import genai

# Initialize the Gemini Client
client = genai.Client()

st.title("🤖 Simple AI Resume Ranker")

# 1. Inputs
job_description = st.text_area("1. Paste Job Description:", height=150)
uploaded_files = st.file_uploader("2. Upload Resumes (PDFs):", type=["pdf"], accept_multiple_files=True)

# 2. Process & Rank
if st.button("🚀 Rank Resumes", type="primary"):
    if not job_description or not uploaded_files:
        st.error("Please provide both a Job Description and Resumes!")
    else:
        all_resumes_text = ""
        
        # Extract text from all uploaded PDFs
        for file in uploaded_files:
            reader = PdfReader(file)
            file_text = "".join([page.extract_text() or "" for page in reader.pages])
            all_resumes_text += f"\n--- START OF RESUME: {file.name} ---\n{file_text}\n--- END OF RESUME ---\n"
        
        # Send everything to Gemini
        prompt = f"""
        You are an expert HR assistant. Compare the following batch of resumes against the Job Description.
        Rank the candidates from best to worst based on fit.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATES' RESUMES:
        {all_resumes_text}
        
        Output your response ONLY as a cleanly formatted Markdown table with these exact columns:
        | Rank | Candidate/File Name | Match Score (0-100) | Top Strengths | Missing Gaps | 1-Sentence Verdict |
        """
        
        with st.spinner("AI is evaluating and ranking..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # 3. Output the result directly as a beautiful Markdown table
            st.success("Ranking Complete!")
            st.markdown(response.text)