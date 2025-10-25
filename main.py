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


# -------- Comprehensive Theory System Prompt --------
SYSTEM_PROMPT = """
You are an expert Physics Professor preparing comprehensive theory notes for IIT-JAM, CSIR-NET, and GATE Physics students.

**Your Mission:** Provide EXTENSIVE, DETAILED conceptual explanations covering every aspect of the topic.

**Content Requirements:**
- Write 800-1200 words of pure theory (no equations, formulas, or mathematical symbols)
- Cover ALL fundamental concepts, principles, and physical insights
- Explain the historical context and motivation behind the concept
- Describe ALL assumptions, conditions, and limitations in detail
- Discuss symmetries, boundary conditions, and special cases thoroughly
- Provide multiple real-world analogies and physical interpretations
- Include comprehensive exam strategy, common mistakes, and problem-solving approaches
- Add conceptual tricks, shortcuts, and pattern recognition tips
- Discuss how the concept connects to other physics topics

**Structure (use these headings):**
### Introduction
- One-sentence definition
- Historical background and motivation
- Why this concept is fundamental

### Core Physical Principles
- Detailed explanation of the underlying physics
- Multiple perspectives and interpretations
- Physical intuition and analogies

### Assumptions and Applicability
- When and where the concept applies
- Limitations and breakdown conditions
- Special cases and generalizations

### Symmetries and Key Features
- Symmetry considerations in detail
- Conservation laws involved
- Characteristic behaviors

### Boundary Conditions and Constraints
- Detailed discussion of boundary conditions
- Why they matter physically
- How they affect solutions

### Physical Interpretation
- What the concept means in reality
- How to visualize it
- Connection to observable phenomena

### Problem-Solving Strategy
- Systematic approach for exam problems
- Step-by-step conceptual framework
- Pattern recognition tips

### Common Mistakes and Pitfalls
- Typical student errors
- Conceptual misconceptions
- How to avoid them

### Exam Tips and Tricks
- Quick checks and sanity tests
- Time-saving approaches
- What examiners look for

### Connections to Other Topics
- How this relates to other physics areas
- Unified understanding

**Writing Rules:**
- NO mathematical equations, symbols, Greek letters, operators, or numerical expressions
- Use descriptive language instead: "the ratio of charge to permittivity" NOT "q/ε₀"
- Write in clear, flowing paragraphs (3-5 sentences each)
- Use bullet points only for lists
- Bold key physics terms once per section
- Keep tone engaging, clear, and student-friendly
- Focus on UNDERSTANDING, not memorization

**Strictly Forbidden:**
- Mathematical notation of any kind
- Equations, integrals, derivatives, summations
- Greek letters, subscripts, superscripts
- Numerical calculations or examples with operators

Write as if you're giving a detailed lecture to help students master the concept completely.
"""


# -------- Math Stripper (Safety Backup) --------
def strip_math(text: str) -> str:
    """Remove any residual mathematical notation"""
    s = text.replace("\r\n", "\n")
    
    # Remove LaTeX blocks
    s = re.sub(r"\$\$[\s\S]*?\$\$", "", s)
    s = re.sub(r"\\\[[\s\S]*?\\\]", "", s)
    s = re.sub(r"\$[^\$]*?\$", "", s)
    s = re.sub(r"\\\([^\)]*?\\\)", "", s)
    s = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})*", "", s)
    
    # Remove math symbols
    s = re.sub(r"[∇∂±≈≃≅≡≤≥×·∙⋅∞ΣΠ∫∮→←↔^_{}]", "", s)
    s = re.sub(r"\s[=+\-/*^><]+\s", " ", s)
    
    # Clean spacing
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


# -------- Streamlit Configuration --------
st.set_page_config(
    page_title="🧠 Physics Theory Tutor",
    page_icon="🧠",
    layout="wide",
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
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 1.5rem 0;
            letter-spacing: 1px;
        }
        
        .subtitle {
            text-align: center;
            color: #a0aec0;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .stForm {
            background: rgba(26, 31, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            max-width: 900px;
            margin: 0 auto 2rem auto;
        }
        
        .stTextInput > label {
            color: #a0aec0 !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #1a1f2e !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 12px !important;
            padding: 0.9rem 1.2rem !important;
            color: #e2e8f0 !important;
            font-size: 1rem !important;
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
            padding: 0.9rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin-top: 1.2rem !important;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
        }
        
        .answer-container {
            max-width: 1100px;
            margin: 0 auto;
        }
        
        div[data-testid="stMarkdownContainer"] {
            background: rgba(26, 31, 46, 0.85) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            color: #e2e8f0 !important;
            line-height: 1.8 !important;
            margin-top: 1rem !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        }
        
        div[data-testid="stMarkdownContainer"] h3 {
            color: #667eea !important;
            font-size: 1.4rem !important;
            margin-top: 1.8rem !important;
            margin-bottom: 0.8rem !important;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
            padding-bottom: 0.4rem;
        }
        
        div[data-testid="stMarkdownContainer"] h3:first-child {
            margin-top: 0 !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 1rem;
            color: #d1d5db;
        }
        
        div[data-testid="stMarkdownContainer"] strong {
            color: #a78bfa !important;
            font-weight: 600 !important;
        }
        
        div[data-testid="stMarkdownContainer"] ul {
            margin: 0.8rem 0 1.2rem 1.5rem;
        }
        
        div[data-testid="stMarkdownContainer"] li {
            margin-bottom: 0.5rem;
            color: #d1d5db;
        }
        
        .stSpinner > div {
            border-top-color: #667eea !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Physics Theory Tutor by Sreekesh M</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Comprehensive Theory for IIT-JAM, CSIR-NET & GATE Physics</div>', unsafe_allow_html=True)


# -------- Input Form --------
with st.form(key="physics_form"):
    query = st.text_input(
        "📚 Enter any Physics topic for detailed theory:",
        placeholder="e.g., Schrödinger equation, Gauss's law, Maxwell's equations, etc.",
        key="question"
    )
    submit_button = st.form_submit_button("📖 Generate Comprehensive Theory")


# -------- Generate Comprehensive Answer --------
if submit_button and query:
    with st.spinner("🧠 Preparing comprehensive theory notes..."):
        try:
            llm = get_llm()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{question}")
            ])
            
            chain = prompt | llm | StrOutputParser()
            response = chain.invoke({"question": query})
            
            # Clean any residual math
            clean_response = strip_math(response)
            
            # Display in centered container
            st.markdown('<div class="answer-container">', unsafe_allow_html=True)
            st.markdown(clean_response)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Please check your API key in groq_config.py and ensure you have internet connectivity.")
