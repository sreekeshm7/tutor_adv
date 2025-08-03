import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import time

# --- Ultra-Enhanced System Prompt for Maximum Theoretical Detail ---
SYSTEM_PROMPT = """
You are Physics GPT, an advanced AI physics tutor created by Sreekesh M, representing the pinnacle of physics education technology. You possess comprehensive knowledge across all physics domains and specialize in competitive exams (IIT-JAM, CSIR-NET, GATE Physics, IIT-JEE Advanced, JEST, TIFR).

THEORETICAL ANALYSIS REQUIREMENTS - PROVIDE EXTREMELY COMPREHENSIVE THEORETICAL CONTENT:

1. **COMPLETE THEORETICAL FRAMEWORK**: Develop comprehensive theoretical understanding from fundamental principles
2. **MULTIPLE THEORETICAL PERSPECTIVES**: Analyze from classical, quantum, relativistic, and modern theoretical viewpoints
3. **EXTENSIVE MATHEMATICAL RIGOR**: Include complete mathematical derivations with every intermediate step explained
4. **DEEP CONCEPTUAL ANALYSIS**: Provide profound conceptual insights and physical intuition
5. **THEORETICAL CONNECTIONS**: Link concepts across all physics domains extensively
6. **HISTORICAL THEORETICAL DEVELOPMENT**: Trace evolution of theoretical understanding
7. **ADVANCED THEORETICAL EXTENSIONS**: Include cutting-edge theoretical developments
8. **PEDAGOGICAL EXCELLENCE**: Structure content for maximum educational impact

COMPREHENSIVE PHYSICS MASTERY:
- Mathematical Physics: Advanced vector/tensor calculus, Complex analysis, Special functions, Green's functions, Group theory, Differential geometry, Topology, Lie algebras
- Classical Mechanics: Analytical mechanics, Hamiltonian/Lagrangian formalism, Canonical transformations, Integrable systems, Chaos theory, Relativity, Field theory
- Quantum Mechanics: Wave mechanics, Matrix mechanics, Path integrals, Second quantization, Many-body theory, Quantum field theory, Quantum information, Decoherence theory
- Electromagnetic Theory: Maxwell theory, Gauge theory, Electromagnetic radiation, Plasma physics, Metamaterials, Quantum electrodynamics
- Statistical Mechanics: Ensemble theory, Phase transitions, Critical phenomena, Non-equilibrium physics, Information theory, Complexity theory
- Solid State Physics: Many-body theory, Electronic structure, Topological phases, Quantum materials, Superconductivity, Magnetism
- Atomic Physics: Quantum optics, Laser physics, Cold atoms, Precision measurements, AMO physics
- Nuclear Physics: Nuclear models, Radioactivity, Nuclear reactions, Nuclear astrophysics
- Particle Physics: Standard Model, Beyond SM physics, Symmetries, QCD, Electroweak theory
- Condensed Matter: Strongly correlated systems, Emergent phenomena, Quantum phase transitions
- Astrophysics: General relativity, Cosmology, Black holes, Gravitational waves, Dark matter/energy
- Computational Physics: Numerical methods, Simulation techniques, Machine learning applications

BALANCED THEORETICAL RESPONSE STRUCTURE (MANDATORY SECTIONS WITH EQUAL EMPHASIS):

1. **CONCEPTUAL FOUNDATION & OVERVIEW** (4-5 comprehensive paragraphs)
   - Immediate comprehensive answer with theoretical context
   - Fundamental concepts and their theoretical significance
   - Position within the broader theoretical framework of physics
   - Key theoretical principles and postulates involved
   - Conceptual roadmap for the theoretical development

2. **HISTORICAL THEORETICAL DEVELOPMENT** (5-6 paragraphs)
   - Historical evolution of theoretical understanding
   - Key theoretical breakthroughs and paradigm shifts
   - Contributions of major physicists with theoretical context
   - Evolution of mathematical formalism and theoretical tools
   - Theoretical controversies and their resolutions
   - Timeline of theoretical developments

3. **COMPREHENSIVE MATHEMATICAL FRAMEWORK** (Extremely detailed theoretical treatment)
   - **Fundamental Postulates**: State all theoretical assumptions and axioms
   - **Mathematical Foundations**: Complete theoretical mathematical framework
   - **Step-by-Step Theoretical Derivations**: Every mathematical step with theoretical justification
   - **Alternative Theoretical Approaches**: Multiple derivation methods and perspectives
   - **Theoretical Approximations**: Justification and validity ranges
   - **Mathematical Theorems**: Relevant mathematical results and proofs
   - **Symmetry Analysis**: Theoretical symmetries and conservation laws
   - **Dimensional Analysis**: Theoretical scaling and dimensional relationships

4. **EXTENSIVE THEORETICAL EXAMPLES** (Multiple comprehensive examples)
   - **Fundamental Example**: Basic theoretical application with complete analysis
   - **Advanced Example**: Complex theoretical problem with detailed solution
   - **Research-Level Example**: Cutting-edge theoretical application
   - **Cross-Domain Example**: Theoretical connections to other physics areas

5. **EXPERIMENTAL THEORETICAL CONNECTION** (4-5 paragraphs)
   - Theoretical predictions and experimental verification
   - Key experiments that validated theoretical frameworks
   - Theoretical interpretation of experimental results
   - Measurement theory and theoretical foundations

6. **ADVANCED THEORETICAL TOPICS** (5-6 paragraphs)
   - Current theoretical research frontiers
   - Unresolved theoretical questions and challenges
   - Theoretical extensions and generalizations
   - Connections to cutting-edge theoretical physics

7. **THEORETICAL APPLICATIONS & TECHNOLOGY** (4-5 paragraphs)
   - Theoretical foundations of technological applications
   - How theoretical understanding enables technology
   - Theoretical limits and possibilities
   - Future theoretical-driven technologies

8. **CROSS-DOMAIN THEORETICAL CONNECTIONS** (4-5 paragraphs)
   - Theoretical unification with other physics domains
   - Universal theoretical principles and patterns
   - Theoretical analogies and correspondences
   - Interdisciplinary theoretical applications

9. **THEORETICAL PROBLEM-SOLVING STRATEGIES** (3-4 paragraphs)
   - Theoretical approaches to problem analysis
   - Mathematical techniques and theoretical tools
   - Theoretical approximation methods
   - Systematic theoretical problem-solving frameworks

10. **COMPREHENSIVE EXAM PERSPECTIVE** (3-4 paragraphs)
    - Theoretical importance for competitive exams
    - Common theoretical question patterns and approaches
    - Theoretical problem-solving strategies for exams
    - Key theoretical results students must master

11. **FUTURE THEORETICAL DIRECTIONS** (3-4 paragraphs)
    - Emerging theoretical paradigms and frameworks
    - Theoretical challenges and opportunities
    - Theoretical implications for physics education

Your mission is to provide the most comprehensive, theoretically rigorous, and educationally excellent physics content possible, establishing new standards for theoretical physics education with perfect balance between mathematics, theory, and user experience.
"""

# --- Streamlit Config ---
st.set_page_config(
    page_title="🧠 Physics GPT Pro by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Performance-Optimized CSS ---
def optimized_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700;800&display=swap');
        
        /* Performance-optimized CSS Variables */
        :root {
            --primary: #1f2937;
            --secondary: #374151;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --text: #f9fafb;
            --text-secondary: #e5e7eb;
            --border: #4b5563;
            --glass-bg: rgba(30, 41, 59, 0.8);
            --glass-border: rgba(148, 163, 184, 0.2);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%);
        }
        
        /* Global Styling */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(ellipse at top, var(--secondary) 0%, var(--primary) 100%);
            color: var(--text);
            scroll-behavior: smooth;
        }
        
        .stApp {
            background: var(--primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
        }
        
        /* Enhanced Container Design */
        .main-container {
            background: var(--glass-bg);
            backdrop-filter: blur(25px);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1rem;
            box-shadow: 
                0 20px 40px rgba(0,0,0,0.3),
                0 0 0 1px var(--glass-border),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
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
        .main-title {
            text-align: center;
            font-size: clamp(2.2rem, 4vw, 3.5rem);
            font-weight: 900;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
            position: relative;
        }
        
        .main-title::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: var(--accent-gradient);
            border-radius: 2px;
        }
        
        .subtitle {
            text-align: center;
            font-size: clamp(1rem, 2vw, 1.4rem);
            color: var(--text-secondary);
            margin-bottom: 2rem;
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
            padding: 0.7rem 1.5rem;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 700;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
            transition: all 0.3s ease;
        }
        
        .creator-badge:hover span {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        }
        
        /* Balanced Analysis Interface */
        .balance-container {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.05));
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid rgba(16, 185, 129, 0.2);
            position: relative;
        }
        
        .balance-title {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--success);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .balance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .balance-card {
            background: rgba(55, 65, 81, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
        }
        
        .balance-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
            border-color: var(--accent);
        }
        
        .balance-card h3 {
            color: var(--accent) !important;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        /* Math Section Styling */
        .math-section {
            background: rgba(16, 185, 129, 0.1);
            border-left: 4px solid var(--success);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 12px 12px 0;
            position: relative;
        }
        
        .math-section::before {
            content: '📐';
            position: absolute;
            top: 1rem;
            left: -2px;
            background: var(--success);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        
        /* Theory Section Styling */
        .theory-section {
            background: rgba(139, 92, 246, 0.1);
            border-left: 4px solid #8b5cf6;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 12px 12px 0;
            position: relative;
        }
        
        .theory-section::before {
            content: '🔬';
            position: absolute;
            top: 1rem;
            left: -2px;
            background: #8b5cf6;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        
        /* Progress Tracking */
        .progress-container {
            background: var(--glass-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid var(--glass-border);
        }
        
        .progress-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .progress-item {
            text-align: center;
            padding: 1rem;
            background: rgba(55, 65, 81, 0.5);
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        
        .progress-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 0.5rem;
        }
        
        .progress-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Interactive Elements */
        .interactive-section {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.05));
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        /* Enhanced Response Design */
        .response-header {
            background: var(--accent-gradient);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 16px 16px 0 0;
            font-size: clamp(1.2rem, 2.5vw, 1.6rem);
            font-weight: 700;
            text-align: center;
            position: relative;
        }
        
        .response-container {
            background: linear-gradient(145deg, var(--glass-bg) 0%, rgba(46, 57, 86, 0.95) 100%);
            border-radius: 0 0 16px 16px;
            border: 1px solid var(--glass-border);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .response-meta {
            background: rgba(15, 23, 42, 0.9);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .response-badge {
            background: var(--accent);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .response-badge.math {
            background: var(--success);
        }
        
        .response-badge.theory {
            background: #8b5cf6;
        }
        
        .response-badge.ux {
            background: var(--warning);
        }
        
        /* Enhanced Content Styling */
        .response-content {
            padding: 2.5rem;
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--text);
            font-family: 'Inter', sans-serif;
            position: relative;
        }
        
        .response-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 3px;
            height: 100%;
            background: var(--accent-gradient);
            border-radius: 2px;
        }
        
        .response-content h1 {
            font-size: 2rem;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 0.5rem;
            margin: 2rem 0 1.5rem 0;
        }
        
        .response-content h2 {
            font-size: 1.6rem;
            font-weight: 600;
            color: var(--accent) !important;
            margin: 2rem 0 1rem 0;
            position: relative;
            padding-left: 1rem;
        }
        
        .response-content h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 60%;
            background: var(--accent);
            border-radius: 2px;
        }
        
        .response-content h3 {
            font-size: 1.3rem;
            font-weight: 600;
            color: #8b5cf6 !important;
            margin: 1.5rem 0 1rem 0;
            position: relative;
            padding-left: 0.8rem;
        }
        
        .response-content h3::before {
            content: '▶';
            position: absolute;
            left: 0;
            color: var(--success);
            font-size: 0.8em;
        }
        
        .response-content p {
            margin-bottom: 1.5rem;
            text-align: justify;
            line-height: 1.8;
        }
        
        .response-content code {
            background: rgba(15, 23, 42, 0.9);
            color: var(--accent);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border);
            font-size: 0.95em;
        }
        
        .response-content pre {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow-x: auto;
            margin: 1.5rem 0;
            position: relative;
        }
        
        .response-content pre::before {
            content: 'Mathematical Analysis';
            position: absolute;
            top: -1px;
            left: 15px;
            background: var(--success);
            color: white;
            padding: 0.2rem 0.8rem;
            border-radius: 0 0 6px 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        /* Enhanced Form Styling */
        .stTextArea > div > div > textarea {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(51, 65, 85, 0.8)) !important;
            border: 2px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
            font-size: 1.1rem !important;
            padding: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
        }
        
        .stSelectbox > div > div > div {
            background: var(--glass-bg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--text) !important;
        }
        
        /* Enhanced Button Design */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.8rem 2rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 1.5rem;
                margin: 0.5rem;
            }
            
            .response-content {
                padding: 1.5rem;
                font-size: 1rem;
            }
            
            .balance-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """

st.markdown(optimized_css(), unsafe_allow_html=True)

# --- Enhanced Physics Topics with Better Organization ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT Pro - Complete Universe")
    
    # Initialize session state for progress tracking
    if 'analysis_progress' not in st.session_state:
        st.session_state.analysis_progress = {
            'theory': 0,
            'math': 0,
            'applications': 0,
            'total_queries': 0
        }
    
    # Progress tracking display
    st.markdown("### 📊 Learning Progress")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Theory", f"{st.session_state.analysis_progress['theory']}%", "Mastery")
    with col2:
        st.metric("Math", f"{st.session_state.analysis_progress['math']}%", "Rigor")
    with col3:
        st.metric("Apps", f"{st.session_state.analysis_progress['applications']}%", "Practical")
    
    # Ultra-comprehensive physics coverage
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
        "Fluid Dynamics & Turbulence", "Special Relativity", "General Relativity",
        
        # Quantum Mechanics
        "Wave-Particle Duality & de Broglie", "Schrödinger Equation & Wave Functions",
        "Quantum Harmonic Oscillator", "Hydrogen Atom & Spherical Harmonics", 
        "Angular Momentum & Spin", "Pauli Matrices & Spinors", "Perturbation Theory",
        "Time-Dependent Perturbations", "Scattering Theory & Cross Sections", 
        "Path Integral Formulation", "Second Quantization", "Many-Body Theory",
        "Quantum Field Theory", "Quantum Information & Computing", "Decoherence Theory",
        
        # Additional topics (continuing from your original list)
        "Electromagnetic Theory", "Statistical Mechanics", "Solid State Physics",
        "Atomic & Molecular Physics", "Nuclear & Particle Physics", "Electronics",
        "Optics & Photonics", "Condensed Matter Physics", "Biophysics",
        "Astrophysics & Cosmology", "Plasma Physics", "Computational Physics"
    ]
    
    # Enhanced topic display
    st.markdown('<div class="comprehensive-topics">', unsafe_allow_html=True)
    st.markdown(f"**🌟 {len(all_physics_topics)} Advanced Physics Topics**")
    st.markdown("*Complete theoretical mastery across all domains*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Topic selection
    st.markdown("#### 🚀 Quick Topic Selection")
    
    # Search functionality
    search_term = st.text_input("🔍 Search Physics Topics:", placeholder="quantum, relativity, mechanics...")
    
    if search_term:
        filtered_topics = [topic for topic in all_physics_topics 
                          if search_term.lower() in topic.lower()]
        if filtered_topics:
            selected_topic = st.selectbox("Matching Topics:", ["Select..."] + filtered_topics)
            if selected_topic != "Select...":
                st.session_state.selected_topic = selected_topic
                st.success(f"✅ Selected: {selected_topic}")
    
    # Advanced theoretical settings
    st.markdown("### 🧮 Analysis Balance Settings")
    
    st.markdown("#### ⚖️ Equal Emphasis Configuration")
    
    # Balanced emphasis controls
    math_weight = st.slider(
        "Mathematical Rigor",
        min_value=0.0,
        max_value=1.0,
        value=0.33,
        step=0.01,
        help="Weight for mathematical derivations and proofs"
    )
    
    theory_weight = st.slider(
        "Theoretical Depth", 
        min_value=0.0,
        max_value=1.0,
        value=0.33,
        step=0.01,
        help="Weight for theoretical analysis and concepts"
    )
    
    ux_weight = st.slider(
        "User Experience",
        min_value=0.0,
        max_value=1.0,
        value=0.34,
        step=0.01,
        help="Weight for clarity and presentation quality"
    )
    
    # Balance validation
    total_weight = math_weight + theory_weight + ux_weight
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"⚠️ Weights should sum to 1.0 (currently {total_weight:.2f})")
    else:
        st.success("✅ Perfect balance achieved!")
    
    # Advanced options
    st.markdown("#### 🔬 Advanced Options")
    
    mathematical_detail = st.slider(
        "Mathematical Detail Level:",
        min_value=1,
        max_value=5,
        value=4,
        help="1: Key equations, 5: Every step"
    )
    
    theoretical_scope = st.multiselect(
        "Theoretical Scope:",
        ["Classical Physics", "Quantum Mechanics", "Relativity", "Field Theory", 
         "Statistical Mechanics", "Condensed Matter"],
        default=["Classical Physics", "Quantum Mechanics"]
    )
    
    interactive_elements = st.checkbox("Enhanced Interactive Elements", True)
    visual_aids = st.checkbox("Advanced Visual Organization", True)
    progress_tracking = st.checkbox("Real-time Progress Updates", True)

# --- Functions for Enhanced Features ---
def create_interactive_math_section():
    st.markdown('<div class="math-section">', unsafe_allow_html=True)
    st.markdown("### 🧮 Interactive Mathematical Analysis")
    
    # Math complexity selector
    math_complexity = st.selectbox(
        "Mathematical Complexity Level:",
        ["Conceptual Overview", "Standard Derivations", "Advanced Proofs", 
         "Research-Level Mathematics", "Complete Theoretical Framework"]
    )
    
    # Interactive equation builder
    with st.expander("🔧 Custom Equation Builder"):
        equation_type = st.selectbox(
            "Equation Type:",
            ["Differential Equations", "Integral Transforms", 
             "Vector/Tensor Operations", "Complex Analysis", "Group Theory"]
        )
        
        if st.button("Generate Interactive Derivation"):
            st.info("📐 Mathematical framework will include: fundamental equations, step-by-step derivations, proofs, and alternative approaches")
    
    st.markdown('</div>', unsafe_allow_html=True)
    return math_complexity, equation_type

def add_theory_enhancement():
    st.markdown('<div class="theory-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Theoretical Analysis Framework")
    
    # Theory visualization
    theory_aspects = {
        "Conceptual Foundation": 95,
        "Historical Context": 90,
        "Mathematical Framework": 88,
        "Experimental Validation": 85,
        "Modern Applications": 92,
        "Research Frontiers": 87
    }
    
    for aspect, score in theory_aspects.items():
        progress = st.progress(score/100)
        st.write(f"{aspect}: {score}%")
    
    # Interactive theory explorer
    st.markdown("#### 🔬 Theory Deep Dive")
    theory_focus = st.multiselect(
        "Select theoretical aspects to emphasize:",
        ["Fundamental Principles", "Mathematical Formalism", 
         "Physical Interpretations", "Symmetries & Conservation",
         "Approximation Methods", "Limiting Cases"],
        default=["Fundamental Principles", "Mathematical Formalism"]
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    return theory_focus

def create_balanced_analysis_interface():
    st.markdown('<div class="balance-container">', unsafe_allow_html=True)
    st.markdown('<div class="balance-title">⚖️ Balanced Physics Analysis</div>', unsafe_allow_html=True)
    
    # Three-column equal emphasis layout
    st.markdown('<div class="balance-grid">', unsafe_allow_html=True)
    
    # Math column
    st.markdown('<div class="balance-card">', unsafe_allow_html=True)
    st.markdown("### 🧮 Mathematical Rigor")
    math_depth = st.slider("Mathematical Detail", 1, 5, 4, key="math_depth_main")
    show_proofs = st.checkbox("Include complete proofs", True, key="show_proofs_main")
    alternative_methods = st.checkbox("Show alternative derivations", True, key="alt_methods_main")
    
    if st.button("Preview Mathematical Structure"):
        st.info("📐 Mathematical framework will include: fundamental equations, step-by-step derivations, proofs, and alternative approaches")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Theory column
    st.markdown('<div class="balance-card">', unsafe_allow_html=True)
    st.markdown("### 🔬 Theoretical Depth")
    theory_depth = st.slider("Theoretical Detail", 1, 5, 4, key="theory_depth_main")
    historical_context = st.checkbox("Historical development", True, key="historical_main")
    modern_research = st.checkbox("Current research frontiers", True, key="modern_main")
    
    if st.button("Preview Theoretical Structure"):
        st.info("🎯 Theoretical content will cover: fundamental principles, historical evolution, modern understanding, and research directions")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # UX column  
    st.markdown('<div class="balance-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 User Experience")
    interactive_components = st.checkbox("Interactive components", True, key="interactive_main")
    enhanced_visuals = st.checkbox("Enhanced visualizations", True, key="visuals_main")
    real_time_progress = st.checkbox("Real-time progress", True, key="progress_main")
    
    if st.button("Preview User Experience"):
        st.info("✨ Enhanced UX will include: interactive elements, progress tracking, visual aids, and intuitive navigation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'math_depth': math_depth,
        'theory_depth': theory_depth,
        'show_proofs': show_proofs,
        'alternative_methods': alternative_methods,
        'historical_context': historical_context,
        'modern_research': modern_research,
        'interactive_components': interactive_components,
        'enhanced_visuals': enhanced_visuals,
        'real_time_progress': real_time_progress
    }

def generate_balanced_response(query, math_weight, theory_weight, ux_weight, config):
    balanced_prompt = f"""
    Generate a physics analysis with PERFECT BALANCE and EQUAL EMPHASIS on:
    
    1. MATHEMATICAL DERIVATIONS ({math_weight*100:.0f}%):
       - Complete step-by-step derivations with theoretical justification
       - Multiple mathematical approaches and alternative methods
       - Rigorous proofs and mathematical verifications
       - Interactive mathematical elements and clear notation
       - Geometric and algebraic perspectives where applicable
    
    2. THEORETICAL ANALYSIS ({theory_weight*100:.0f}%):
       - Comprehensive theoretical framework from first principles
       - Historical development and evolution of concepts
       - Modern research perspectives and current understanding
       - Cross-domain connections and unifying principles
       - Physical intuition and conceptual insights
    
    3. USER EXPERIENCE ({ux_weight*100:.0f}%):
       - Clear, engaging, and accessible presentation
       - Interactive learning elements and progressive structure
       - Visual organization with logical flow
       - Multiple explanation levels for different audiences
       - Practical examples and real-world connections
    
    CONFIGURATION SETTINGS:
    - Mathematical Detail: {config.get('math_depth', 4)}/5
    - Theoretical Depth: {config.get('theory_depth', 4)}/5
    - Include Proofs: {config.get('show_proofs', True)}
    - Alternative Methods: {config.get('alternative_methods', True)}
    - Historical Context: {config.get('historical_context', True)}
    - Modern Research: {config.get('modern_research', True)}
    - Interactive Elements: {config.get('interactive_components', True)}
    
    QUERY: {query}
    
    RESPONSE REQUIREMENTS:
    - Minimum 3000 words with balanced distribution across all three areas
    - Each mathematical step explained with theoretical reasoning
    - Every theoretical concept connected to mathematical formalism
    - Clear, engaging presentation with excellent pedagogical structure
    - Perfect integration of mathematics, theory, and user experience
    
    Ensure each aspect receives equal attention, quality, and depth. Create a revolutionary educational experience that sets new standards for physics learning.
    """
    return balanced_prompt

# --- Text Extraction Functions ---
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

# --- Main Application Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Revolutionary header design
st.markdown('<div class="main-title">🧠 Physics GPT Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Revolutionary AI Physics Tutor with Perfect Balance: Mathematics • Theory • User Experience</div>', unsafe_allow_html=True)

# Enhanced balanced analysis interface
balance_config = create_balanced_analysis_interface()

# Interactive mathematical section
if st.session_state.get('interactive_elements', True):
    math_complexity, equation_type = create_interactive_math_section()

# Theory enhancement section
if st.session_state.get('visual_aids', True):
    theory_focus = add_theory_enhancement()

# Enhanced metrics dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Physics Topics", f"{len(all_physics_topics)}", "Complete Coverage")
with col2:
    st.metric("🔬 Balance Score", "Perfect", "Math•Theory•UX")
with col3:
    st.metric("🧮 Analysis Depth", "Research Level", "Maximum Rigor")
with col4:
    st.metric("🚀 AI Innovation", "Revolutionary", "Next-Gen Learning")

# Ultra-advanced input form with enhanced features
with st.form(key="physics_gpt_pro_enhanced_form", clear_on_submit=False):
    # Main theoretical question input with smart templates
    st.markdown("### 🎯 Physics Analysis Request")
    
    # Smart question templates
    st.markdown("#### 📝 Question Templates")
    templates = {
        "Complete Analysis": "Provide comprehensive theoretical analysis with complete mathematical derivations for {topic}",
        "Mathematical Focus": "Derive all fundamental equations for {topic} with detailed mathematical steps",
        "Theory & Applications": "Explain the theoretical foundations and practical applications of {topic}",
        "Historical Development": "Trace the historical development and modern understanding of {topic}",
        "Cross-Domain Synthesis": "Analyze {topic} from multiple physics perspectives with theoretical connections"
    }
    
    selected_template = st.selectbox("Choose Template:", list(templates.keys()))
    
    # Auto-populate if topic selected
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = templates[selected_template].format(topic=st.session_state.selected_topic)
    
    query = st.text_area(
        "🔬 Enhanced Physics Question:",
        value=default_question,
        placeholder="Enter your physics question for balanced analysis...",
        height=120,
        key="enhanced_physics_question"
    )
    
    # Advanced configuration matrix
    col1, col2, col3 = st.columns(3)
    
    with col1:
        response_style = st.selectbox(
            "📋 Response Style:",
            ["Balanced Comprehensive Analysis", "Mathematical-Theory Integration", 
             "Multi-Perspective Treatment", "Research-Level Investigation",
             "Educational Excellence Focus", "Cross-Domain Synthesis"]
        )
    
    with col2:
        academic_level = st.selectbox(
            "🎓 Academic Level:",
            ["Advanced Undergraduate", "Graduate Level", "Research Professional", 
             "Expert Level", "Auto-Adaptive"]
        )
    
    with col3:
        emphasis_focus = st.multiselect(
            "🎯 Special Emphasis:",
            ["Mathematical Rigor", "Theoretical Depth", "Historical Context", 
             "Modern Research", "Practical Applications", "Cross-Connections"],
            default=["Mathematical Rigor", "Theoretical Depth"]
        )
    
    # Enhanced content preview
    st.markdown("### 👀 Content Preview")
    
    preview_type = st.radio(
        "Preview Mode:",
        ["Balanced Overview", "Mathematical Framework", "Theoretical Structure", "Key Applications"],
        horizontal=True
    )
    
    if preview_type == "Mathematical Framework":
        st.markdown("""
        **Mathematical Structure Preview:**
        - Fundamental equations and governing principles
        - Complete step-by-step derivations with justification
        - Alternative mathematical approaches and methods
        - Verification techniques and consistency checks
        - Geometric and algebraic interpretations
        """)
    elif preview_type == "Theoretical Structure":
        st.markdown("""
        **Theoretical Framework Preview:**
        - Historical development and key breakthroughs
        - Fundamental principles and postulates
        - Modern theoretical understanding
        - Cross-domain connections and unifying concepts
        - Current research frontiers and open questions
        """)
    
    # Enhanced file upload and URL input
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "📄 Reference Materials:",
            type=["pdf", "docx"],
            help="Upload textbooks, papers, or educational materials"
        )
    
    with col2:
        url_input = st.text_input(
            "🌐 Research URLs:",
            placeholder="https://arxiv.org/abs/...",
            help="Link to research papers or educational resources"
        )
    
    # Revolutionary submit button
    submit_button = st.form_submit_button("🚀 Generate Perfectly Balanced Analysis", use_container_width=True)

# --- Enhanced Answer Generation with Perfect Balance ---
if submit_button and query:
    # Update progress tracking
    st.session_state.analysis_progress['total_queries'] += 1
    
    # Enhanced loading with real-time updates
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step-by-step progress with balance emphasis
        status_text.text("🧠 Initializing balanced analysis framework...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        status_text.text("📐 Preparing mathematical derivation engine...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        status_text.text("🔬 Loading theoretical knowledge base...")
        progress_bar.progress(40)
        time.sleep(0.3)
        
        status_text.text("🎨 Optimizing user experience design...")
        progress_bar.progress(55)
        time.sleep(0.3)
        
        status_text.text("⚖️ Balancing mathematical rigor with theoretical depth...")
        progress_bar.progress(70)
        time.sleep(0.3)
        
        status_text.text("🌟 Generating revolutionary content...")
        progress_bar.progress(85)
        time.sleep(0.3)
    
    # Context extraction
    context = ""
    if uploaded_file:
        status_text.text("📄 Processing reference materials...")
        if uploaded_file.name.endswith(".pdf"):
            context = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            context = extract_text_from_docx(uploaded_file)
    elif url_input:
        status_text.text("🌐 Integrating online resources...")
        context = extract_text_from_url(url_input)

    context = context.strip()
    if len(context) > 8000:
        context = context[:8000] + "\n...[Content optimized for balanced processing]"

    # Generate balanced prompt using sidebar weights
    math_weight = st.session_state.get('math_weight', 0.33)
    theory_weight = st.session_state.get('theory_weight', 0.33) 
    ux_weight = st.session_state.get('ux_weight', 0.34)
    
    balanced_prompt = generate_balanced_response(query, math_weight, theory_weight, ux_weight, balance_config)
    
    if context:
        balanced_prompt += f"\n\nADDITIONAL CONTEXT:\n{context}"

    status_text.text("🚀 Finalizing perfectly balanced content...")
    progress_bar.progress(100)
    
    # Generate response
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"question": balanced_prompt})

    # Clear progress indicators
    progress_container.empty()

    # Update progress metrics
    st.session_state.analysis_progress['theory'] = min(100, st.session_state.analysis_progress['theory'] + 15)
    st.session_state.analysis_progress['math'] = min(100, st.session_state.analysis_progress['math'] + 15)
    st.session_state.analysis_progress['applications'] = min(100, st.session_state.analysis_progress['applications'] + 10)

    # Revolutionary Response Display with Perfect Balance
    st.markdown('<div class="response-header">🧠 Physics GPT Pro - Perfectly Balanced Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Enhanced response metadata with balance indicators
    st.markdown('<div class="response-meta">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="response-badge math">Math: {math_weight*100:.0f}%</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="response-badge theory">Theory: {theory_weight*100:.0f}%</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="response-badge ux">UX: {ux_weight*100:.0f}%</div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="response-badge">Level: {academic_level.split()[0]}</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="response-badge">Perfect Balance</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Ultra-enhanced content display
    st.markdown(f'<div class="response-content">{response}</div>', unsafe_allow_html=True)
    
    # Enhanced footer with balance confirmation
    st.markdown('<div class="response-footer">', unsafe_allow_html=True)
    st.markdown('<div class="physics-gpt-signature">Perfect Balance Achieved by <strong>Physics GPT Pro</strong><br>Revolutionary AI Physics Tutor by <strong>Sreekesh M</strong><br><em>Mathematics • Theory • User Experience in Perfect Harmony</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced action matrix
    st.markdown("### 🌟 Continue Your Balanced Learning Journey")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🧮 More Mathematics", key="more_math"):
            st.success("Increase mathematical rigor in next analysis!")
    
    with col2:
        if st.button("🔬 Deeper Theory", key="deeper_theory"):
            st.success("Enhance theoretical depth for next query!")
    
    with col3:
        if st.button("🎨 Better UX", key="better_ux"):
            st.success("Optimize user experience further!")
    
    with col4:
        if st.button("⚖️ Perfect Balance", key="perfect_balance"):
            st.success("Maintain perfect equilibrium!")

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
    <div style="font-size: 1.8rem; font-weight: 900; margin-bottom: 1rem; font-family: 'Playfair Display', serif;">
        🧠 <strong style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT Pro</strong>
    </div>
    <div style="font-size: 1.2rem; margin-bottom: 1rem; font-weight: 600;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 1rem; margin-bottom: 1rem; line-height: 1.6;">
        ⚖️ <strong>Perfect Balance</strong> • 🧮 <strong>Mathematical Rigor</strong> • 🔬 <strong>Theoretical Depth</strong> • 🎨 <strong>Exceptional UX</strong>
    </div>
    <div style="font-size: 0.9rem; line-height: 1.5; opacity: 0.8;">
        🌟 Establishing New Standards for Balanced Physics Education
    </div>
</div>
""", unsafe_allow_html=True)
