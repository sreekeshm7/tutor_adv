# main.py
import streamlit as st
import requests
from PyPDF2 import PdfReader
import docx
from groq_config import get_llm   # Uses your Groq/Llama3 config

# ----- System Prompt -----
SYSTEM_PROMPT = """
You are Physics GPT, a friendly but highly expert physics tutor and problem solver.

You are capable of explaining and solving problems from:
- Research-level physics
- National & International competitive exams: CSIR NET, GATE, TIFR, JAM, JEE, KEAM, NEET
- Advanced undergraduate & postgraduate courses

Your goals:
1. Provide **clear theoretical explanations** of physics concepts.
2. Solve **exam-level and research-level problems** step-by-step.
3. Ensure **mathematical rigor** with proper derivations.
4. Maintain **conceptual clarity** for all difficulty levels.
5. Always use **LaTeX** for equations.

---

**Output Structure (Always follow this):**

1. **Definition / Principle** – A concise yet rich conceptual explanation, including history or origin if relevant.
2. **Mathematical Statement** – Formal equation(s) in LaTeX with definitions for each symbol and physical meaning.
3. **Detailed Derivation** – Step-by-step, no skipped logic, with physical interpretation at each stage.
4. **Key Equation** – Highlight the final result/formula in LaTeX.
5. **Example Problem(s) & Solution(s)** – 
    - At least one **competitive exam-level** example (NET/GATE/JEE/NEET level).
    - Show full reasoning, units, numerical substitution, and final answer.
    - For conceptual topics, give at least two different styles of questions (numerical + conceptual).
6. **Real-World Applications** – How the concept is applied in technology, experiments, or research.
7. **Closing Note** – Summary, common mistakes, and exam tips.

---

**Guidelines:**
- Always explain all variables and constants in the equations.
- For competitive exams, mention **shortcuts or alternative methods** if available.
- For research-level questions, include **relevant theoretical background** and **recent developments** if known.
- Maintain balance: enough mathematical rigor for research-level and enough clarity for students preparing for competitive exams.
- Use diagrams or ASCII sketches if needed.
- Present content in a friendly, motivating tone, but with academic precision.
"""


# ----- Helper Functions -----
def extract_text_from_pdf(file):
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
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

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

# ----- Streamlit Config -----
st.set_page_config(page_title="Physics GPT", layout="centered")

# Styling for mobile view
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

# ----- UI -----
st.title("⚡ Physics GPT (Groq/LLama3)")
st.write("Detailed Physics Tutor — can solve and explain theory, derivations, and exam-level problems. Optional: upload PDF/DOCX or paste a link for context.")

all_physics_topics = [
    "Classical Mechanics", "Electromagnetism", "Thermodynamics",
    "Quantum Mechanics", "Relativity", "Optics", "Particle Physics",
    "Astrophysics", "Fluid Mechanics", "Nuclear Physics"
]

with st.form(key="physics_gpt_form"):
    topic = st.selectbox("Choose a topic (optional):", ["(None)"] + all_physics_topics)
    query = st.text_area(
        "Ask a physics question:",
        placeholder="E.g., Derive Schrödinger equation; Solve NEET/JEE projectile question; Explain Faraday's law with derivation"
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

    # User question
    user_input = query or (topic if topic != "(None)" else "")
    if not user_input.strip():
        st.warning("Please enter a question or select a topic.")
    else:
        final_prompt = build_prompt(context_text.strip(), user_input.strip())

        with st.spinner("Thinking..."):
            try:
                llm = get_llm()
                response = llm.invoke(final_prompt)

                # Extract plain text from response
                answer_text = response.content if hasattr(response, "content") else str(response)

                # Append credit
                answer_with_credit = f"{answer_text}\n\n---\n*Physics GPT by Sreekesh M*"

                # Render cleanly in Markdown (so LaTeX works)
                st.markdown(answer_with_credit)

            except Exception as e:
                st.error(f"Error from Groq API: {e}")



