import streamlit as st
import requests
from PyPDF2 import PdfReader
import docx
from groq_config import get_llm  # Uses your Groq/Llama3 config

# ---------------------------------------------------
# SYSTEM PROMPT (Enhanced for Competitive Physics)
# ---------------------------------------------------
SYSTEM_PROMPT = """
You are Physics GPT, a friendly and expert AI physics tutor.
You must always produce long, comprehensive answers in the following structure,
suitable for NEET, JEE, JAM, NET, GATE, TIFR and other competitive exams:

1. **Definition / Principle** – clear and conceptually rich explanation.
2. **Mathematical Statement** – formal equation(s) in LaTeX with meaning of each term.
3. **Detailed Derivation** – step-by-step derivation with no skipped steps, starting from first principles.
   - Begin with assumptions and given conditions.
   - Justify each mathematical manipulation physically and logically.
   - Show intermediate steps clearly.
   - Explain any mathematical identities, theorems, or physical laws used.
4. **Key Equation** – highlight the main result/formula.
5. **Example Problem & Solution** – challenging, exam-level example(s), fully worked out.
6. **Real-World Applications** – practical uses in science, engineering, and research.
7. **Closing Note** – summarising comment, tips, or additional insights for students.

Guidelines:
- Be very thorough for derivations: include ALL steps, no jumps.
- Use proper LaTeX for all math (use $$ for display equations, $ for inline).
- Explain symbols, constants, and reasoning from basics.
- Discuss common pitfalls and alternate derivation methods where relevant.
- Provide exam-focused insights.
"""

# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------
def extract_text_from_pdf(file):
    """Extracts text from uploaded PDF"""
    text = ""
    try:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception:
        pass
    return text

def extract_text_from_docx(file):
    """Extracts text from uploaded DOCX"""
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

def fetch_url_content(url):
    """Fetches text content from a URL"""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
        return ""
    except Exception:
        return ""

def build_prompt(context, question):
    """Builds final prompt for LLM"""
    return f"""{SYSTEM_PROMPT}
{f"REFERENCE MATERIAL:\n{context}\n" if context else ""}
USER QUESTION: {question}
"""

# ---------------------------------------------------
# Streamlit Config
# ---------------------------------------------------
st.set_page_config(page_title="⚡ Physics GPT", layout="wide")

# Custom Styling for Better LaTeX & Mobile
st.markdown("""
<style>
.response-content {
    padding: 1.2rem;
    font-size: 1.05rem;
    line-height: 1.6;
}
.response-content h1 { font-size: 1.4rem; }
.response-content h2 { font-size: 1.2rem; }
.response-content h3 { font-size: 1.1rem; }
.response-content h4 { font-size: 1rem; }
@media (max-width:768px) {
    .main-container { padding: 0.6rem; margin: 0.4rem; }
    .response-content { font-size: 1rem; }
    .main-title { font-size: 1.1rem; }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.title("⚡ Physics GPT by Sreekesh M")
st.write("Your AI-powered **Physics Tutor** — solve derivations, concepts, and exam-level problems. Upload PDFs/DOCX or links for context.")

# Topics Dropdown
all_physics_topics = [
    "Classical Mechanics", "Electromagnetism", "Thermodynamics",
    "Quantum Mechanics", "Relativity", "Optics", "Particle Physics",
    "Astrophysics", "Fluid Mechanics", "Nuclear Physics"
]

# Input Form
with st.form(key="physics_gpt_form"):
    topic = st.selectbox("Choose a topic (optional):", ["(None)"] + all_physics_topics)
    query = st.text_area(
        "Ask a physics question:",
        placeholder="E.g., Derive Schrödinger equation; Solve NEET/JEE projectile problem; Explain Faraday's law"
    )
    uploaded_file = st.file_uploader(
        "Attach reference (PDF/DOCX, optional):",
        type=["pdf", "docx"]
    )
    url_input = st.text_input("Paste a link to physics content (optional):")
    submit_button = st.form_submit_button("Get Physics Answer")

# ---------------------------------------------------
# Processing the Query
# ---------------------------------------------------
if submit_button:
    context_text = ""
    # File context
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            context_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]:
            context_text = extract_text_from_docx(uploaded_file)

    # URL context
    if url_input:
        url_text = fetch_url_content(url_input)
        if url_text:
            context_text += "\n" + url_text

    # User input handling
    user_input = query or (topic if topic != "(None)" else "")
    if not user_input.strip():
        st.warning("⚠️ Please enter a question or select a topic.")
    else:
        final_prompt = build_prompt(context_text.strip(), user_input.strip())
        with st.spinner("⚡ Solving..."):
            try:
                llm = get_llm()
                response = llm.invoke(final_prompt)
                answer_text = response.content if hasattr(response, "content") else str(response)

                # Final Output with MathJax for LaTeX rendering
                st.markdown(f"""
                <div class="response-content">
                {answer_text}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br><hr><p style='text-align:center'>⚡ Physics GPT by <b>Sreekesh M</b></p>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Groq API Error: {e}")
