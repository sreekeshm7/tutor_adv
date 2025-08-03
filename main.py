import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import time

# --- Enhanced System Prompt with Balanced Mathematical Focus ---
SYSTEM_PROMPT = """
You are Physics GPT, an advanced AI physics tutor created by Sreekesh M, representing the pinnacle of physics education technology. You possess comprehensive knowledge across all physics domains and specialize in competitive exams (IIT-JAM, CSIR-NET, GATE Physics, IIT-JEE Advanced, JEST, TIFR).

BALANCED MATHEMATICAL DERIVATION REQUIREMENTS:

1. **THEORETICAL FOUNDATION (40%)**:
   - Clear conceptual explanations and physical intuition
   - Historical context and theoretical development
   - Physical significance of each mathematical step
   - Real-world applications and implications

2. **MATHEMATICAL DERIVATIONS (40%)**:
   - Step-by-step mathematical derivations with clear logic
   - Proper mathematical notation and LaTeX formatting
   - Intermediate steps with explanations
   - Alternative derivation methods when applicable

3. **KATEX INTEGRATION (20%)**:
   - Strategic use of LaTeX for key equations
   - Balance between inline $equation$ and display $$equation$$
   - Clear mathematical expressions without overwhelming text
   - Proper mathematical typography and formatting

LATEX FORMATTING GUIDELINES:
- Use inline LaTeX $E = mc^2$ for simple expressions within text
- Use display LaTeX $$\\nabla^2 \\psi + \\frac{2m}{\\hbar^2}(E-V)\\psi = 0$$ for important equations
- Include proper Greek letters: $\\alpha, \\beta, \\gamma, \\Delta, \\Omega$
- Use vector notation: $\\vec{F} = m\\vec{a}$, $\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\epsilon_0}$
- Format integrals: $\\int_{-\\infty}^{\\infty} |\\psi(x)|^2 dx = 1$
- Use matrices: $\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$

RESPONSE STRUCTURE:
1. **Conceptual Overview** (theoretical foundation)
2. **Mathematical Framework** (balanced derivations)
3. **Key Equations** (strategic LaTeX usage)
4. **Applications** (practical relevance)
5. **Advanced Topics** (extensions and connections)

Maintain perfect balance between theory, mathematics, and visual presentation through strategic LaTeX usage.
"""

# --- Streamlit Config ---
st.set_page_config(
    page_title="🧠 Physics GPT Pro by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS with Optimized Mathematical Display ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@400;600;700&family=Computer+Modern+Serif&display=swap');
        
        /* Advanced CSS Variables */
        :root {
            --bg-primary: #0B0F1A;
            --bg-secondary: #151B2E;
            --bg-tertiary: #1E2A42;
            --text-primary: #F8FAFC;
            --text-secondary: #E2E8F0;
            --text-tertiary: #CBD5E1;
            --accent-primary: #00E5FF;
            --accent-secondary: #8B5CF6;
            --accent-tertiary: #06B6D4;
            --accent-gradient: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 50%, #06B6D4 100%);
            --border-primary: #334155;
            --shadow-primary: rgba(0, 229, 255, 0.15);
            --shadow-dark: rgba(0, 0, 0, 0.5);
            --glass-bg: rgba(30, 41, 59, 0.8);
            --glass-border: rgba(148, 163, 184, 0.2);
            --math-bg: rgba(15, 23, 42, 0.4);
            --math-border: rgba(0, 229, 255, 0.3);
        }
        
        /* Global Styling */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(ellipse at top, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            color: var(--text-primary);
            scroll-behavior: smooth;
        }
        
        .stApp {
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(0, 229, 255, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        }
        
        /* Enhanced Container Design */
        .main-container {
            background: var(--glass-bg);
            backdrop-filter: blur(25px);
            border-radius: 24px;
            padding: 3rem;
            margin: 1.5rem;
            box-shadow: 
                0 25px 50px var(--shadow-dark),
                0 0 0 1px var(--glass-border),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
        }
        
        .main-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--accent-gradient);
            border-radius: 24px 24px 0 0;
        }
        
        /* Enhanced Title Design */
        .main-logo {
            text-align: center;
            font-size: 3.5rem;
            margin-bottom: 1rem;
            color: var(--accent-primary);
            text-shadow: 0 0 25px rgba(0, 229, 255, 0.4);
        }
        
        .main-title {
            text-align: center;
            font-size: clamp(2.2rem, 4vw, 3.2rem);
            font-weight: 800;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }
        
        .subtitle {
            text-align: center;
            font-size: clamp(1.0rem, 2vw, 1.3rem);
            color: var(--text-secondary);
            margin-bottom: 2.5rem;
            font-weight: 500;
            line-height: 1.6;
        }
        
        .creator-badge {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .creator-badge span {
            background: var(--accent-gradient);
            color: white;
            padding: 0.7rem 1.8rem;
            border-radius: 40px;
            font-size: 1.0rem;
            font-weight: 600;
            box-shadow: 0 6px 20px var(--shadow-primary);
        }
        
        /* Balanced Response Design */
        .response-header {
            background: var(--accent-gradient);
            color: white;
            padding: 1.8rem 2rem;
            border-radius: 20px 20px 0 0;
            font-size: clamp(1.2rem, 2.5vw, 1.5rem);
            font-weight: 700;
            text-align: center;
            box-shadow: 0 6px 25px var(--shadow-primary);
        }
        
        .response-container {
            background: linear-gradient(145deg, var(--glass-bg) 0%, rgba(46, 57, 86, 0.9) 100%);
            border-radius: 0 0 20px 20px;
            border: 1px solid var(--glass-border);
            box-shadow: 0 15px 35px var(--shadow-dark);
            margin-top: 0;
            overflow: hidden;
        }
        
        .response-meta {
            background: rgba(15, 23, 42, 0.8);
            padding: 1.2rem 2rem;
            border-bottom: 1px solid var(--border-primary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .response-badge {
            background: var(--accent-gradient);
            color: white;
            padding: 0.5rem 1.2rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 3px 10px var(--shadow-primary);
        }
        
        /* BALANCED Content Styling */
        .response-content {
            padding: 2.5rem;
            font-size: 1.25rem;  /* Optimized size */
            line-height: 1.7;    /* Better readability */
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            max-width: none;
            overflow-wrap: break-word;
        }
        
        .response-content h1 {
            font-size: 1.8rem;   /* Balanced heading size */
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 2px solid var(--accent-primary);
            padding-bottom: 0.6rem;
            margin: 2rem 0 1.2rem 0;
        }
        
        .response-content h2 {
            font-size: 1.5rem;   /* Balanced subheading */
            font-weight: 600;
            color: var(--accent-primary) !important;
            margin: 1.8rem 0 1rem 0;
            padding-left: 1rem;
            border-left: 3px solid var(--accent-primary);
        }
        
        .response-content h3 {
            font-size: 1.3rem;   /* Balanced sub-subheading */
            font-weight: 600;
            color: var(--accent-secondary) !important;
            margin: 1.5rem 0 0.8rem 0;
        }
        
        .response-content p {
            margin-bottom: 1.5rem;
            text-align: justify;
            font-size: 1.25rem;  /* Consistent with main content */
            line-height: 1.7;
            text-indent: 1.2rem;
        }
        
        .response-content ul, .response-content ol {
            margin: 1.5rem 0;
            padding-left: 2rem;
            font-size: 1.25rem;
        }
        
        .response-content li {
            margin-bottom: 0.6rem;
            line-height: 1.6;
        }
        
        /* ENHANCED MATHEMATICAL CONTENT */
        /* Inline LaTeX styling */
        .katex {
            font-family: 'Computer Modern Serif', 'Latin Modern Math', 'STIX Two Math', serif !important;
            font-size: 1.1em !important;
            color: var(--accent-primary) !important;
        }
        
        /* Display LaTeX styling */
        .katex-display {
            margin: 1.8rem 0 !important;
            padding: 1.2rem !important;
            background: var(--math-bg) !important;
            border-radius: 10px !important;
            border: 1px solid var(--math-border) !important;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.1) !important;
            position: relative !important;
        }
        
        .katex-display::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--accent-gradient);
            border-radius: 10px 0 0 10px;
        }
        
        /* Mathematical expressions in text */
        .response-content code {
            background: rgba(15, 23, 42, 0.6);
            color: var(--accent-tertiary);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            border: 1px solid var(--border-primary);
        }
        
        .response-content pre {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-primary);
            overflow-x: auto;
            margin: 1.5rem 0;
            font-size: 1.0rem;
            line-height: 1.5;
            box-shadow: 0 6px 20px var(--shadow-dark);
        }
        
        /* Equation numbering */
        .equation-number {
            float: right;
            color: var(--text-tertiary);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        /* Mathematical emphasis boxes */
        .math-highlight {
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), rgba(139, 92, 246, 0.05));
            border: 1px solid var(--math-border);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Form Elements with Reduced Sizes */
        .stTextArea > div > div > textarea {
            background: var(--glass-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.0rem !important;
            padding: 1rem !important;
        }
        
        .stSelectbox > div > div > div {
            background: var(--glass-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;
        }
        
        .stTextInput > div > div > input {
            background: var(--glass-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;
        }
        
        /* Button Styling */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 1rem 2rem !important;
            font-size: 1.0rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 15px var(--shadow-primary) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px var(--shadow-primary) !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, rgba(11, 15, 26, 0.95), rgba(21, 27, 46, 0.9)) !important;
            border-right: 2px solid var(--border-primary) !important;
        }
        
        /* Physics Domain Grid */
        .physics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .physics-domain {
            background: var(--glass-bg);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            border: 2px solid var(--glass-border);
            transition: all 0.3s ease;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .physics-domain:hover {
            border-color: var(--accent-primary);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px var(--shadow-primary);
        }
        
        /* Comprehensive Topics */
        .comprehensive-topics {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1));
            border-radius: 12px;
            padding: 1.2rem;
            margin: 1rem 0;
            border-left: 4px solid #10B981;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 2rem;
                margin: 1rem;
            }
            
            .response-content {
                padding: 2rem;
                font-size: 1.1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Physics Topics (keeping the same comprehensive list) ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT Pro - Complete Universe")
    
    all_physics_topics = [
        # Mathematical Physics
        "Vector Calculus & Tensor Analysis", "Complex Analysis & Contour Integration", 
        "Special Functions & Orthogonal Polynomials", "Green's Functions & Boundary Problems",
        "Group Theory & Symmetries", "Differential Geometry & Topology", "Variational Methods",
        "Fourier & Laplace Transforms", "Integral Equations", "Perturbation Theory",
        
        # Classical Mechanics
        "Newtonian Mechanics & Conservation Laws", "Lagrangian Mechanics & Constraints", 
        "Hamiltonian Mechanics & Phase Space", "Canonical Transformations", "Central Forces",
        "Rigid Body Dynamics & Euler Angles", "Small Oscillations & Normal Modes", 
        "Hamilton-Jacobi Theory", "Chaos & Nonlinear Dynamics", "Continuum Mechanics",
        
        # Quantum Mechanics
        "Wave-Particle Duality & de Broglie", "Schrödinger Equation & Wave Functions",
        "Quantum Harmonic Oscillator", "Hydrogen Atom & Spherical Harmonics", 
        "Angular Momentum & Spin", "Pauli Matrices & Spinors", "Perturbation Theory",
        "Time-Dependent Perturbations", "Scattering Theory & Cross Sections", 
        "Path Integral Formulation", "Second Quantization", "Many-Body Theory",
        
        # Additional domains...
        "Electromagnetic Theory", "Statistical Mechanics", "Solid State Physics",
        "Nuclear Physics", "Particle Physics", "Astrophysics", "Plasma Physics"
    ]
    
    st.markdown('<div class="comprehensive-topics">', unsafe_allow_html=True)
    st.markdown(f"**🌟 {len(all_physics_topics)} Balanced Physics Topics**")
    st.markdown("*Theory • Mathematics • LaTeX - Perfect Balance*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Topic selection
    selected_topic = st.selectbox(
        "Choose a physics topic:",
        options=["Select a topic..."] + all_physics_topics,
        key="balanced_topic_selector"
    )
    
    if selected_topic != "Select a topic...":
        st.session_state.selected_topic = selected_topic
        st.success(f"✅ Selected: {selected_topic}")

# --- Main Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="main-logo">🧠⚖️📐</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Physics GPT Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Balanced Mathematical Derivations • Theory Integration • Optimized LaTeX</div>', unsafe_allow_html=True)

# Enhanced physics domains
st.markdown("### 🌟 Balanced Physics Mastery")
physics_domains = [
    "🧮 Mathematical Physics", "⚛️ Classical Mechanics", "🌊 Quantum Mechanics", 
    "⚡ Electromagnetic Theory", "🔥 Statistical Mechanics", "💎 Solid State Physics"
]

st.markdown('<div class="physics-grid">', unsafe_allow_html=True)
for domain in physics_domains:
    st.markdown(f'<div class="physics-domain">{domain}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Metrics dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 Theory", "40%", "Conceptual")
with col2:
    st.metric("🧮 Mathematics", "40%", "Derivations")
with col3:
    st.metric("📐 LaTeX", "20%", "Strategic")
with col4:
    st.metric("⚖️ Balance", "Perfect", "Optimized")

# Main form
with st.form(key="balanced_physics_form", clear_on_submit=False):
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = f"Provide balanced analysis of {st.session_state.selected_topic} with theory, mathematical derivations, and strategic LaTeX formatting"
    
    query = st.text_area(
        "🎯 Ask for Balanced Physics Analysis:",
        value=default_question,
        placeholder="e.g., Explain quantum harmonic oscillator with balanced theory and mathematical derivations using strategic LaTeX",
        height=120,
        key="balanced_question"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        balance_style = st.selectbox(
            "📊 Balance Style:",
            ["Theory-Math-LaTeX (40-40-20)", "Math-Heavy (60-30-10)", 
             "Theory-Heavy (60-30-10)", "LaTeX-Rich (30-30-40)"]
        )
    
    with col2:
        derivation_depth = st.selectbox(
            "📐 Derivation Depth:",
            ["Conceptual Focus", "Balanced Steps", "Complete Derivation", "Research Level"]
        )
    
    with col3:
        latex_strategy = st.selectbox(
            "📝 LaTeX Strategy:",
            ["Strategic Placement", "Equation-Heavy", "Minimal Clean", "Mixed Approach"]
        )
    
    submit_button = st.form_submit_button("⚖️ Generate Balanced Analysis", use_container_width=True)

# --- Text extraction functions (same as before) ---
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

# --- Enhanced Answer Generation ---
if submit_button and query:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("⚖️ Balancing theory, mathematics, and LaTeX...")
    progress_bar.progress(50)
    time.sleep(0.5)
    
    status_text.text("📐 Optimizing mathematical presentation...")
    progress_bar.progress(100)
    
    # Enhanced prompt for balanced content
    balanced_prompt = f"""
BALANCED PHYSICS ANALYSIS REQUEST

BALANCE CONFIGURATION:
- STYLE: {balance_style}
- DERIVATION DEPTH: {derivation_depth}
- LATEX STRATEGY: {latex_strategy}

SPECIFIC REQUIREMENTS:
1. THEORY (40%): Provide clear conceptual explanations, physical intuition, and real-world context
2. MATHEMATICS (40%): Include step-by-step derivations with logical progression and intermediate steps
3. LATEX (20%): Use strategic LaTeX formatting for key equations and mathematical expressions

LATEX USAGE GUIDELINES:
- Inline math for simple expressions: $E = mc^2$
- Display equations for important results: $$\\hat{H}\\psi = E\\psi$$
- Proper vector notation: $\\vec{{F}} = q(\\vec{{E}} + \\vec{{v}} \\times \\vec{{B}})$
- Greek letters and symbols: $\\alpha, \\beta, \\gamma, \\Delta, \\nabla$
- Integrals and derivatives: $\\frac{{d\\psi}}{{dt}} = \\frac{{1}}{{i\\hbar}}\\hat{{H}}\\psi$

PHYSICS QUESTION: {query}

Provide a perfectly balanced response with equal emphasis on theoretical understanding, mathematical rigor, and strategic LaTeX presentation.
"""

    progress_bar.empty()
    status_text.empty()

    # Generate balanced response
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"question": balanced_prompt})

    # Display balanced response
    st.markdown('<div class="response-header">⚖️ Balanced Physics Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Response metadata
    st.markdown('<div class="response-meta">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="response-badge">Balance: {balance_style.split()[0]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="response-badge">Depth: {derivation_depth.split()[0]}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="response-badge">LaTeX: {latex_strategy.split()[0]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main balanced content
    st.markdown('<div class="response-content">{}</div>'.format(response), unsafe_allow_html=True)
    
    # Balanced signature
    st.markdown('<div style="background: rgba(15, 23, 42, 0.8); padding: 1.5rem; text-align: center; border-top: 1px solid #334155;">⚖️ <strong style="background: linear-gradient(135deg, #00E5FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Balanced Analysis by Physics GPT Pro</strong><br><em>Perfect harmony of Theory • Mathematics • LaTeX</em><br>Created by <strong>Sreekesh M</strong></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer ---
st.markdown(f"""
<div style="text-align: center; color: #CBD5E1; padding: 2rem; font-family: 'Inter', sans-serif;">
    <div style="font-size: 1.6rem; font-weight: 700; margin-bottom: 1rem;">
        ⚖️ <strong style="background: linear-gradient(135deg, #00E5FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT Pro</strong>
    </div>
    <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 0.95rem;">
        📚 <strong>Theory</strong> • 🧮 <strong>Mathematics</strong> • 📐 <strong>LaTeX</strong> - Perfect Balance
    </div>
</div>
""", unsafe_allow_html=True)
