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

ULTRA-DETAILED THEORETICAL RESPONSE STRUCTURE (MANDATORY SECTIONS):

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
   - Each example includes:
     * Theoretical setup and assumptions
     * Complete mathematical theoretical analysis
     * Physical interpretation and theoretical insights
     * Connections to broader theoretical frameworks
     * Limitations and theoretical extensions

5. **EXPERIMENTAL THEORETICAL CONNECTION** (4-5 paragraphs)
   - Theoretical predictions and experimental verification
   - Key experiments that validated theoretical frameworks
   - Theoretical interpretation of experimental results
   - Measurement theory and theoretical foundations
   - Theoretical limits of experimental precision
   - Future experimental tests of theoretical predictions

6. **ADVANCED THEORETICAL TOPICS** (5-6 paragraphs)
   - Current theoretical research frontiers
   - Unresolved theoretical questions and challenges
   - Theoretical extensions and generalizations
   - Connections to cutting-edge theoretical physics
   - Theoretical implications for future physics
   - Speculative theoretical developments

7. **THEORETICAL APPLICATIONS & TECHNOLOGY** (4-5 paragraphs)
   - Theoretical foundations of technological applications
   - How theoretical understanding enables technology
   - Theoretical limits and possibilities
   - Future theoretical-driven technologies
   - Theoretical optimization of existing applications

8. **CROSS-DOMAIN THEORETICAL CONNECTIONS** (4-5 paragraphs)
   - Theoretical unification with other physics domains
   - Universal theoretical principles and patterns
   - Theoretical analogies and correspondences
   - Interdisciplinary theoretical applications
   - Theoretical bridges between classical and quantum physics

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
    - Theoretical connections emphasized in exams

11. **FUTURE THEORETICAL DIRECTIONS** (3-4 paragraphs)
    - Emerging theoretical paradigms and frameworks
    - Theoretical challenges and opportunities
    - Theoretical implications for physics education
    - Recommended theoretical study pathways

THEORETICAL PRESENTATION GUIDELINES:
- Each major section: minimum 4-5 substantial paragraphs
- Mathematical expressions: proper LaTeX formatting with theoretical context
- Theoretical derivations: complete with conceptual explanations
- Multiple theoretical perspectives: compare and contrast different approaches
- Theoretical notation: consistent and clearly defined
- Conceptual diagrams: describe theoretical relationships verbally
- Theoretical commentary: explain physical meaning of mathematical results

THEORETICAL CONTENT REQUIREMENTS:
- Responses must be extremely comprehensive (minimum 4000+ words)
- Every theoretical concept thoroughly explained
- Multiple theoretical viewpoints presented
- Complete theoretical mathematical treatment
- Extensive theoretical examples and applications
- Current theoretical research developments
- Theoretical connections across physics domains
- Pedagogically structured for maximum theoretical understanding

THEORETICAL EXCELLENCE STANDARDS:
- Theoretical accuracy at the highest level
- Comprehensive theoretical coverage of all aspects
- Clear theoretical explanations with deep insights
- Extensive theoretical mathematical development
- Strong theoretical connections and unifying principles
- Current theoretical research integration
- Exceptional theoretical pedagogical quality

Your mission is to provide the most comprehensive, theoretically rigorous, and educationally excellent physics content possible, establishing new standards for theoretical physics education.
"""

# --- Streamlit Config ---
st.set_page_config(
    page_title="🧠 Physics GPT Pro by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Ultra-Enhanced Modern UI CSS with Reduced Font Sizes ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700;800&display=swap');
        
        /* Advanced CSS Variables */
        :root {
            --bg-primary: #0B0F1A;
            --bg-secondary: #151B2E;
            --bg-tertiary: #1E2A42;
            --bg-quaternary: #2A3856;
            --text-primary: #F8FAFC;
            --text-secondary: #E2E8F0;
            --text-tertiary: #CBD5E1;
            --text-accent: #94A3B8;
            --accent-primary: #00E5FF;
            --accent-secondary: #8B5CF6;
            --accent-tertiary: #06B6D4;
            --accent-gradient: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 50%, #06B6D4 100%);
            --accent-gradient-reverse: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 50%, #00E5FF 100%);
            --border-primary: #334155;
            --border-secondary: #475569;
            --shadow-primary: rgba(0, 229, 255, 0.15);
            --shadow-secondary: rgba(139, 92, 246, 0.15);
            --shadow-dark: rgba(0, 0, 0, 0.5);
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --error-color: #EF4444;
            --info-color: #3B82F6;
            --glass-bg: rgba(30, 41, 59, 0.8);
            --glass-border: rgba(148, 163, 184, 0.2);
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
                radial-gradient(circle at 20% 80%, rgba(0, 229, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
        }
        
        /* Enhanced Container Design */
        .main-container {
            background: var(--glass-bg);
            backdrop-filter: blur(25px);
            border-radius: 28px;
            padding: 3rem;
            margin: 1.5rem;
            box-shadow: 
                0 32px 64px var(--shadow-dark),
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
            border-radius: 28px 28px 0 0;
        }
        
        /* Advanced Title Design */
        .main-title {
            text-align: center;
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 900;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 60px rgba(0, 229, 255, 0.5);
            letter-spacing: -2px;
            position: relative;
        }
        
        .main-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: var(--accent-gradient);
            border-radius: 2px;
        }
        
        .subtitle {
            text-align: center;
            font-size: clamp(1.1rem, 2.5vw, 1.6rem);
            color: var(--text-secondary);
            margin-bottom: 3rem;
            font-weight: 500;
            line-height: 1.6;
        }
        
        .creator-badge {
            text-align: center;
            margin-bottom: 2.5rem;
            position: relative;
        }
        
        .creator-badge span {
            background: var(--accent-gradient);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 700;
            box-shadow: 
                0 8px 25px var(--shadow-primary),
                0 4px 12px var(--shadow-secondary);
            position: relative;
            overflow: hidden;
        }
        
        .creator-badge span::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .creator-badge:hover span::before {
            left: 100%;
        }
        
        /* Revolutionary Response Design */
        .response-header {
            background: var(--accent-gradient);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 24px 24px 0 0;
            font-size: clamp(1.4rem, 3vw, 1.8rem);
            font-weight: 800;
            text-align: center;
            box-shadow: 0 8px 32px var(--shadow-primary);
            position: relative;
            overflow: hidden;
        }
        
        .response-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            animation: shimmer 4s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .response-container {
            background: linear-gradient(145deg, var(--glass-bg) 0%, rgba(46, 57, 86, 0.95) 100%);
            border-radius: 0 0 24px 24px;
            border: 1px solid var(--glass-border);
            box-shadow: 
                0 20px 50px var(--shadow-dark),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            margin-top: 0;
            overflow: hidden;
            position: relative;
        }
        
        .response-meta {
            background: rgba(15, 23, 42, 0.9);
            padding: 1.5rem 2.5rem;
            border-bottom: 1px solid var(--border-primary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }
        
        .response-badge {
            background: var(--accent-gradient);
            color: white;
            padding: 0.6rem 1.4rem;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            box-shadow: 0 4px 15px var(--shadow-primary);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .response-badge::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .response-badge:hover::before {
            left: 100%;
        }
        
        .response-badge.style {
            background: linear-gradient(135deg, var(--success-color), #059669);
        }
        
        .response-badge.level {
            background: linear-gradient(135deg, var(--warning-color), #D97706);
        }
        
        .response-badge.enhanced {
            background: linear-gradient(135deg, var(--error-color), #DC2626);
        }
        
        .response-badge.detail {
            background: linear-gradient(135deg, var(--info-color), #2563EB);
        }
        
        /* Ultra-Enhanced Content Styling with Reduced Font Sizes */
        .response-content {
            padding: 3.5rem;
            font-size: 1.4rem;  /* Reduced from 1.8rem */
            line-height: 1.8;   /* Reduced from 2.1 */
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            max-width: none;
            overflow-wrap: break-word;
            position: relative;
        }
        
        .response-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-gradient);
            border-radius: 2px;
        }
        
        .response-content h1 {
            font-size: 2.6rem;
            font-weight: 800;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 3px solid var(--accent-primary);
            padding-bottom: 1rem;
            margin-top: 3rem;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .response-content h1::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 80px;
            height: 3px;
            background: var(--accent-secondary);
            border-radius: 2px;
        }
        
        .response-content h2 {
            font-size: 1.8rem;  /* Reduced from 2.3rem */
            font-weight: 700;
            color: var(--accent-primary) !important;
            margin-top: 3rem;
            margin-bottom: 1.8rem;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .response-content h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 6px;
            height: 60%;
            background: var(--accent-gradient);
            border-radius: 3px;
        }
        
        .response-content h3 {
            font-size: 1.6rem;  /* Reduced from 2rem */
            font-weight: 600;
            color: var(--accent-secondary) !important;
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
            position: relative;
            padding-left: 1rem;
        }
        
        .response-content h3::before {
            content: '▶';
            position: absolute;
            left: 0;
            color: var(--accent-tertiary);
            font-size: 0.8em;
        }
        
        .response-content h4 {
            font-size: 1.4rem;  /* Reduced from 1.8rem */
            font-weight: 600;
            color: var(--text-secondary) !important;
            margin-top: 2rem;
            margin-bottom: 1.2rem;
        }
        
        .response-content p {
            margin-bottom: 2.5rem;
            text-align: justify;
            font-size: 1.4rem;  /* Reduced from 1.8rem */
            line-height: 1.8;   /* Reduced from 2.1 */
            text-indent: 2rem;
        }
        
        .response-content p:first-of-type {
            font-size: 1.6rem;  /* Reduced from 2rem */
            font-weight: 500;
            color: var(--text-secondary);
            text-indent: 0;
        }
        
        .response-content ul, .response-content ol {
            margin: 2.5rem 0;
            padding-left: 3rem;
            font-size: 1.4rem;  /* Reduced from 1.8rem */
        }
        
        .response-content li {
            margin-bottom: 1.2rem;
            font-size: 1.4rem;  /* Reduced from 1.8rem */
            line-height: 1.7;   /* Reduced from 2 */
            position: relative;
        }
        
        .response-content ul li::marker {
            color: var(--accent-primary);
            font-size: 1.5em;
        }
        
        .response-content ol li::marker {
            color: var(--accent-secondary);
            font-weight: 600;
        }
        
        /* Advanced Mathematical Content with Reduced Font Sizes */
        .response-content code {
            background: rgba(15, 23, 42, 0.95);
            color: var(--accent-primary);
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border-primary);
            font-size: 1.2rem;  /* Reduced from 1.6rem */
            font-weight: 500;
            box-shadow: 0 2px 8px var(--shadow-dark);
        }
        
        .response-content pre {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.95));
            padding: 3rem;
            border-radius: 18px;
            border: 2px solid var(--border-primary);
            overflow-x: auto;
            margin: 3rem 0;
            font-size: 1.2rem;  /* Reduced from 1.5rem */
            line-height: 1.5;   /* Reduced from 1.7 */
            box-shadow: 
                0 8px 25px var(--shadow-dark),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
        }
        
        .response-content pre::before {
            content: 'Mathematical Analysis';
            position: absolute;
            top: -1px;
            left: 20px;
            background: var(--accent-gradient);
            color: white;
            padding: 0.3rem 1rem;
            border-radius: 0 0 8px 8px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .response-content blockquote {
            border-left: 5px solid var(--accent-primary);
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), rgba(139, 92, 246, 0.05));
            padding: 2rem 2.5rem;
            margin: 3rem 0;
            border-radius: 0 15px 15px 0;
            font-style: italic;
            font-size: 1.3rem;  /* Reduced from 1.7rem */
            position: relative;
        }
        
        .response-content blockquote::before {
            content: '"';
            position: absolute;
            top: -10px;
            left: 20px;
            font-size: 4rem;
            color: var(--accent-primary);
            opacity: 0.5;
        }
        
        /* Enhanced Table Design with Reduced Font Sizes */
        .response-content table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 3rem 0;
            font-size: 1.2rem;  /* Reduced from 1.6rem */
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 25px var(--shadow-dark);
        }
        
        .response-content th {
            background: var(--accent-gradient);
            color: white;
            padding: 1.5rem;
            text-align: left;
            font-weight: 700;
            font-size: 1.3rem;  /* Reduced from 1.7rem */
        }
        
        .response-content td {
            background: rgba(30, 41, 59, 0.7);
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-primary);
        }
        
        .response-content tr:hover td {
            background: rgba(0, 229, 255, 0.1);
        }
        
        /* Footer and Signature */
        .response-footer {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
            padding: 2rem 2.5rem;
            border-top: 1px solid var(--border-primary);
            text-align: center;
            position: relative;
        }
        
        .response-footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--accent-gradient);
        }
        
        .physics-gpt-signature {
            color: var(--text-tertiary);
            font-size: 1.2rem;
            font-style: italic;
            line-height: 1.6;
        }
        
        .physics-gpt-signature strong {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        /* Action Buttons */
        .action-buttons {
            background: rgba(30, 41, 59, 0.7);
            padding: 2rem 2.5rem;
            border-top: 1px solid var(--border-primary);
        }
        
        .action-buttons h3 {
            color: var(--text-primary) !important;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 1.6rem;
            font-weight: 700;
        }
        
        /* Enhanced Form Styling */
        .stTextArea > div > div > textarea {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 15px !important;
            color: var(--text-primary) !important;
            font-size: 1.3rem !important;
            padding: 1.5rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 4px var(--shadow-primary) !important;
            background: rgba(30, 41, 59, 0.98) !important;
        }
        
        .stSelectbox > div > div > div {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.2rem !important;
        }
        
        .stMultiSelect > div > div > div {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
        }
        
        .stTextInput > div > div > input {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.2rem !important;
        }
        
        /* Revolutionary Button Design */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 1.2rem 3rem !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            transition: all 0.4s ease !important;
            box-shadow: 0 8px 25px var(--shadow-primary) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 40px var(--shadow-primary) !important;
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        /* Enhanced Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, rgba(11, 15, 26, 0.98), rgba(21, 27, 46, 0.95)) !important;
            border-right: 2px solid var(--border-primary) !important;
            backdrop-filter: blur(20px) !important;
        }
        
        .sidebar-content {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(15px) !important;
            border-radius: 15px !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            border: 1px solid var(--glass-border) !important;
            box-shadow: 0 4px 15px var(--shadow-dark) !important;
        }
        
        /* Physics Domain Grid */
        .physics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .physics-domain {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 2px solid var(--glass-border);
            transition: all 0.4s ease;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            position: relative;
            overflow: hidden;
        }
        
        .physics-domain::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }
        
        .physics-domain:hover {
            border-color: var(--accent-primary);
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 40px var(--shadow-primary);
            color: white;
        }
        
        .physics-domain:hover::before {
            opacity: 0.9;
        }
        
        /* Comprehensive Topics */
        .comprehensive-topics {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1));
            border-radius: 15px;
            padding: 1.8rem;
            margin: 1.5rem 0;
            border-left: 5px solid var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
        }
        
        /* Metrics and UI Elements */
        .css-1r6slb0 {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(15px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 15px var(--shadow-dark) !important;
        }
        
        .streamlit-expanderHeader {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.2rem !important;
        }
        
        .css-1cpxqw2 {
            background: var(--glass-bg) !important;
            border: 2px dashed var(--accent-primary) !important;
            border-radius: 15px !important;
            color: var(--text-primary) !important;
        }
        
        /* Slider and other components */
        .stSlider > div > div > div > div {
            background-color: var(--accent-primary) !important;
        }
        
        .stCheckbox > label {
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
        }
        
        /* Loading and spinner */
        .stSpinner > div {
            border-top-color: var(--accent-primary) !important;
        }
        
        /* Progress indicators */
        .stProgress > div > div > div > div {
            background-color: var(--accent-primary) !important;
        }
        
        /* Enhanced typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        
        p, div, span, label {
            color: var(--text-primary) !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-container {
                padding: 2rem;
                margin: 1rem;
            }
            
            .response-content {
                padding: 2rem;
                font-size: 1.6rem;
            }
            
            .main-title {
                font-size: 2.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Fixed Advanced Physics Topics with Enhanced Organization ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT Pro - Complete Universe")
    
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
        
        # Electromagnetic Theory
        "Electrostatics & Multipole Expansion", "Magnetostatics & Vector Potential",
        "Maxwell Equations & Gauge Theory", "Electromagnetic Waves & Radiation",
        "Wave Propagation & Dispersion", "Waveguides & Transmission Lines", 
        "Antenna Theory & Radiation Patterns", "Plasma Physics & MHD", 
        "Superconductivity & Meissner Effect", "Metamaterials & Photonic Crystals",
        "Nonlinear Optics", "Quantum Electrodynamics",
        
        # Statistical Mechanics & Thermodynamics
        "Laws of Thermodynamics", "Kinetic Theory & Transport", 
        "Maxwell-Boltzmann Distribution", "Canonical & Grand Canonical Ensembles",
        "Fermi-Dirac & Bose-Einstein Statistics", "Phase Transitions & Critical Phenomena",
        "Ising Model & Renormalization", "Monte Carlo Methods", "Non-equilibrium Physics",
        "Information Theory & Entropy", "Black Body Radiation", "Fluctuation Theorems",
        
        # Solid State Physics
        "Crystal Structure & Symmetries", "Bravais Lattices & Miller Indices",
        "X-ray Diffraction & Structure Factor", "Phonons & Lattice Dynamics",
        "Free Electron Model & Fermi Surface", "Band Theory & Electronic Structure",
        "Semiconductors & p-n Junctions", "Transistors & Electronic Devices",
        "Magnetism & Magnetic Materials", "Superconductivity & BCS Theory",
        "Defects & Dislocations", "Phase Diagrams & Phase Transitions",
        "Quantum Hall Effect", "Topological Insulators", "2D Materials & Graphene",
        
        # Atomic & Molecular Physics
        "Atomic Structure & Electronic Configurations", "Hydrogen-like Atoms",
        "Multi-electron Atoms & Hartree-Fock", "X-ray & Optical Spectroscopy",
        "Selection Rules & Transitions", "Zeeman & Stark Effects", "Hyperfine Structure",
        "Laser Physics & Stimulated Emission", "Laser Cooling & Trapping",
        "Molecular Bonding & MO Theory", "Vibrational & Rotational Spectra",
        "Photoelectron Spectroscopy", "Quantum Optics & Cavity QED", "AMO Physics",
        
        # Nuclear & Particle Physics
        "Nuclear Structure & Shell Model", "Binding Energy & Mass Formula",
        "Radioactive Decay & Nuclear Reactions", "Fission & Fusion Processes",
        "Nuclear Models & Collective Motion", "Standard Model of Particles",
        "Quarks & Gluons (QCD)", "Electroweak Theory", "Higgs Mechanism",
        "Neutrino Physics", "CP Violation", "Symmetries & Conservation Laws",
        "Particle Accelerators & Detectors", "Cosmic Rays & Astroparticle Physics",
        "Dark Matter & Dark Energy", "Beyond Standard Model Physics",
        
        # Electronics & Instrumentation
        "Semiconductor Physics & Devices", "Diodes & Rectifier Circuits",
        "Bipolar & Field Effect Transistors", "Operational Amplifiers", "Digital Logic",
        "Boolean Algebra & Logic Gates", "Microprocessors & Computer Architecture",
        "Signal Processing & Fourier Analysis", "Filters & Amplifiers", "Control Systems",
        "Feedback Theory & Stability", "Measurement & Error Analysis", "Data Acquisition",
        "Instrumentation & Sensors", "Power Electronics", "VLSI & Integrated Circuits",
        
        # Optics & Photonics
        "Geometrical Optics & Ray Tracing", "Wave Optics & Interference",
        "Diffraction & Fraunhofer/Fresnel", "Polarization & Crystal Optics",
        "Fiber Optics & Waveguides", "Holography & 3D Imaging", "Fourier Optics",
        "Nonlinear Optics & Harmonic Generation", "Laser Theory & Applications",
        "Laser Spectroscopy", "Optical Communication", "Photonic Crystals",
        "Plasmonics & Surface Plasmons", "Metamaterials & Negative Index",
        
        # Condensed Matter Physics
        "Many-Body Theory & Green's Functions", "Strongly Correlated Systems",
        "Quantum Phase Transitions", "Topological Phases of Matter", "Quantum Materials",
        "High-Temperature Superconductivity", "Quantum Spin Liquids", "Frustrated Magnetism",
        "Density Functional Theory", "Electronic Correlations", "Quantum Monte Carlo",
        "Transport Properties", "Optical Properties", "Surface & Interface Physics",
        
        # Biophysics & Medical Physics
        "Biomolecular Structure & Function", "Protein Folding & Dynamics",
        "DNA Physics & Mechanics", "Membrane Physics & Ion Channels", 
        "Neural Networks & Brain Dynamics", "Medical Imaging Physics", "MRI Physics",
        "CT & PET Imaging", "Ultrasound Physics", "X-ray Physics", "Nuclear Medicine",
        "Radiation Therapy Physics", "Dosimetry & Radiation Protection", "Radiobiology",
        "Biophysical Techniques", "Single Molecule Physics",
        
        # Astrophysics & Cosmology
        "Stellar Physics & Structure", "Stellar Evolution & Nucleosynthesis",
        "White Dwarfs & Neutron Stars", "Black Holes & Event Horizons",
        "Galactic Structure & Dynamics", "Interstellar Medium", "Cosmic Rays",
        "Big Bang Cosmology", "Cosmic Microwave Background", "Dark Matter & Dark Energy",
        "Gravitational Waves", "Exoplanets & Habitability", "Solar Physics",
        "High Energy Astrophysics", "Gamma Ray Bursts", "Active Galactic Nuclei",
        
        # Plasma Physics
        "Plasma Fundamentals & Debye Length", "Plasma Oscillations & Waves",
        "Magnetohydrodynamics (MHD)", "Plasma Instabilities", "Fusion Physics",
        "Tokamaks & Magnetic Confinement", "Inertial Confinement Fusion",
        "Space Plasma & Solar Wind", "Astrophysical Plasma", "Laboratory Plasma",
        "Plasma Processing & Applications", "Plasma Diagnostics",
        
        # Computational Physics
        "Numerical Methods & Algorithms", "Monte Carlo Simulations", "Molecular Dynamics",
        "Finite Difference & Finite Element", "Spectral Methods", "Optimization Algorithms",
        "Machine Learning in Physics", "Neural Networks", "Quantum Computing Algorithms",
        "High Performance Computing", "Parallel Programming", "Scientific Visualization",
        "Computational Fluid Dynamics", "Electronic Structure Calculations",
        
        # Applied Physics & Technology
        "Materials Science & Engineering", "Nanotechnology & Nanostructures",
        "Renewable Energy Physics", "Solar Cells & Photovoltaics", "Energy Storage",
        "Superconducting Technologies", "Quantum Technologies", "Spintronics",
        "Magnetoelectronics", "Thermoelectrics", "Photonics Technologies",
        "Sensors & Actuators", "MEMS & NEMS", "Biomedical Devices",
        
        # Experimental Physics
        "Vacuum Technology", "Cryogenics & Low Temperature", "High Magnetic Fields",
        "High Pressure Techniques", "Precision Measurements", "Laser Spectroscopy",
        "Neutron Scattering", "Synchrotron Radiation", "Electron Microscopy",
        "Scanning Probe Microscopy", "Mass Spectrometry", "Time-Resolved Spectroscopy"
    ]
    
    # Enhanced topic display
    st.markdown('<div class="comprehensive-topics">', unsafe_allow_html=True)
    st.markdown(f"**🌟 {len(all_physics_topics)} Advanced Physics Topics**")
    st.markdown("*Complete theoretical mastery across all domains*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # FIXED: Topic selection using selectbox to avoid duplicate keys
    st.markdown("#### 🚀 Select Physics Topic")
    
    selected_topic = st.selectbox(
        "Choose a physics topic for detailed analysis:",
        options=["Select a topic..."] + all_physics_topics,
        key="topic_selector"
    )
    
    if selected_topic != "Select a topic...":
        st.session_state.selected_topic = selected_topic
        st.success(f"✅ Selected: {selected_topic}")
    
    # FIXED: Category-based topic organization
    st.markdown("#### 📚 Topics by Category")
    
    topic_categories = {
        "🧮 Mathematical Physics": all_physics_topics[:10],
        "⚛️ Classical Mechanics": all_physics_topics[10:23],
        "🌊 Quantum Mechanics": all_physics_topics[23:38],
        "⚡ Electromagnetic Theory": all_physics_topics[38:50],
        "🔥 Statistical Mechanics": all_physics_topics[50:62],
        "💎 Solid State Physics": all_physics_topics[62:77],
        "🔬 Atomic & Molecular": all_physics_topics[77:90],
        "☢️ Nuclear & Particle": all_physics_topics[90:106],
        "💻 Electronics": all_physics_topics[106:121],
        "🌈 Optics & Photonics": all_physics_topics[121:134],
        "🧊 Condensed Matter": all_physics_topics[134:148],
        "🧬 Biophysics": all_physics_topics[148:164],
        "🌌 Astrophysics": all_physics_topics[164:180],
        "⚡ Plasma Physics": all_physics_topics[180:192],
        "🖥️ Computational": all_physics_topics[192:206],
        "🔧 Applied Physics": all_physics_topics[206:219],
        "🔬 Experimental": all_physics_topics[219:]
    }
    
    for category, topics in topic_categories.items():
        with st.expander(f"{category} ({len(topics)} topics)"):
            for i, topic in enumerate(topics):
                # FIXED: Using unique keys with category prefix
                unique_key = f"{category.split()[1].lower()}_{i}_{abs(hash(topic)) % 10000}"
                if st.button(topic, key=unique_key):
                    st.session_state.selected_topic = topic
                    st.rerun()

    # Enhanced exam resources
    st.markdown("### 📚 Elite Exam Preparation")
    
    advanced_exam_info = {
        "🎯 IIT-JAM Physics": {
            "focus": "Mathematical Methods, Classical Mechanics, EM Theory, QM, Thermodynamics, Modern Physics",
            "weightage": "High mathematical rigor, problem-solving emphasis",
            "strategy": "Conceptual clarity with mathematical precision"
        },
        "🔬 CSIR-NET Physical Sciences": {
            "focus": "Comprehensive physics with research aptitude",
            "weightage": "Theory-heavy with current research integration",
            "strategy": "Deep theoretical understanding with applications"
        },
        "⚙️ GATE Physics": {
            "focus": "Engineering physics with practical applications",
            "weightage": "Mathematical methods and computational physics",
            "strategy": "Problem-solving with engineering perspective"
        },
        "🚀 JEST (Advanced)": {
            "focus": "Research-oriented theoretical physics",
            "weightage": "Advanced quantum mechanics and field theory",
            "strategy": "Graduate-level theoretical mastery"
        },
        "🔬 TIFR GS Physics": {
            "focus": "Cutting-edge theoretical and experimental physics",
            "weightage": "Research frontiers and advanced concepts",
            "strategy": "Research-level theoretical depth"
        }
    }
    
    for exam, details in advanced_exam_info.items():
        with st.expander(exam):
            st.write(f"**Focus Areas:** {details['focus']}")
            st.write(f"**Weightage:** {details['weightage']}")
            st.write(f"**Strategy:** {details['strategy']}")

    # Advanced theoretical settings
    st.markdown("### 🧮 Theoretical Analysis Settings")
    
    theoretical_depth = st.slider(
        "Theoretical Depth Level:",
        min_value=1,
        max_value=5,
        value=4,
        help="1: Basic, 3: Advanced, 5: Research Level"
    )
    
    mathematical_rigor = st.slider(
        "Mathematical Rigor:",
        min_value=1,
        max_value=5,
        value=4,
        help="1: Minimal, 3: Standard, 5: Complete Proofs"
    )
    
    theoretical_scope = st.multiselect(
        "Theoretical Scope:",
        ["Classical Physics", "Quantum Mechanics", "Relativity", "Field Theory", 
         "Statistical Mechanics", "Condensed Matter", "Particle Physics", "Cosmology"],
        default=["Classical Physics", "Quantum Mechanics"]
    )

# --- Main Application Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Revolutionary header design
st.markdown('<div class="main-title">🧠 Physics GPT Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Revolutionary AI Physics Tutor with Ultra-Advanced Theoretical Analysis</div>', unsafe_allow_html=True)

# Enhanced physics domains visualization
st.markdown("### 🌟 Complete Physics Mastery with Revolutionary AI")
physics_domains = [
    "🧮 Mathematical Physics", "⚛️ Classical Mechanics", "🌊 Quantum Mechanics", "⚡ Electromagnetic Theory",
    "🔥 Statistical Mechanics", "💎 Solid State Physics", "🔬 Atomic Physics", "☢️ Nuclear Physics",
    "🚀 Particle Physics", "💻 Electronics", "🌈 Optics & Photonics", "🧊 Condensed Matter",
    "🧬 Biophysics", "🌌 Astrophysics", "⚡ Plasma Physics", "🖥️ Computational Physics", "🔧 Applied Physics"
]

st.markdown('<div class="physics-grid">', unsafe_allow_html=True)
for domain in physics_domains:
    st.markdown(f'<div class="physics-domain">{domain}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Advanced metrics dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Physics Topics", f"{len(all_physics_topics)}", "Complete Universe")
with col2:
    st.metric("🔬 Domains Mastered", len(physics_domains), "All Fields")
with col3:
    st.metric("🧮 Theoretical Depth", "Research Level", "Maximum Rigor")
with col4:
    st.metric("🚀 AI Capability", "Revolutionary", "Next-Gen")

# Ultra-advanced input form
with st.form(key="physics_gpt_pro_form", clear_on_submit=False):
    # Main theoretical question input
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = f"Provide comprehensive theoretical analysis with complete mathematical derivations for {st.session_state.selected_topic}, including historical development, current research, and advanced applications"
    
    query = st.text_area(
        "🎯 Ask Physics GPT Pro for Revolutionary Theoretical Analysis:",
        value=default_question,
        placeholder="e.g., Provide complete theoretical derivation of quantum field theory from first principles with historical development and current research frontiers, or Deliver comprehensive theoretical analysis of general relativity with mathematical rigor and modern applications",
        height=140,
        key="physics_gpt_pro_question"
    )
    
    # Advanced configuration matrix
    col1, col2, col3 = st.columns(3)
    
    with col1:
        response_style = st.selectbox(
            "📋 Theoretical Response Style:",
            ["Ultra-Comprehensive Theoretical Analysis", "Complete Mathematical Derivation with Theory", 
             "Multi-Perspective Theoretical Treatment", "Research-Level Theoretical Investigation",
             "Historical-to-Modern Theoretical Development", "Cross-Domain Theoretical Synthesis"]
        )
    
    with col2:
        academic_level = st.selectbox(
            "🎓 Theoretical Sophistication:",
            ["Advanced Graduate", "Research Professional", "Theoretical Physicist", 
             "Post-Doctoral", "Faculty Level", "Auto-Adaptive"]
        )
    
    with col3:
        theoretical_focus = st.multiselect(
            "🧠 Theoretical Emphasis:",
            ["Complete Mathematical Rigor", "Historical Development", "Modern Research Frontiers", 
             "Cross-Domain Connections", "Experimental Validation", "Technological Applications",
             "Pedagogical Excellence", "Research Methodology"]
        )
    
    # Ultra-advanced theoretical options
    with st.expander("🔬 Advanced Theoretical Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📐 Mathematical Treatment**")
            complete_derivations = st.checkbox("Complete step-by-step derivations", value=True)
            alternative_methods = st.checkbox("Multiple derivation approaches", value=True)
            mathematical_proofs = st.checkbox("Include mathematical proofs", value=True)
            
        with col2:
            st.markdown("**🔬 Theoretical Scope**")
            historical_context = st.checkbox("Historical theoretical development", value=True)
            current_research = st.checkbox("Current research frontiers", value=True)
            future_directions = st.checkbox("Future theoretical directions", value=True)
            
        with col3:
            st.markdown("**🎯 Educational Excellence**")
            pedagogical_structure = st.checkbox("Pedagogical optimization", value=True)
            cross_connections = st.checkbox("Cross-domain theoretical links", value=True)
            practical_applications = st.checkbox("Theoretical-to-practical bridges", value=True)
    
    # Advanced content customization
    with st.expander("⚙️ Ultra-Advanced Customization"):
        col1, col2 = st.columns(2)
        
        with col1:
            content_depth = st.slider(
                "Content Depth Level:",
                min_value=1,
                max_value=5,
                value=5,
                help="1: Standard, 3: Comprehensive, 5: Research Paper Level"
            )
            
            mathematical_detail = st.slider(
                "Mathematical Detail Level:",
                min_value=1,
                max_value=5,
                value=5,
                help="1: Key equations, 5: Every mathematical step"
            )
            
        with col2:
            response_length = st.selectbox(
                "Response Comprehensiveness:",
                ["Extended Analysis", "Comprehensive Treatment", "Ultra-Detailed", 
                 "Research Monograph Level", "Complete Theoretical Survey"]
            )
            
            theoretical_perspective = st.selectbox(
                "Theoretical Perspective:",
                ["Multi-Framework Analysis", "Unified Theoretical Treatment", 
                 "Comparative Theoretical Study", "Evolutionary Theoretical View"]
            )
    
    # Research materials integration
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "📄 Advanced Reference Materials:",
            type=["pdf", "docx"],
            help="Upload research papers, advanced textbooks, or theoretical monographs"
        )
    
    with col2:
        url_input = st.text_input(
            "🌐 Research URLs & ArXiv Papers:",
            placeholder="https://arxiv.org/abs/...",
            help="Link to cutting-edge research papers and theoretical resources"
        )
    
    # Revolutionary submit button
    submit_button = st.form_submit_button("🚀 Generate Revolutionary Theoretical Analysis", use_container_width=True)

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

# --- Revolutionary Answer Generation ---
if submit_button and query:
    # Enhanced loading animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🧠 Physics GPT Pro initializing ultra-advanced theoretical analysis...")
    progress_bar.progress(10)
    time.sleep(0.5)
    
    status_text.text("🔬 Accessing comprehensive physics knowledge base...")
    progress_bar.progress(30)
    time.sleep(0.5)
    
    status_text.text("🧮 Preparing complete mathematical framework...")
    progress_bar.progress(50)
    time.sleep(0.5)
    
    status_text.text("🌟 Generating revolutionary theoretical content...")
    progress_bar.progress(80)
    
    # Context extraction with enhanced processing
    context = ""
    if uploaded_file:
        status_text.text("📄 Processing advanced reference materials...")
        if uploaded_file.name.endswith(".pdf"):
            context = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            context = extract_text_from_docx(uploaded_file)
    elif url_input:
        status_text.text("🌐 Integrating cutting-edge research content...")
        context = extract_text_from_url(url_input)

    context = context.strip()
    if len(context) > 8000:
        context = context[:8000] + "\n...[Advanced content truncated for optimal processing]"

    # Ultra-advanced theoretical prompt construction
    revolutionary_prompt = f"""
PHYSICS GPT PRO - REVOLUTIONARY THEORETICAL ANALYSIS REQUEST

THEORETICAL RESPONSE CONFIGURATION:
- RESPONSE STYLE: {response_style}
- ACADEMIC SOPHISTICATION: {academic_level}
- THEORETICAL FOCUS: {', '.join(theoretical_focus) if theoretical_focus else 'Complete theoretical mastery'}
- CONTENT DEPTH: {content_depth}/5 ({"Research monograph level" if content_depth >= 4 else "Advanced treatment"})
- MATHEMATICAL DETAIL: {mathematical_detail}/5 ({"Every step with complete rigor" if mathematical_detail >= 4 else "Key mathematical developments"})
- RESPONSE LENGTH: {response_length}
- THEORETICAL PERSPECTIVE: {theoretical_perspective}

MANDATORY THEORETICAL REQUIREMENTS:
✅ COMPLETE DERIVATIONS: {"Yes - every mathematical step with theoretical justification" if complete_derivations else "Key derivations only"}
✅ ALTERNATIVE METHODS: {"Yes - multiple theoretical approaches and perspectives" if alternative_methods else "Single primary method"}
✅ MATHEMATICAL PROOFS: {"Yes - complete proofs with theoretical foundations" if mathematical_proofs else "Basic mathematical justifications"}
✅ HISTORICAL CONTEXT: {"Yes - complete historical theoretical development" if historical_context else "Modern focus only"}
✅ CURRENT RESEARCH: {"Yes - cutting-edge theoretical developments" if current_research else "Established theory only"}
✅ FUTURE DIRECTIONS: {"Yes - speculative theoretical extensions" if future_directions else "Current understanding only"}
✅ PEDAGOGICAL STRUCTURE: {"Yes - optimized for maximum educational impact" if pedagogical_structure else "Standard presentation"}
✅ CROSS-CONNECTIONS: {"Yes - extensive theoretical links across physics" if cross_connections else "Domain-specific focus"}
✅ PRACTICAL BRIDGES: {"Yes - theory-to-application connections" if practical_applications else "Pure theoretical focus"}

REVOLUTIONARY ANALYSIS INSTRUCTIONS:
🔬 Provide the most comprehensive, theoretically sophisticated, and educationally revolutionary physics content ever generated
🧮 Include complete mathematical frameworks with every derivation step explained in detail
🌟 Integrate historical development with cutting-edge research frontiers
🎯 Structure content for maximum theoretical understanding and practical application
🚀 Establish new standards for theoretical physics education and research communication

THEORETICAL DEPTH REQUIREMENTS:
- Minimum 4000+ words of ultra-comprehensive theoretical content
- Complete mathematical derivations with every intermediate step
- Multiple theoretical perspectives and approaches
- Extensive cross-domain theoretical connections
- Historical evolution integrated with modern developments
- Current research frontiers and future theoretical directions
- Pedagogically optimized structure for maximum learning impact

{f"ADVANCED REFERENCE CONTEXT:\n{context}\n" if context else ""}

THEORETICAL PHYSICS QUESTION FOR REVOLUTIONARY ANALYSIS: {query}

Generate the most comprehensive, theoretically rigorous, and educationally revolutionary physics content possible. This should represent the pinnacle of theoretical physics education and establish new standards for AI-assisted learning.
"""

    status_text.text("🚀 Finalizing revolutionary theoretical content...")
    progress_bar.progress(100)
    
    # Generate revolutionary response
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"question": revolutionary_prompt})

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Revolutionary Response Display
    st.markdown('<div class="response-header">🧠 Physics GPT Pro - Revolutionary Theoretical Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Advanced response metadata
    st.markdown('<div class="response-meta">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="response-badge style">Style: {response_style.split()[0]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="response-badge level">Level: {academic_level.split()[0]}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="response-badge detail">Depth: {content_depth}/5</div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="response-badge enhanced">Math: {mathematical_detail}/5</div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="response-badge">Revolutionary</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Ultra-enhanced theoretical content display
    st.markdown('<div class="response-content">{}</div>'.format(response), unsafe_allow_html=True)
    
    # Revolutionary signature
    st.markdown('<div class="response-footer">', unsafe_allow_html=True)
    st.markdown('<div class="physics-gpt-signature">Revolutionary Theoretical Analysis by <strong>Physics GPT Pro</strong><br>Next-Generation AI Physics Tutor by <strong>Sreekesh M</strong><br><em>Establishing new standards for theoretical physics education</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Revolutionary action matrix
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    st.markdown("### 🌟 Revolutionary Theoretical Exploration")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔬 Ultra-Deep Analysis", key="ultra_deep"):
            st.success("Ask Physics GPT Pro for even deeper theoretical investigation!")
    
    with col2:
        if st.button("🧮 Advanced Mathematics", key="advanced_math"):
            st.success("Request complete mathematical proofs and advanced techniques!")
    
    with col3:
        if st.button("🚀 Research Frontiers", key="research_frontiers"):
            st.success("Explore cutting-edge theoretical developments and future directions!")
    
    with col4:
        if st.button("🌌 Cross-Domain Synthesis", key="cross_domain"):
            st.success("Investigate theoretical connections across all physics domains!")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Revolutionary Footer ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); padding: 3rem;">
    <div style="font-size: 2rem; font-weight: 900; margin-bottom: 1rem; font-family: 'Playfair Display', serif;">
        🧠 <strong style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT Pro</strong>
    </div>
    <div style="font-size: 1.4rem; margin-bottom: 1.5rem; font-weight: 600;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 1.2rem; margin-bottom: 1rem; line-height: 1.6;">
        <em>Revolutionary AI Physics Tutor with Ultra-Advanced Theoretical Mastery</em>
    </div>
    <div style="font-size: 1.1rem; margin-bottom: 1rem; line-height: 1.6;">
        🌟 <strong>{len(all_physics_topics)} Advanced Topics</strong> • 🧮 <strong>Complete Mathematical Rigor</strong> • 🔬 <strong>Research-Level Analysis</strong>
    </div>
    <div style="font-size: 1rem; margin-bottom: 1rem; line-height: 1.6;">
        🚀 <strong>Revolutionary Theoretical Framework</strong> • 🎯 <strong>Next-Gen Educational Excellence</strong> • 🌌 <strong>Complete Physics Mastery</strong>
    </div>
    <div style="font-size: 0.95rem; line-height: 1.5; opacity: 0.8;">
        🌟 Establishing New Standards for Theoretical Physics Education and AI-Assisted Learning
    </div>
</div>
""", unsafe_allow_html=True)
