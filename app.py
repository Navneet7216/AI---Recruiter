import streamlit as st
from pypdf import PdfReader
from google import genai

# --- INITIALIZE GEMINI CLIENT WITH YOUR API KEY ---
import os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# --- EMBEDDED LIGHT NEON STYLES ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=500;800&family=Rajdhani:wght=500;700&display=swap');

    /* 1. Main App Background & Base Text */
    .stApp {
        background-color: #ffffff !important;
        background-image: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 40%, #e0f7fa 100%) !important;
        color: #1e293b !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem;
    }

    /* 2. Glow Title (Deep Purple/Blue with Electric Teal Glow) */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 800 !important;
        color: #1e1b4b !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3) !important;
        letter-spacing: 2px;
        padding-bottom: 10px;
        text-transform: uppercase;
    }

    /* 3. Input Sector Labels */
    .stTextArea label, div[data-testid="stFileUploader"] label p {
        color: #0f172a !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }

    /* 4. Textarea and File Uploader Dropzone Fields */
    div[data-baseweb="textarea"], 
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #f8fafc !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease;
    }

    /* 5. Input Interactivity (Focus & Hover) */
    div[data-baseweb="textarea"]:focus-within {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
    }

    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6366f1 !important;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.3) !important;
    }

    /* 6. File Uploader Text Visibility Fixes */
    div[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stFileUploaderDropzone"] span, 
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] button p {
        color: #475569 !important;
    }

    /* 7. Primary Action Button (Deep Purple to Electric Teal Gradient) */
    button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 2px;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
        transform: scale(1.01);
    }

    /* 8. Output Analysis Matrix (Table Elements) */
    table {
        background-color: #ffffff !important;
        border: 2px solid #06b6d4 !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.08) !important;
        border-radius: 8px !important;
    }

    th {
        background-color: rgba(6, 182, 212, 0.08) !important;
        color: #1e1b4b !important;
        font-family: 'Orbitron', sans-serif !important;
        border-bottom: 2px solid #06b6d4 !important;
    }

    td {
        color: #334155 !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }

    div[data-testid="stAlert"] {
        background-color: rgba(6, 182, 212, 0.05) !important;
        border: 1px solid #06b6d4 !important;
        color: #0891b2 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- APP UI CONTENT ---
st.title("⚡ AI RESUME RANKER")
st.markdown("<p style='color:#64748b;'>Quantum batch candidate evaluation matrix.</p>", unsafe_allow_html=True)

job_description = st.text_area("1. Target Profile (Job Description):", height=150)
uploaded_files = st.file_uploader("2. Dataset Input (Resumes):", type=["pdf"], accept_multiple_files=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("RUN EVALUATION ENGINE", type="primary"):
    if not job_description or not uploaded_files:
        st.error("Matrix inputs incomplete. Please provide both data sectors.")
    else:
        all_resumes_text = ""
        for file in uploaded_files:
            reader = PdfReader(file)
            file_text = "".join([page.extract_text() or "" for page in reader.pages])
            all_resumes_text += f"\n--- START OF RESUME: {file.name} ---\n{file_text}\n--- END OF RESUME ---\n"
        
        # Define the customized prompt structure explicitly
        prompt = f"""
        You are an expert technical interviewer and HR analyst. Evaluate the following batch of resumes against the provided Job Description.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATES' RESUMES:
        {all_resumes_text}
        
        Execute a comprehensive comparative review. Rank the candidates from best to worst based entirely on alignment accuracy.
        
        For your output, generate TWO distinct sections:
        
        ### 📊 CANDIDATE EVALUATION MATRIX
        Output a cleanly formatted Markdown table with these exact columns:
        | Rank | Candidate/File Name | Match Score (0-100) | Top Strengths | Missing Gaps | 1-Sentence Verdict |
        
        ### 🎯 TAILORED CANDIDATE INTERVIEW QUESTIONS
        Directly below the table, create a numbered breakdown for EACH candidate (ordered by their rank). For each individual, provide:
        * **Candidate Name**
        * **3 Hyper-Targeted Interview Questions**: Crafted specifically to pressure-test their identified "Missing Gaps" or deep-dive into their claimed "Top Strengths".
        """
        
        with st.spinner("Analyzing data streams..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.success("ANALYSIS COMPLETE")
            st.markdown(response.text)
