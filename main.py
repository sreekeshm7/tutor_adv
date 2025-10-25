# Compatibility fix
import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False

import re
import streamlit as st
from groq_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# -------- Improved Theory-Only System Prompt --------
SYSTEM_PROMPT = """
You are an expert Physics Tutor for IIT-JAM, CSIR-NET, and GATE Physics exams.

**Output Format Rules:**
- Provide ONLY conceptual explanations in simple, clear language
- NO equations, formulas, mathematical symbols, or derivations
- Use short paragraphs (2-3 sentences max)
- Use bullet points for lists
- Use numbered steps for procedures
- Add section headings with ### for main topics
- Add **bold** for key physics terms (once per paragraph)

**Content Rules:**
- Start with a one-sentence definition
- Explain the physical meaning and intuition
- Mention key assumptions and when it applies
- Highlight symmetries and boundary conditions in words
- Give exam tips and common mistakes
- Keep it concise - aim for 300-500 words total

**Strictly Forbidden:**
- Do NOT write any equations, integrals, derivatives, or mathematical expressions
- Do NOT use Greek letters, subscripts, superscripts, or mathematical operators
- Do NOT show calculations or numerical examples
- If asked for a formula, describe what it represents conceptually instead

**Tone:** Clear, structured, exam-focused, and student-friendly. Write as if explaining to a friend before an exam.
"""


# -------- Math stripper (backup safety) --------
def strip_math(text: str) -> str:
    """Remove any residual math notation"""
    s = text.replace("\r\n", "\n")
    
    # Remove LaTeX patterns
    s = re.sub(r"\$\$[\s\S]*?\$\$", "", s)
    s = re.sub(r"\\\[[\s\S]*?\\\]", "", s)
    s = re.sub(r"\$[^\$]*?\$", "", s)
    s = re.sub(r"\\\([^\)]*?\\\)", "", s)
    s = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})*", "", s)
    
    # Remove common math symbols
    s = re.sub(r"[∇∂±≈≃≅≡≤≥×·∙⋅∞ΣΠ∫∮→←↔^_{}]", "", s)
    s = re.sub(r"\s[=+\-/*^><]+\s", " ", s)
    
    # Clean up extra spaces
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# -------- UI Configuration --------
st.set_page_config(
    page_title="🧠 Physics Tutor – Concepts Only",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        #MainMenu, footer, header { visibility: hidden; }
        
        .main-title {
            text-align: center;
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 1rem 0 1.5rem 0;
        }
        
        .stForm {
            background: rgba(26, 31, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 16px;
            padding: 1.8rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .stTextInput > label {
            color: #a0aec0 !important;
            font-weight: 500 !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #1a1f2e !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 12px !important;
            padding: 0.85rem 1rem !important;
            color: #e2e8f0 !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        }
        
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.85rem !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
        }
        
        div[data-testid="stMarkdownContainer"] {
            background: rgba(26, 31, 46, 0.8) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 16px !important;
            padding: 1.3rem !important;
            color: #e2e8f0 !important;
            line-height: 1.7 !important;
            margin-top: 0.8rem !important;
        }
        
        div[data-testid="stMarkdownContainer"] h3 {
            color: #667eea !important;
            font-size: 1.3rem !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.6rem !important;
            border-bottom: 1px solid rgba(102, 126, 234, 0.3);
            padding-bottom: 0.3rem;
        }
        
        div[data-testid="stMarkdownContainer"] strong {
            color: #a78bfa !important;
        }
        
        div[data-testid="stMarkdownContainer"] ul {
            margin-left: 1rem;
        }
        
        div[data-testid="stMarkdownContainer"] li {
            margin-bottom: 0.4rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Physics Tutor by Sreekesh M</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------- Input Form --------
with st.form(key="physics_form"):
    query = st.text_input(
        "📌 Ask any Physics concept (theory only):",
        placeholder="e.g., Explain the Schrödinger equation conceptually",
        key="question"
    )
    submit_button = st.form_submit_button("🚀 Get Answer")


# -------- Generate Answer --------
if submit_button and query:
    with st.spinner("🧠 Thinking..."):
        try:
            llm = get_llm()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{question}")
            ])
            
            chain = prompt | llm | StrOutputParser()
            response = chain.invoke({"question": query})
            
            # Clean any math that slipped through
            clean_response = strip_math(response)
            
            # Display
            st.markdown("### 📖 Answer")
            st.markdown(clean_response)
            
            # Save to history
            st.session_state.messages.append({
                "question": query,
                "answer": clean_response
            })
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check your API key in groq_config.py")


# -------- Chat History --------
if st.session_state.messages:
    with st.expander("📚 Previous Questions", expanded=False):
        for i, msg in enumerate(reversed(st.session_state.messages[:-1] if len(st.session_state.messages) > 1 else []), 1):
            st.markdown(f"**Q{i}:** {msg['question']}")
            preview = msg['answer'][:250] + "..." if len(msg['answer']) > 250 else msg['answer']
            st.markdown(preview)
            if i < len(st.session_state.messages) - 1:
                st.divider()
