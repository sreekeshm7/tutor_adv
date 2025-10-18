import streamlit as st
import requests
from PyPDF2 import PdfReader
import docx
from groq_config import get_llm  # Uses your Groq/Llama3 config
import re

# ---------------------------------------------------
# SYSTEM PROMPT (Enhanced for Competitive Physics)
# ---------------------------------------------------
SYSTEM_PROMPT = """
You are Physics GPT, a friendly and expert AI physics tutor.
You must always produce long, comprehensive answers in the following structure,
suitable for NEET, JEE, JAM, NET, GATE, TIFR and other competitive exams:

1. **Definition / Principle** – clear and conceptually rich explanation.
2. **Mathematical Statement** – formal equation(s) with meaning of each term.
3. **Detailed Derivation** – step-by-step derivation with no skipped steps, starting from first principles.
4. **Key Equation** – highlight the main result/formula.
5. **Example Problem & Solution** – challenging, exam-level example(s), fully worked out.
6. **Real-World Applications** – practical uses in science, engineering, and research.
7. **Closing Note** – summarising comment, tips, or additional insights for students.

CRITICAL MATH FORMATTING RULES:
- Use ONLY standard LaTeX notation
- For inline math: $mathematical_expression$
- For display equations: $$mathematical_expression$$  
- Use proper LaTeX commands: \\mathbf{E}, \\nabla, \\varepsilon, \\rho, \\int, \\oint, \\cdot, \\times, etc.
- For fractions: \\frac{numerator}{denominator}
- For subscripts: E_{field}, for superscripts: R^{2}
- For vectors: \\mathbf{E}, \\mathbf{r}, \\hat{r}
- Always use proper spacing in equations

Example correct format:
The electric field is $\\mathbf{E} = \\frac{1}{4\\pi\\varepsilon_0} \\frac{q}{r^2} \\hat{r}$.

The integral form of Gauss's law is:
$$\\oint_S \\mathbf{E} \\cdot d\\mathbf{A} = \\frac{Q_{enc}}{\\varepsilon_0}$$

Guidelines:
- Be very thorough for derivations: include ALL steps, no jumps.
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

def clean_latex_expressions(text):
    """Clean and properly format LaTeX expressions for Streamlit"""
    
    # Remove problematic characters and fix common issues
    text = text.replace('!', '')  # Remove exclamation marks in math
    text = text.replace(',', ' ')  # Clean up comma spacing in math
    text = text.replace(';;', ' ')  # Remove double semicolons
    
    # Fix display math brackets
    text = re.sub(r'\[\s*\\begin\{aligned\}', r'$$\\begin{aligned}', text)
    text = re.sub(r'\\end\{aligned\}\s*\\tag\{[^}]*\}\s*\]', r'\\end{aligned}$$', text)
    text = re.sub(r'\[\s*([^]]+?)\s*\\tag\{[^}]*\}\s*\]', r'$$\1$$', text)
    text = re.sub(r'\[\s*([^]]+?)\s*\]', r'$$\1$$', text)
    
    # Fix inline math
    text = re.sub(r'\(([^)]*?\\[a-zA-Z]+[^)]*?)\)', r'$\1$', text)
    
    # Clean up boxed equations
    text = re.sub(r'\\boxed\{\\displaystyle\s*([^}]+)\}', r'\\boxed{\1}', text)
    
    # Fix common LaTeX commands
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'\\mathbf{\1}', text)
    text = re.sub(r'\\varepsilon_\{0\}', r'\\varepsilon_0', text)
    text = re.sub(r'\\varepsilon_\{([^}]+)\}', r'\\varepsilon_{\1}', text)
    
    # Fix spacing issues
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*\$\s*', '$', text)
    
    return text

def render_physics_content(text):
    """Render physics content with proper LaTeX formatting"""
    
    # Clean the LaTeX first
    cleaned_text = clean_latex_expressions(text)
    
    # Split into sections and render
    sections = cleaned_text.split('\n\n')
    
    for section in sections:
        if section.strip():
            # Check if this section contains display math
            if '$$' in section:
                parts = section.split('$$')
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Text part
                        if part.strip():
                            st.markdown(part.strip())
                    else:  # Math part
                        if part.strip():
                            st.latex(part.strip())
            else:
                # Regular markdown content
                st.markdown(section.strip())

# ---------------------------------------------------
# Streamlit Config
# ---------------------------------------------------
st.set_page_config(page_title="⚡ Physics GPT", layout="wide")

# Custom Styling
st.markdown("""
<style>
.stMarkdown {
    font-family: 'Times New Roman', serif;
    font-size: 1.05rem;
    line-height: 1.8;
}
.stLatex {
    font-size: 1.1rem !important;
    margin: 1rem 0;
}
div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 1rem;
}
h1, h2, h3, h4 {
    color: #1f4e79;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}
@media (max-width:768px) {
    .stMarkdown { font-size: 1rem; }
    .stLatex { font-size: 1rem !important; }
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
        placeholder="E.g., Derive Schrödinger equation; Solve NEET/JEE projectile problem; Explain Gauss's law"
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

                # Render the physics content with proper LaTeX
                st.markdown("---")
                render_physics_content(answer_text)
                st.markdown("---")

                st.markdown("<p style='text-align:center; margin-top: 2rem'>⚡ Physics GPT by <b>Sreekesh M</b></p>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Groq API Error: {e}")
