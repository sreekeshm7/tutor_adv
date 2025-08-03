import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup

# --- Enhanced System Prompt ---
SYSTEM_PROMPT = """
You are Physics GPT, an advanced AI physics tutor created by Sreekesh M, with comprehensive knowledge across all physics domains, specializing in competitive exams (IIT-JAM, CSIR-NET, GATE Physics, IIT-JEE Advanced, JEST, TIFR).

Complete Physics Expertise:
- Mathematical Physics: Vector/Tensor calculus, Complex analysis, Special functions, Green's functions, Group theory, Differential equations
- Classical Mechanics: Newtonian mechanics, Lagrangian/Hamiltonian formalism, Rigid body dynamics, Oscillations, Chaos theory, Relativity
- Quantum Mechanics: Wave mechanics, Matrix mechanics, Scattering theory, Many-body systems, Quantum field theory, Quantum information
- Electromagnetic Theory: Electrostatics, Magnetostatics, Maxwell equations, Wave propagation, Plasma physics, Superconductivity
- Thermodynamics & Statistical Mechanics: Laws of thermodynamics, Kinetic theory, Ensembles, Phase transitions, Critical phenomena
- Solid State Physics: Crystal structure, Band theory, Semiconductors, Magnetism, Superconductivity, Defects, Phase diagrams
- Atomic & Molecular Physics: Atomic structure, Spectroscopy, Lasers, Molecular bonding, Quantum optics, AMO physics
- Nuclear & Particle Physics: Nuclear structure, Radioactivity, Standard model, Symmetries, Accelerators, Cosmology
- Electronics: Semiconductor devices, Analog/Digital circuits, Microprocessors, Signal processing, Control systems
- Optics: Geometrical optics, Wave optics, Fourier optics, Nonlinear optics, Laser physics, Fiber optics
- Biophysics: Biomolecular structure, Protein folding, Membrane physics, Neural networks, Medical imaging
- Astrophysics: Stellar physics, Galactic dynamics, Cosmology, Black holes, Gravitational waves
- Condensed Matter: Many-body theory, Strongly correlated systems, Topological phases, Quantum materials
- Plasma Physics: MHD theory, Fusion physics, Space plasma, Laboratory plasma
- Computational Physics: Numerical methods, Monte Carlo simulations, DFT, Molecular dynamics

Teaching Methodology:
1. **Universal Approach**: Address any physics question regardless of subdomain
2. **Adaptive Depth**: Scale complexity based on question requirements
3. **Cross-Domain Integration**: Connect concepts across different physics areas
4. **Mathematical Rigor**: Use appropriate mathematics for each topic
5. **Practical Applications**: Include real-world relevance and current research

Response Framework:
- **Immediate Answer**: Direct response to the question
- **Conceptual Foundation**: Build from fundamental principles
- **Mathematical Treatment**: Include relevant equations and derivations
- **Physical Insight**: Provide intuitive understanding
- **Connections**: Link to related physics concepts
- **Applications**: Real-world examples and current research
- **Exam Relevance**: Highlight importance for competitive exams

Always provide comprehensive, accurate, and pedagogically sound explanations regardless of the physics topic asked.
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
            padding: 2.5rem;
            font-size: 1.15rem;
            line-height: 1.8;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }
        
        .response-content h1, .response-content h2, .response-content h3 {
            color: var(--text-primary) !important;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        .response-content h1 {
            font-size: 1.8rem;
            font-weight: 700;
            border-bottom: 2px solid var(--accent-primary);
            padding-bottom: 0.5rem;
        }
        
        .response-content h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-primary) !important;
        }
        
        .response-content h3 {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-secondary) !important;
        }
        
        .response-content p {
            margin-bottom: 1.2rem;
            text-align: justify;
        }
        
        .response-content ul, .response-content ol {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        .response-content li {
            margin-bottom: 0.5rem;
        }
        
        .response-content code {
            background: rgba(30, 41, 59, 0.8);
            color: var(--accent-primary);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border-color);
        }
        
        .response-content pre {
            background: rgba(15, 23, 42, 0.9);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow-x: auto;
            margin: 1.5rem 0;
        }
        
        .response-footer {
            background: rgba(15, 23, 42, 0.8);
            padding: 1.5rem 2rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
        }
        
        .physics-gpt-signature {
            color: var(--text-accent);
            font-size: 0.95rem;
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
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        /* Form and input styling */
        .stTextArea > div > div > textarea {
            background-color: rgba(30, 41, 59, 0.9) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
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
        }
        
        /* Enhanced button styling */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.9rem 2.5rem !important;
            font-size: 1.1rem !important;
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
            font-size: 0.95rem;
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

    # Theme Toggle
    st.markdown("### 🎨 Display Settings")
    
    theme_choice = st.selectbox(
        "Choose Theme:",
        ["Dark Mode (Current)", "Light Mode", "High Contrast"]
    )

# --- Main Content ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Enhanced Title Section with Physics GPT Branding
st.markdown('<div class="main-title">🧠 Physics GPT</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced AI Physics Tutor • Complete Coverage • Any Topic • Any Level • Any Exam</div>', unsafe_allow_html=True)

# Physics Domains Overview
st.markdown("### 🌟 Complete Physics Coverage")
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

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Physics Topics", f"{len(all_physics_topics)}", "Complete Coverage")
with col2:
    st.metric("Domains Covered", len(physics_domains), "All Areas")
with col3:
    st.metric("Exam Support", "All Major", "Comprehensive")
with col4:
    st.metric("Depth Levels", "UG to Research", "Adaptive")

# Universal Input Form
with st.form(key="universal_physics_form", clear_on_submit=False):
    # Main question input
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = f"Explain {st.session_state.selected_topic} comprehensively"
    elif hasattr(st.session_state, 'quick_topic'):
        default_question = f"Provide detailed explanation of {st.session_state.quick_topic}"
    
    query = st.text_area(
        "🎯 Ask Physics GPT any question from any domain:",
        value=default_question,
        placeholder="e.g., Explain quantum entanglement and Bell's theorem, or Derive Maxwell's equations from first principles, or How does superconductivity work?",
        height=120,
        key="universal_question"
    )
    
    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        response_style = st.selectbox(
            "📋 Response Style:",
            ["Comprehensive Explanation", "Step-by-Step Derivation", "Problem-Solving Approach", 
             "Conceptual Overview", "Research Perspective", "Exam-Focused", "Quick Summary"]
        )
    
    with col2:
        academic_level = st.selectbox(
            "🎓 Academic Level:",
            ["High School", "Undergraduate", "Advanced Undergraduate", "Graduate", "Research Level", "Auto-Detect"]
        )
    
    with col3:
        include_extras = st.multiselect(
            "➕ Include:",
            ["Mathematical Derivations", "Numerical Examples", "Applications", "Current Research", 
             "Historical Context", "Experimental Methods", "Practice Problems"]
        )
    
    # File upload and references
    uploaded_file = st.file_uploader(
        "📄 Upload Reference Material (Optional):",
        type=["pdf", "docx"],
        help="Upload any physics material for context"
    )
    
    url_input = st.text_input(
        "🌐 Reference URL (Optional):",
        placeholder="https://arxiv.org/abs/...",
        help="Link to papers, lectures, or resources"
    )
    
    # Submit button
    submit_button = st.form_submit_button("🚀 Ask Physics GPT", use_container_width=True)

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

# --- Universal Answer Generation ---
if submit_button and query:
    with st.spinner(f"🧠 Physics GPT is analyzing your question with {response_style.lower()} approach..."):
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
        if len(context) > 5000:
            context = context[:5000] + "\n...[Content truncated for processing]"

        # Universal prompt construction
        universal_prompt = f"""
RESPONSE STYLE: {response_style}
ACADEMIC LEVEL: {academic_level}
ADDITIONAL REQUIREMENTS: {', '.join(include_extras) if include_extras else 'Standard explanation'}

{f"REFERENCE CONTEXT:\n{context}\n" if context else ""}

PHYSICS QUESTION: {query}

Please provide a comprehensive response covering any physics domain this question touches. Use your complete physics expertise to deliver the most helpful and accurate answer possible, regardless of the specific field or complexity level involved.
"""

        # Generate response
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"question": universal_prompt})

        # Enhanced Response UI
        st.markdown('<div class="response-header">🧠 Physics GPT Response</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="response-container">', unsafe_allow_html=True)
        
        # Response metadata
        st.markdown('<div class="response-meta">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="response-badge style">Style: {response_style}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="response-badge level">Level: {academic_level}</div>', unsafe_allow_html=True)
        with col3:
            if include_extras:
                st.markdown(f'<div class="response-badge enhanced">Enhanced Features</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Main response content
        st.markdown('<div class="response-content">{}</div>'.format(response), unsafe_allow_html=True)
        
        # Physics GPT signature
        st.markdown('<div class="response-footer">', unsafe_allow_html=True)
        st.markdown('<div class="physics-gpt-signature">Generated by <strong>Physics GPT</strong> - Advanced AI Physics Tutor by <strong>Sreekesh M</strong></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Action Buttons
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        st.markdown("### 🌟 Explore Further with Physics GPT")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Deeper Analysis", key="deeper"):
                st.info("Ask Physics GPT for more detailed analysis of any aspect!")
        
        with col2:
            if st.button("🧮 Mathematical Details", key="math"):
                st.info("Request mathematical derivations and proofs from Physics GPT!")
        
        with col3:
            if st.button("🔬 Experimental Aspects", key="exp"):
                st.info("Ask Physics GPT about experimental verification and methods!")
        
        with col4:
            if st.button("🚀 Current Research", key="research"):
                st.info("Inquire about latest developments in the field!")
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer with Physics GPT Branding ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
    <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">
        🧠 <strong style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT</strong>
    </div>
    <div style="font-size: 1.1rem; margin-bottom: 1rem;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 0.95rem; margin-bottom: 0.5rem;">
        <em>Advanced AI Physics Tutor • {len(all_physics_topics)} Topics • All Domains • Any Level</em>
    </div>
    <div style="font-size: 0.85rem;">
        🌟 From Classical to Quantum • From Theory to Applications • From Basic to Research Level
    </div>
</div>
""", unsafe_allow_html=True)
