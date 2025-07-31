import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a highly intelligent and professional Physics Tutor with expertise in competitive exams such as IIT-JAM, CSIR-NET, and GATE Physics. 

Your responsibilities:
- Provide conceptually sound, accurate, and syllabus-aligned explanations.
- Use step-by-step problem-solving, relevant equations, and mathematical derivations.
- Explain the underlying physics intuitively, building from first principles.
- Include real-world examples or analogies wherever helpful.
- Use LaTeX-style math formatting for clarity in equations.
- When appropriate, include graphs, diagrams, or brief derivations to aid understanding.
- Clearly state assumptions, boundary conditions, and approximations used in derivations or numerical solutions.
- Keep your answers focused on the question. Avoid philosophical, vague, or unrelated explanations.
- When multiple methods exist, briefly mention alternative approaches.

Respond in a teaching tone, suitable for students aiming for high scores in national-level physics exams.

Always assume the student has a basic undergraduate-level understanding of physics and mathematics, but may need guidance in advanced applications and exam tricks.

If a question is ambiguous, clearly state assumptions before answering.
"""

# --- Streamlit Config ---
st.set_page_config(page_title="🧠 Physics Tutor – JAM/NET/GATE", page_icon="🔬", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f6fa;
        }
        .main-title {
            text-align: center;
            font-size: 2.2rem;
            color: #333333;
            margin-bottom: 1rem;
        }
        .question-box input {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        .submit-button {
            width: 100%;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem;
            font-size: 1rem;
            font-weight: 600;
            margin-top: 1rem;
        }
        .answer-box {
            background-color: white;
            border: 1px solid #dddddd;
            border-radius: 12px;
            padding: 1.2rem;
            font-size: 1.05rem;
            color: #111;
            line-height: 1.6;
            margin-top: 1.5rem;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="main-title">🧠 Physics Tutor by Sreekesh M</div>', unsafe_allow_html=True)

# --- Text Extraction Utilities ---
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n")
    except Exception as e:
        return f"Error reading URL: {e}"

# --- Form Input ---
with st.form(key="physics_form"):
    query = st.text_input("📌 Enter your Physics question below:", placeholder="e.g., Derive the Schrödinger equation.", key="question")
    uploaded_file = st.file_uploader("📄 Optionally upload a file (PDF or DOCX):", type=["pdf", "docx"])
    url_input = st.text_input("🌐 Optionally paste a webpage URL (e.g., NPTEL, Wikipedia):")
    submit_button = st.form_submit_button("🚀 Get Answer")

# --- Answer Generation ---
if submit_button and query:
    with st.spinner("🧠 Thinking..."):
        # Optional context from file or URL
        context = ""
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                context = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                context = extract_text_from_docx(uploaded_file)
        elif url_input:
            context = extract_text_from_url(url_input)

        # Limit context size (avoid LLM overload)
        context = context.strip()
        if len(context) > 3000:
            context = context[:3000] + "\n...[Content trimmed]"

        # Create final prompt for LLM
        if context:
            full_prompt = f"""You may use the following reference content if helpful:\n\n{context}\n\nQuestion: {query}"""
        else:
            full_prompt = query

        # Run LLM chain
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"question": full_prompt})

        # Show Answer
        st.markdown('<div class="answer-box">{}</div>'.format(response), unsafe_allow_html=True)
