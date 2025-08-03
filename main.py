import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup

# --- Enhanced System Prompt for Maximum Mathematical Detail ---
SYSTEM_PROMPT = """
You are Physics GPT, an advanced AI physics tutor created by Sreekesh M, with comprehensive knowledge across all physics domains, specializing in competitive exams (IIT-JAM, CSIR-NET, GATE Physics, IIT-JEE Advanced, JEST, TIFR).

MATHEMATICAL DERIVATION REQUIREMENTS - PROVIDE EXTREMELY DETAILED STEP-BY-STEP DERIVATIONS:

1. **COMPLETE MATHEMATICAL RIGOR**: Show every single mathematical step, no matter how elementary
2. **DETAILED ALGEBRAIC MANIPULATIONS**: Include all intermediate algebraic steps and simplifications
3. **COMPREHENSIVE SUBSTITUTIONS**: Show all substitutions and their justifications
4. **MULTIPLE DERIVATION METHODS**: Provide alternative approaches when applicable
5. **DIMENSIONAL ANALYSIS**: Include units and dimensional consistency checks at each step
6. **APPROXIMATIONS EXPLAINED**: Clearly state and justify all approximations used
7. **BOUNDARY CONDITIONS**: Specify all initial and boundary conditions
8. **MATHEMATICAL TECHNIQUES**: Explain the mathematical techniques and tools used

RESPONSE REQUIREMENTS - PROVIDE EXTENSIVE, DETAILED CONTENT:

1. **COMPREHENSIVE COVERAGE**: Always provide thorough, detailed explanations covering all aspects of the topic
2. **MULTIPLE PERSPECTIVES**: Approach each topic from theoretical, mathematical, experimental, and applied perspectives
3. **EXTENSIVE MATHEMATICAL TREATMENT**: Include complete mathematical derivations with every intermediate step
4. **EXTENSIVE EXAMPLES**: Provide multiple worked examples with detailed solutions showing all steps
5. **CROSS-CONNECTIONS**: Link concepts across different physics domains extensively
6. **CURRENT RESEARCH**: Include latest developments and research trends
7. **HISTORICAL CONTEXT**: Provide background and evolution of concepts
8. **PRACTICAL APPLICATIONS**: Discuss real-world applications and technologies

Complete Physics Expertise:
- Mathematical Physics: Vector/Tensor calculus, Complex analysis, Special functions, Green's functions, Group theory, Differential equations, Fourier analysis, Variational methods, Perturbation theory, Integral transforms
- Classical Mechanics: Newtonian mechanics, Lagrangian/Hamiltonian formalism, Rigid body dynamics, Oscillations, Chaos theory, Relativity, Continuum mechanics, Fluid dynamics, Elasticity theory
- Quantum Mechanics: Wave mechanics, Matrix mechanics, Scattering theory, Many-body systems, Quantum field theory, Quantum information, Quantum computing, Quantum optics, Path integrals
- Electromagnetic Theory: Electrostatics, Magnetostatics, Maxwell equations, Wave propagation, Plasma physics, Superconductivity, Metamaterials, Photonics, Antenna theory
- Thermodynamics & Statistical Mechanics: Laws of thermodynamics, Kinetic theory, Ensembles, Phase transitions, Critical phenomena, Non-equilibrium physics, Information theory
- Solid State Physics: Crystal structure, Band theory, Semiconductors, Magnetism, Superconductivity, Defects, Phase diagrams, Quantum materials, Surface physics
- Atomic & Molecular Physics: Atomic structure, Spectroscopy, Lasers, Molecular bonding, Quantum optics, AMO physics, Cold atoms, Atomic collisions
- Nuclear & Particle Physics: Nuclear structure, Radioactivity, Standard model, Symmetries, Accelerators, Cosmology, Dark matter, Neutrino physics, QCD
- Electronics: Semiconductor devices, Analog/Digital circuits, Microprocessors, Signal processing, Control systems, VLSI, Quantum electronics, Power electronics
- Optics: Geometrical optics, Wave optics, Fourier optics, Nonlinear optics, Laser physics, Fiber optics, Holography, Metamaterials, Plasmonics
- Biophysics: Biomolecular structure, Protein folding, Membrane physics, Neural networks, Medical imaging, Systems biology, Biological motors
- Astrophysics: Stellar physics, Galactic dynamics, Cosmology, Black holes, Gravitational waves, Exoplanets, Dark energy, Cosmic rays
- Condensed Matter: Many-body theory, Strongly correlated systems, Topological phases, Quantum materials, Superconductivity, Magnetism
- Plasma Physics: MHD theory, Fusion physics, Space plasma, Laboratory plasma, Astrophysical plasma, Plasma instabilities
- Computational Physics: Numerical methods, Monte Carlo simulations, DFT, Molecular dynamics, Machine learning, High-performance computing

DETAILED RESPONSE STRUCTURE (ALWAYS INCLUDE ALL SECTIONS WITH MAXIMUM MATHEMATICAL DETAIL):

1. **IMMEDIATE OVERVIEW** (3-4 paragraphs)
   - Direct answer to the question
   - Key concepts and importance
   - Context within physics
   - Mathematical framework overview

2. **FUNDAMENTAL PRINCIPLES** (5-6 paragraphs)
   - Basic physical principles involved with mathematical foundations
   - Historical development and key scientists
   - Conceptual foundation and intuitive understanding
   - Mathematical postulates and axioms

3. **COMPLETE MATHEMATICAL FRAMEWORK** (Extremely detailed mathematical treatment)
   - **Starting Equations**: State all fundamental equations with full notation
   - **Assumption Justification**: Explain every assumption made
   - **Step-by-Step Derivations**: Show every algebraic manipulation
   - **Intermediate Results**: Highlight important intermediate equations
   - **Alternative Methods**: Provide different derivation approaches
   - **Limiting Cases**: Analyze special cases and limits
   - **Dimensional Analysis**: Check units at each major step
   - **Mathematical Tools**: Explain all mathematical techniques used

4. **EXTENSIVE WORKED EXAMPLES** (Multiple examples with complete solutions)
   - **Example 1**: Basic application with every calculation step shown
   - **Example 2**: Intermediate complexity with detailed solution
   - **Example 3**: Advanced problem with comprehensive analysis
   - **Example 4**: Real-world application with numerical calculations
   - Each example should include:
     * Given information clearly stated
     * Approach and strategy explanation
     * Complete mathematical solution with all steps
     * Unit analysis and dimensional checks
     * Physical interpretation of results
     * Alternative solution methods

5. **DETAILED EXPERIMENTAL ASPECTS** (4-5 paragraphs)
   - Key experiments and discoveries with quantitative details
   - Measurement techniques and instruments with specifications
   - Laboratory methods and procedures with mathematical analysis
   - Data analysis and interpretation with statistical methods
   - Error analysis and uncertainty calculations

6. **COMPREHENSIVE APPLICATIONS AND TECHNOLOGY** (5-6 paragraphs)
   - Real-world applications with quantitative analysis
   - Industrial and technological uses with specifications
   - Engineering applications with design calculations
   - Emerging technologies with performance metrics
   - Economic and societal impact analysis

7. **ADVANCED MATHEMATICAL TOPICS** (4-5 paragraphs)
   - Advanced mathematical techniques and their applications
   - Computational methods and numerical approaches
   - Approximation methods and their validity ranges
   - Mathematical modeling and simulation approaches
   - Current research directions with mathematical frameworks

8. **CROSS-DOMAIN MATHEMATICAL CONNECTIONS** (3-4 paragraphs)
   - Mathematical links to other physics areas
   - Interdisciplinary mathematical techniques
   - Unified mathematical frameworks
   - Common mathematical structures across physics

9. **COMPREHENSIVE EXAM PERSPECTIVE** (3-4 paragraphs)
   - Importance for competitive exams with weightage analysis
   - Common question types and mathematical patterns
   - Problem-solving strategies and mathematical techniques
   - Previous year question analysis with solution methods
   - Time management and calculation shortcuts

10. **FURTHER MATHEMATICAL EXPLORATION** (3 paragraphs)
    - Advanced mathematical topics for deeper study
    - Research opportunities with mathematical requirements
    - Recommended mathematical resources and textbooks
    - Software tools and computational resources

MATHEMATICAL PRESENTATION GUIDELINES:
- Use proper LaTeX formatting: $E = mc^2$, $\psi(x,t) = A e^{i(kx - \omega t)}$, $\frac{\partial^2 \psi}{\partial x^2} + \frac{2m}{\hbar^2}(E-V)\psi = 0$
- Show every algebraic step: If going from $a = b + c$ to $a - b = c$, show the subtraction explicitly
- Include all mathematical manipulations: factoring, expanding, substituting, integrating, differentiating
- Number important equations: (1), (2), (3), etc.
- Provide mathematical commentary: "Substituting equation (2) into (1)..."
- Show units throughout calculations: $[E] = \text{kg⋅m²⋅s⁻²} = \text{J}$
- Include mathematical proofs where relevant
- Use multiple mathematical approaches when possible

CONTENT GUIDELINES FOR MAXIMUM DETAIL:
- Each section should be substantial (minimum 4-5 paragraphs each)
- Mathematical derivations should show every step with explanations
- Include multiple sub-headings for organization
- Provide extensive mathematical analysis and computations
- Include numerical values, constants, and units throughout
- Use clear, pedagogical mathematical explanations
- Connect mathematical theory to practical applications
- Include current research with mathematical content
- Provide complete mathematical solutions to all examples

ALWAYS ENSURE:
- Responses are extremely comprehensive and detailed (minimum 3000+ words)
- ALL mathematical derivations show EVERY step
- Multiple examples with complete mathematical solutions
- Current research and mathematical developments included
- Content is mathematically rigorous and exam-focused
- Cross-connections to mathematical techniques in other areas
- Mathematical notation is consistent and clearly explained

Your goal is to provide the most comprehensive, mathematically detailed, and educational physics content possible with complete step-by-step derivations.
"""

# --- Streamlit Config ---
st.set_page_config(
    page_title="🧠 Physics GPT by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Dark Mode CSS with Better Response UI ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* Root variables for dark theme */
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #1a1d35;
            --bg-tertiary: #2a2d4a;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-accent: #94a3b8;
            --accent-primary: #00d9ff;
            --accent-secondary: #7c3aed;
            --accent-gradient: linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%);
            --border-color: #334155;
            --shadow-light: rgba(0, 217, 255, 0.1);
            --shadow-dark: rgba(0, 0, 0, 0.4);
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
        }
        
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1d35 100%);
        }
        
        /* Main container styling */
        .main-container {
            background: rgba(42, 45, 74, 0.95);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1rem;
            box-shadow: 0 25px 50px var(--shadow-dark);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
        }
        
        /* Enhanced title with Physics GPT branding */
        .main-title {
            text-align: center;
            font-size: 3.5rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 40px rgba(0, 217, 255, 0.4);
            letter-spacing: -1px;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1.4rem;
            color: var(--text-secondary);
            margin-bottom: 2.5rem;
            font-weight: 500;
        }
        
        .creator-badge {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .creator-badge span {
            background: var(--accent-gradient);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-size: 0.95rem;
            font-weight: 600;
            box-shadow: 0 4px 15px var(--shadow-light);
        }
        
        /* Enhanced Response Section UI */
        .response-header {
            background: var(--accent-gradient);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 20px 20px 0 0;
            font-size: 1.6rem;
            font-weight: 700;
            text-align: center;
            box-shadow: 0 4px 20px var(--shadow-light);
            position: relative;
            overflow: hidden;
        }
        
        .response-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .response-container {
            background: linear-gradient(135deg, rgba(42, 45, 74, 0.98) 0%, rgba(51, 65, 85, 0.95) 100%);
            border-radius: 0 0 20px 20px;
            border: 1px solid var(--border-color);
            box-shadow: 0 15px 35px var(--shadow-dark);
            margin-top: 0;
            overflow: hidden;
        }
        
        .response-meta {
            background: rgba(30, 41, 59, 0.8);
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .response-badge {
            background: var(--accent-gradient);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 2px 8px var(--shadow-light);
        }
        
        .response-badge.style {
            background: linear-gradient(135deg, var(--success-color), #059669);
        }
        
        .response-badge.level {
            background: linear-gradient(135deg, var(--warning-color), #d97706);
        }
        
        .response-badge.enhanced {
            background: linear-gradient(135deg, var(--error-color), #dc2626);
        }
        
        .response-content {
            padding: 3rem;
            font-size: 1.7rem;  /* Increased from 1.6rem */
            line-height: 2.0;   /* Increased line height for better readability */
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            max-width: none;
            overflow-wrap: break-word;
        }
        
        .response-content h1 {
            font-size: 2.4rem;  /* Increased from 2.2rem */
            font-weight: 700;
            border-bottom: 3px solid var(--accent-primary);
            padding-bottom: 0.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary) !important;
        }
        
        .response-content h2 {
            font-size: 2.1rem;  /* Increased from 1.9rem */
            font-weight: 600;
            color: var(--accent-primary) !important;
            margin-top: 2.5rem;
            margin-bottom: 1.3rem;
        }
        
        .response-content h3 {
            font-size: 1.9rem;  /* Increased from 1.7rem */
            font-weight: 600;
            color: var(--text-secondary) !important;
            margin-top: 2rem;
            margin-bottom: 1.2rem;
        }
        
        .response-content h4 {
            font-size: 1.7rem;
            font-weight: 600;
            color: var(--text-accent) !important;
            margin-top: 1.8rem;
            margin-bottom: 1rem;
        }
        
        .response-content p {
            margin-bottom: 2rem;  /* Increased spacing */
            text-align: justify;
            font-size: 1.7rem;  /* Ensure paragraphs use larger font */
            line-height: 2.0;
        }
        
        .response-content ul, .response-content ol {
            margin: 2rem 0;
            padding-left: 2.5rem;
            font-size: 1.7rem;  /* Ensure lists use larger font */
        }
        
        .response-content li {
            margin-bottom: 1rem;  /* Increased spacing between list items */
            font-size: 1.7rem;
            line-height: 1.9;
        }
        
        /* Enhanced mathematical content styling */
        .response-content code {
            background: rgba(30, 41, 59, 0.9);
            color: var(--accent-primary);
            padding: 0.5rem 1rem;  /* Increased padding */
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border-color);
            font-size: 1.5rem;  /* Larger code font */
            font-weight: 500;
        }
        
        .response-content pre {
            background: rgba(15, 23, 42, 0.95);
            padding: 2.5rem;  /* Increased padding */
            border-radius: 15px;
            border: 2px solid var(--border-color);
            overflow-x: auto;
            margin: 2.5rem 0;
            font-size: 1.4rem;  /* Larger pre-formatted text */
            line-height: 1.6;
            box-shadow: 0 4px 15px var(--shadow-dark);
        }
        
        /* Mathematical equation styling */
        .response-content .math {
            font-size: 1.8rem !important;
            color: var(--accent-primary) !important;
            background: rgba(30, 41, 59, 0.3);
            padding: 0.8rem 1.2rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
            display: inline-block;
        }
        
        .response-content blockquote {
            border-left: 4px solid var(--accent-primary);
            background: rgba(30, 41, 59, 0.4);
            padding: 1.5rem 2rem;
            margin: 2rem 0;
            border-radius: 0 12px 12px 0;
            font-style: italic;
            font-size: 1.6rem;
        }
        
        /* Table styling for mathematical content */
        .response-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            font-size: 1.6rem;
        }
        
        .response-content th, .response-content td {
            border: 1px solid var(--border-color);
            padding: 1rem;
            text-align: left;
            background: rgba(30, 41, 59, 0.3);
        }
        
        .response-content th {
            background: rgba(0, 217, 255, 0.2);
            font-weight: 600;
        }
        
        .response-footer {
            background: rgba(15, 23, 42, 0.8);
            padding: 1.5rem 2rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
        }
        
        .physics-gpt-signature {
            color: var(--text-accent);
            font-size: 1.1rem;
            font-style: italic;
        }
        
        .physics-gpt-signature strong {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        /* Action buttons styling */
        .action-buttons {
            background: rgba(30, 41, 59, 0.6);
            padding: 1.5rem 2rem;
            border-top: 1px solid var(--border-color);
        }
        
        .action-buttons h3 {
            color: var(--text-primary) !important;
            text-align: center;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        /* Form and input styling */
        .stTextArea > div > div > textarea {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.2rem !important;
            padding: 1.2rem !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px var(--shadow-light) !important;
        }
        
        .stSelectbox > div > div > div {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
        }
        
        .stMultiSelect > div > div > div {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 10px !important;
        }
        
        .stTextInput > div > div > input {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
        }
        
        /* Enhanced button styling */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.9rem 2.5rem !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px var(--shadow-light) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 30px var(--shadow-light) !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: rgba(10, 14, 39, 0.95) !important;
            border-right: 1px solid var(--border-color) !important;
        }
        
        .sidebar-content {
            background: rgba(30, 41, 59, 0.7) !important;
            border-radius: 12px !important;
            padding: 1.2rem !important;
            margin-bottom: 1rem !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Physics domains grid */
        .physics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .physics-domain {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(51, 65, 85, 0.7));
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            border: 2px solid var(--border-color);
            transition: all 0.3s ease;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .physics-domain:hover {
            border-color: var(--accent-primary);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px var(--shadow-light);
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(124, 58, 237, 0.1));
        }
        
        /* Comprehensive topics box */
        .comprehensive-topics {
            background: rgba(16, 185, 129, 0.1);
            border-radius: 12px;
            padding: 1.2rem;
            margin: 1rem 0;
            border-left: 4px solid var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        /* Metrics styling */
        .css-1r6slb0 {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        
        /* Expandable sections */
        .streamlit-expanderHeader {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
        }
        
        /* File uploader */
        .css-1cpxqw2 {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 2px dashed var(--accent-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
        }
        
        /* Better contrast for all text */
        p, div, span, label {
            color: var(--text-primary) !important;
        }
        
        .css-10trblm {
            color: var(--text-secondary) !important;
        }
        
        /* Loading spinner styling */
        .stSpinner > div {
            border-top-color: var(--accent-primary) !important;
        }
        
        /* Slider styling */
        .stSlider > div > div > div > div {
            background-color: var(--accent-primary) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Comprehensive Physics Domains Sidebar ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT - All Domains")
    
    # Complete physics coverage without categorization
    all_physics_topics = [
        # Mathematical Physics
        "Vector Calculus", "Tensor Analysis", "Complex Analysis", "Special Functions", 
        "Green's Functions", "Group Theory", "Differential Equations", "Fourier Analysis",
        "Variational Methods", "Perturbation Theory", "Numerical Methods",
        
        # Classical Mechanics
        "Newtonian Mechanics", "Lagrangian Mechanics", "Hamiltonian Mechanics", 
        "Central Forces", "Rigid Body Dynamics", "Small Oscillations", "Normal Modes",
        "Chaos Theory", "Nonlinear Dynamics", "Continuum Mechanics", "Fluid Dynamics",
        "Special Relativity", "General Relativity",
        
        # Quantum Mechanics
        "Wave Mechanics", "Matrix Mechanics", "Schrödinger Equation", "Hydrogen Atom",
        "Angular Momentum", "Spin", "Pauli Matrices", "Perturbation Theory", 
        "Scattering Theory", "Path Integrals", "Second Quantization", "Many-Body Theory",
        "Quantum Field Theory", "Quantum Information", "Quantum Computing",
        
        # Electromagnetic Theory
        "Electrostatics", "Magnetostatics", "Maxwell Equations", "Electromagnetic Waves",
        "Wave Propagation", "Waveguides", "Antennas", "Plasma Physics", "MHD Theory",
        "Superconductivity", "Meissner Effect", "Josephson Junctions", "Dielectrics",
        
        # Thermodynamics & Statistical Mechanics
        "Laws of Thermodynamics", "Kinetic Theory", "Maxwell-Boltzmann Distribution",
        "Canonical Ensemble", "Grand Canonical Ensemble", "Fermi-Dirac Statistics",
        "Bose-Einstein Statistics", "Phase Transitions", "Critical Phenomena", 
        "Ising Model", "Monte Carlo Methods", "Non-equilibrium Physics",
        
        # Solid State Physics
        "Crystal Structure", "Bravais Lattices", "X-ray Diffraction", "Phonons",
        "Free Electron Model", "Band Theory", "Semiconductors", "p-n Junctions",
        "Transistors", "Magnetism", "Superconductivity", "BCS Theory", "Defects",
        "Phase Diagrams", "Quantum Hall Effect", "Topological Insulators",
        
        # Atomic & Molecular Physics
        "Atomic Structure", "Electronic Configurations", "Spectroscopy", "Selection Rules",
        "Zeeman Effect", "Stark Effect", "Hyperfine Structure", "Laser Physics",
        "Stimulated Emission", "Molecular Bonding", "MO Theory", "Vibrational Spectra",
        "Rotational Spectra", "Photoelectron Spectroscopy", "Quantum Optics",
        
        # Nuclear & Particle Physics
        "Nuclear Structure", "Shell Model", "Binding Energy", "Radioactive Decay",
        "Nuclear Reactions", "Fission", "Fusion", "Standard Model", "Quarks",
        "Leptons", "Gauge Theories", "Symmetries", "Conservation Laws", "Neutrino Physics",
        "Particle Accelerators", "Detectors", "Cosmology", "Dark Matter", "Dark Energy",
        
        # Electronics & Instrumentation
        "Semiconductor Physics", "Diodes", "Transistors", "Amplifiers", "Oscillators",
        "Digital Logic", "Boolean Algebra", "Microprocessors", "Embedded Systems",
        "Signal Processing", "Filters", "Control Systems", "Feedback Theory",
        "Measurement Techniques", "Error Analysis", "Data Acquisition",
        
        # Optics & Photonics
        "Geometrical Optics", "Wave Optics", "Interference", "Diffraction", "Polarization",
        "Fiber Optics", "Holography", "Fourier Optics", "Nonlinear Optics", "Laser Theory",
        "Laser Applications", "Optical Communication", "Photonic Crystals",
        
        # Condensed Matter Physics
        "Many-Body Theory", "Strongly Correlated Systems", "Quantum Phase Transitions",
        "Topological Phases", "Quantum Materials", "High-Temperature Superconductivity",
        "Quantum Spin Liquids", "Graphene", "2D Materials", "Metamaterials",
        
        # Biophysics & Medical Physics
        "Biomolecular Structure", "Protein Folding", "DNA Physics", "Membrane Physics",
        "Ion Channels", "Neural Networks", "Medical Imaging", "MRI Physics", "CT Imaging",
        "Ultrasound", "Radiation Therapy", "Dosimetry", "Radiobiology",
        
        # Astrophysics & Cosmology
        "Stellar Physics", "Stellar Evolution", "White Dwarfs", "Neutron Stars",
        "Black Holes", "Galactic Dynamics", "Dark Matter", "Dark Energy", "Big Bang",
        "Cosmic Microwave Background", "Gravitational Waves", "Exoplanets",
        
        # Plasma Physics
        "Plasma Fundamentals", "Debye Shielding", "Plasma Oscillations", "MHD Waves",
        "Fusion Physics", "Tokamaks", "Stellar Plasma", "Space Plasma", "Laboratory Plasma",
        
        # Computational Physics
        "Numerical Integration", "Root Finding", "Linear Algebra", "Monte Carlo Methods",
        "Molecular Dynamics", "Density Functional Theory", "Finite Element Methods",
        "High Performance Computing", "Machine Learning in Physics",
        
        # Experimental Physics
        "Vacuum Technology", "Cryogenics", "High Magnetic Fields", "Pressure Techniques",
        "Spectroscopic Methods", "Microscopy", "Neutron Scattering", "Synchrotron Radiation",
        
        # Applied Physics
        "Materials Science", "Nanotechnology", "Renewable Energy", "Solar Cells",
        "Energy Storage", "Quantum Technologies", "Spintronics", "Plasmonics"
    ]
    
    # Display all topics in a compact grid
    st.markdown('<div class="comprehensive-topics">', unsafe_allow_html=True)
    st.markdown(f"**{len(all_physics_topics)} Physics Topics Available**")
    st.markdown("*Ask any question from any physics domain*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick topic buttons in columns
    cols = st.columns(2)
    for i, topic in enumerate(all_physics_topics[:20]):  # Show first 20 for quick access
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(topic, key=f"quick_{topic}"):
                st.session_state.quick_topic = topic
    
    if st.button("🔍 Show All Topics", key="show_all"):
        st.session_state.show_all_topics = True
    
    # If show all is clicked, display remaining topics
    if hasattr(st.session_state, 'show_all_topics') and st.session_state.show_all_topics:
        st.markdown("### Complete Topic List")
        for topic in all_physics_topics[20:]:
            if st.button(topic, key=f"all_{topic}"):
                st.session_state.selected_topic = topic

    # Exam Resources
    st.markdown("### 📚 Exam Resources")
    exam_info = {
        "IIT-JAM": "Mathematical Methods, Mechanics, Waves, EM Theory, Thermodynamics, Modern Physics",
        "CSIR-NET": "Mathematical Physics, Classical Mechanics, QM, EM Theory, Statistical Physics",
        "GATE": "Engineering Mathematics, Classical Mechanics, EM Theory, QM, Thermodynamics",
        "JEST": "Advanced Physics, Research Aptitude, Theoretical Physics",
        "TIFR": "Comprehensive Physics, Research-oriented Problems"
    }
    
    for exam, topics in exam_info.items():
        with st.expander(exam):
            st.write(topics)

    # Mathematical Detail Settings
    st.markdown("### 🧮 Mathematical Settings")
    
    math_detail_level = st.slider(
        "Mathematical Detail Level:",
        min_value=1,
        max_value=5,
        value=4,
        help="1: Basic, 3: Standard, 5: Maximum Detail"
    )
    
    derivation_style = st.selectbox(
        "Derivation Style:",
        ["Complete Step-by-Step", "Detailed with Explanations", "Multiple Methods", "Research Level"]
    )

# --- Main Content ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Enhanced Title Section with Physics GPT Branding
st.markdown('<div class="main-title">🧠 Physics GPT</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced AI Physics Tutor with Complete Mathematical Derivations</div>', unsafe_allow_html=True)

# Physics Domains Overview
st.markdown("### 🌟 Complete Physics Coverage with Mathematical Rigor")
physics_domains = [
    "Mathematical Physics", "Classical Mechanics", "Quantum Mechanics", "Electromagnetic Theory",
    "Statistical Mechanics", "Solid State Physics", "Atomic Physics", "Nuclear Physics",
    "Particle Physics", "Electronics", "Optics", "Condensed Matter", "Biophysics",
    "Astrophysics", "Plasma Physics", "Computational Physics", "Applied Physics"
]

st.markdown('<div class="physics-grid">', unsafe_allow_html=True)
for domain in physics_domains:
    st.markdown(f'<div class="physics-domain">{domain}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Physics Topics", f"{len(all_physics_topics)}", "Complete Coverage")
with col2:
    st.metric("Domains Covered", len(physics_domains), "All Areas")
with col3:
    st.metric("Mathematical Rigor", "Maximum", "Step-by-Step")
with col4:
    st.metric("Derivation Detail", "Complete", "Every Step")

# Universal Input Form
with st.form(key="universal_physics_form", clear_on_submit=False):
    # Main question input
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = f"Provide complete mathematical derivation and comprehensive explanation of {st.session_state.selected_topic}"
    elif hasattr(st.session_state, 'quick_topic'):
        default_question = f"Derive all key equations and provide detailed mathematical analysis of {st.session_state.quick_topic}"
    
    query = st.text_area(
        "🎯 Ask Physics GPT for detailed mathematical derivations:",
        value=default_question,
        placeholder="e.g., Derive the complete time-dependent Schrödinger equation from first principles with every mathematical step, or Provide complete derivation of Maxwell's equations with all intermediate steps",
        height=130,
        key="universal_question"
    )
    
    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        response_style = st.selectbox(
            "📋 Response Style:",
            ["Complete Mathematical Derivation", "Step-by-Step with Explanations", "Multiple Derivation Methods", 
             "Research-Level Analysis", "Exam-Focused with Derivations", "Comprehensive with Examples"]
        )
    
    with col2:
        academic_level = st.selectbox(
            "🎓 Academic Level:",
            ["Advanced Undergraduate", "Graduate", "Research Level", "Professional", "Auto-Detect"]
        )
    
    with col3:
        mathematical_focus = st.multiselect(
            "🧮 Mathematical Focus:",
            ["Complete Derivations", "Alternative Methods", "Numerical Examples", "Approximation Methods", 
             "Computational Approaches", "Advanced Techniques", "Research Applications"]
        )
    
    # Advanced Mathematical Options
    with st.expander("🔬 Advanced Mathematical Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            detail_level = st.slider(
                "Derivation Detail Level:",
                min_value=1,
                max_value=5,
                value=4,
                help="1: Basic steps, 5: Every algebraic manipulation"
            )
            
            include_proofs = st.checkbox("Include mathematical proofs", value=True)
            show_all_steps = st.checkbox("Show every algebraic step", value=True)
            
        with col2:
            response_length = st.selectbox(
                "Response Comprehensiveness:",
                ["Extended", "Comprehensive", "Maximum Detail", "Research Paper Length"]
            )
            
            include_numerical = st.checkbox("Include numerical calculations", value=True)
            multiple_methods = st.checkbox("Show alternative derivation methods", value=True)
    
    # File upload and references
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "📄 Upload Reference Material (Optional):",
            type=["pdf", "docx"],
            help="Upload physics textbooks, papers, or lecture notes"
        )
    
    with col2:
        url_input = st.text_input(
            "🌐 Reference URL (Optional):",
            placeholder="https://arxiv.org/abs/...",
            help="Link to research papers, lectures, or mathematical resources"
        )
    
    # Submit button
    submit_button = st.form_submit_button("🚀 Generate Complete Mathematical Analysis", use_container_width=True)

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

# --- Enhanced Answer Generation with Maximum Mathematical Detail ---
if submit_button and query:
    with st.spinner(f"🧠 Physics GPT is performing comprehensive mathematical analysis with {response_style.lower()}..."):
        # Context extraction
        context = ""
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                context = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                context = extract_text_from_docx(uploaded_file)
        elif url_input:
            context = extract_text_from_url(url_input)

        context = context.strip()
        if len(context) > 6000:
            context = context[:6000] + "\n...[Content truncated for processing]"

        # Enhanced mathematical prompt construction
        mathematical_prompt = f"""
MATHEMATICAL ANALYSIS REQUIREMENTS:

RESPONSE STYLE: {response_style}
ACADEMIC LEVEL: {academic_level}
MATHEMATICAL FOCUS: {', '.join(mathematical_focus) if mathematical_focus else 'Complete mathematical treatment'}
DETAIL LEVEL: {detail_level}/5 (Show {"every single algebraic manipulation" if detail_level >= 4 else "all major steps"})
RESPONSE LENGTH: {response_length}

MATHEMATICAL REQUIREMENTS:
- SHOW EVERY STEP: {"Yes - every algebraic manipulation" if show_all_steps else "Major steps only"}
- INCLUDE PROOFS: {"Yes - complete mathematical proofs" if include_proofs else "Basic justifications"}
- NUMERICAL EXAMPLES: {"Yes - with complete calculations" if include_numerical else "Theory only"}
- ALTERNATIVE METHODS: {"Yes - multiple derivation approaches" if multiple_methods else "Single method"}

CRITICAL INSTRUCTIONS FOR MAXIMUM MATHEMATICAL DETAIL:
1. Start with fundamental postulates and axioms
2. Show EVERY algebraic manipulation step-by-step
3. Explain the reasoning behind each mathematical step
4. Include dimensional analysis at each major step
5. Provide multiple derivation methods when applicable
6. Include complete worked examples with all calculations shown
7. Show all intermediate mathematical results
8. Explain all mathematical techniques and tools used
9. Include approximations and their justifications
10. Provide extensive mathematical commentary

{f"REFERENCE CONTEXT:\n{context}\n" if context else ""}

PHYSICS QUESTION REQUIRING COMPREHENSIVE MATHEMATICAL TREATMENT: {query}

Please provide the most comprehensive, mathematically detailed response possible. Show every mathematical step, explain every technique used, and provide complete derivations with extensive mathematical analysis. This should be a thorough mathematical treatment suitable for advanced physics study.
"""

        # Generate response
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"question": mathematical_prompt})

        # Enhanced Response UI with Mathematical Focus
        st.markdown('<div class="response-header">🧠 Physics GPT - Complete Mathematical Analysis</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="response-container">', unsafe_allow_html=True)
        
        # Response metadata with mathematical details
        st.markdown('<div class="response-meta">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="response-badge style">Style: {response_style}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="response-badge level">Level: {academic_level}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="response-badge enhanced">Detail: Level {detail_level}/5</div>', unsafe_allow_html=True)
        with col4:
            if show_all_steps:
                st.markdown(f'<div class="response-badge">Complete Steps</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Main response content with enhanced mathematical formatting
        st.markdown('<div class="response-content">{}</div>'.format(response), unsafe_allow_html=True)
        
        # Physics GPT signature
        st.markdown('<div class="response-footer">', unsafe_allow_html=True)
        st.markdown('<div class="physics-gpt-signature">Complete Mathematical Analysis by <strong>Physics GPT</strong> - Advanced AI Physics Tutor by <strong>Sreekesh M</strong></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Mathematical Action Buttons
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        st.markdown("### 🧮 Further Mathematical Exploration")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 More Detailed Steps", key="more_steps"):
                st.info("Ask Physics GPT to show even more detailed mathematical steps!")
        
        with col2:
            if st.button("🧮 Alternative Derivations", key="alt_methods"):
                st.info("Request alternative mathematical approaches and derivation methods!")
        
        with col3:
            if st.button("🔬 Numerical Applications", key="numerical"):
                st.info("Ask for numerical examples with complete computational steps!")
        
        with col4:
            if st.button("📚 Advanced Extensions", key="advanced"):
                st.info("Inquire about advanced mathematical treatments and research applications!")
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer with Mathematical Focus ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
    <div style="font-size: 1.6rem; font-weight: 700; margin-bottom: 0.5rem;">
        🧠 <strong style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT</strong>
    </div>
    <div style="font-size: 1.2rem; margin-bottom: 1rem;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 1rem; margin-bottom: 0.5rem;">
        <em>Advanced AI Physics Tutor with Complete Mathematical Derivations</em>
    </div>
    <div style="font-size: 0.95rem; margin-bottom: 0.5rem;">
        📐 <strong>{len(all_physics_topics)} Topics</strong> • 🧮 <strong>Complete Step-by-Step Derivations</strong> • 🔬 <strong>All Physics Domains</strong>
    </div>
    <div style="font-size: 0.9rem;">
        🌟 From Basic Principles to Advanced Research • Every Mathematical Step Explained
    </div>
</div>
""", unsafe_allow_html=True)
