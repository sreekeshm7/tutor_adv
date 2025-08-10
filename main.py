# main.py
import streamlit as st
import requests
from PyPDF2 import PdfReader
import docx
from groq_config import get_llm   # Uses your code for Groq/LLama3-8B

# ----- System prompt -----
SYSTEM_PROMPT = """
You are Physics GPT, a friendly and expert AI physics tutor.
You explain any physics topic: theory, problems, derivations, with LaTeX for equations. 
Include: definitions, principles, key equations, brief history, simple and detailed examples (solutions/derivations), and real-world applications if asked.
Adapt your depth to the user's question/context.
"""

# ----- File & URL helpers -----
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def fetch_url_content(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
        return ""
    except Exception:
        return ""

def build_prompt(context, question):
    return f"""{SYSTEM_PROMPT}

{f"REFERENCE MATERIAL:\n{context}\n" if context else ""}
USER QUESTION: {question}
"""

# ----- UI -----
st.set_page_config(page_title="Physics GPT", layout="centered")

st.markdown("""
<style>
.response-content {
    padding: 1.25rem;
    font-size: 1.05rem;
    line-height: 1.6;
}
.response-content h1 { font-size: 1.4rem; }
.response-content h2 { font-size: 1.15rem; }
.response-content h3 { font-size: 1.08rem; }
.response-content h4 { font-size: 1rem; }
@media (max-width:768px) {
    .main-container { padding: 0.7rem; margin: 0.4rem; }
    .response-content { font-size: 1.0rem; }
    .main-title { font-size: 1.15rem; }
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Physics GPT (Groq/LLama3)")
st.write("Ask any physics theory, problem, or derivation. Optionally upload a PDF/DOCX or provide a link for context.")

all_physics_topics = [
    "Classical Mechanics", "Electromagnetism", "Thermodynamics",
    "Quantum Mechanics", "Relativity", "Optics", "Particle Physics",
    "Astrophysics", "Fluid Mechanics", "Nuclear Physics"
]

with st.form(key="physics_gpt_form"):
    topic = st.selectbox("Choose a topic (optional):", ["(None)"] + all_physics_topics)
    query = st.text_area(
        "Ask a physics question:",
        placeholder="E.g., Derive Schrödinger equation; Explain Faraday's law; Show a solved projectile problem"
    )
    uploaded_file = st.file_uploader(
        "Attach reference (PDF/DOCX, optional):",
        type=["pdf", "docx"]
    )
    url_input = st.text_input("Paste a link to physics content (optional):")
    submit_button = st.form_submit_button("Get Physics Answer")

# ----- Processing -----
if submit_button:
    context_text = ""

    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                context_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                "application/msword"
            ]:
                context_text = extract_text_from_docx(uploaded_file)
        except Exception as e:
            st.warning(f"Error reading file: {e}")

    if url_input:
        url_text = fetch_url_content(url_input)
        if url_text:
            context_text += "\n" + url_text

    user_input = query or (topic if topic != "(None)" else "")

    if not user_input.strip():
        st.warning("Please enter a question or select a topic.")
    else:
        final_prompt = build_prompt(context_text.strip(), user_input.strip())

        with st.spinner("Thinking..."):
            try:
                llm = get_llm()
                answer = llm.invoke(final_prompt)  # LangChain call
                st.markdown(f'<div class="response-content">{answer}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error from Groq API: {e}")
