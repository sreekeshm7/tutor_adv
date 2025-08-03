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
You are an expert Physics Tutor with comprehensive knowledge across all physics domains, specializing in competitive exams (IIT-JAM, CSIR-NET, GATE Physics, IIT-JEE Advanced, JEST, TIFR).

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
    page_title="🔬 Universal Physics Tutor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Dark Mode CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Root variables for dark theme */
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-tertiary: #0f3460;
            --text-primary: #eee;
            --text-secondary: #b8c5d6;
            --accent-primary: #4facfe;
            --accent-secondary: #00f2fe;
            --border-color: #2d3748;
            --shadow: rgba(0, 0, 0, 0.3);
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
        }
        
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .main-container {
            background: rgba(15, 52, 96, 0.95);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 20px 40px var(--shadow);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
        }
        
        .main-title {
            text-align: center;
            font-size: 3.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 30px rgba(79, 172, 254, 0.3);
        }
        
        .subtitle {
            text-align: center;
            font-size: 1.3rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Form and input styling */
        .stTextArea > div > div > textarea {
            background-color: rgba(45, 55, 72, 0.8) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
            padding: 1rem !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2) !important;
        }
        
        .stSelectbox > div > div > div {
            background-color: rgba(45, 55, 72, 0.8) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }
        
        .stMultiSelect > div > div > div {
            background-color: rgba(45, 55, 72, 0.8) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div > input {
            background-color: rgba(45, 55, 72, 0.8) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.8rem 2rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4) !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: rgba(26, 26, 46, 0.95) !important;
            border-right: 1px solid var(--border-color) !important;
        }
        
        .sidebar-content {
            background: rgba(45, 55, 72, 0.6) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 1rem !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Physics domains grid */
        .physics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.8rem;
            margin: 1rem 0;
        }
        
        .physics-domain {
            background: linear-gradient(135deg, rgba(45, 55, 72, 0.8), rgba(75, 85, 99, 0.6));
            border-radius: 12px;
            padding: 1rem;
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
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.1));
        }
        
        /* Comprehensive topics box */
        .comprehensive-topics {
            background: rgba(34, 197, 94, 0.1);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        /* Answer container */
        .answer-container {
            background: linear-gradient(135deg, rgba(45, 55, 72, 0.95) 0%, rgba(75, 85, 99, 0.9) 100%);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 30px var(--shadow);
            color: var(--text-primary);
        }
        
        .answer-container h1, .answer-container h2, .answer-container h3 {
            color: var(--text-primary) !important;
        }
        
        /* Metrics styling */
        .css-1r6slb0 {
            background: rgba(45, 55, 72, 0.6) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        
        /* Expandable sections */
        .streamlit-expanderHeader {
            background: rgba(45, 55, 72, 0.6) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }
        
        /* File uploader */
        .css-1cpxqw2 {
            background: rgba(45, 55, 72, 0.6) !important;
            border: 2px dashed var(--accent-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
        }
        
        /* Form styling */
        .css-k1vhr4 {
            background: rgba(45, 55, 72, 0.3) !important;
            border-radius: 15px !important;
            padding: 1.5rem !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Better contrast for all text */
        p, div, span, label {
            color: var(--text-primary) !important;
        }
        
        .css-10trblm {
            color: var(--text-secondary) !important;
        }
        
        /* Code blocks */
        .stCodeBlock {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }
        
        /* Math expressions */
        .css-1v3fvcr {
            background: rgba(45, 55, 72, 0.6) !important;
            padding: 0.5rem !important;
            border-radius: 6px !important;
            border: 1px solid var(--border-color) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Comprehensive Physics Domains Sidebar ---
with st.sidebar:
    st.markdown("### 🔬 All Physics Domains")
    
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

# Title Section
st.markdown('<div class="main-title">🔬 Universal Physics Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Complete Physics Coverage • Any Topic • Any Level • Any Exam</div>', unsafe_allow_html=True)

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
        "🎯 Ask any Physics question from any domain:",
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
    submit_button = st.form_submit_button("🚀 Get Universal Physics Answer", use_container_width=True)

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
    with st.spinner(f"🧠 Processing your physics question with {response_style.lower()} approach..."):
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

        # Display Universal Answer
        st.markdown('<div class="answer-container">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 1.5rem; font-weight: 600; color: #eee; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #4facfe;">🎯 Universal Physics Response</div>', unsafe_allow_html=True)
        
        # Response metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<span style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">Style: {response_style}</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">Level: {academic_level}</span>', unsafe_allow_html=True)
        with col3:
            if include_extras:
                st.markdown(f'<span style="background: linear-gradient(135deg, #ffc107, #ff8c00); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">Enhanced</span>', unsafe_allow_html=True)
        
        st.markdown('<div style="font-size: 1.1rem; line-height: 1.8; color: #eee; margin-top: 1.5rem;">{}</div>'.format(response), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Universal Action Buttons
        st.markdown("### 🌟 Explore Further")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Deeper Analysis"):
                st.info("Ask for more detailed analysis of any aspect!")
        
        with col2:
            if st.button("🧮 Mathematical Details"):
                st.info("Request mathematical derivations and proofs!")
        
        with col3:
            if st.button("🔬 Experimental Aspects"):
                st.info("Ask about experimental verification and methods!")
        
        with col4:
            if st.button("🚀 Current Research"):
                st.info("Inquire about latest developments in the field!")

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #b8c5d6; padding: 1.5rem;">
    🔬 <strong>Universal Physics Tutor by Sreekesh M</strong><br>
    <em>Complete Physics Coverage • {len(all_physics_topics)} Topics • All Domains • Any Level</em><br>
    <small>🌟 From Classical to Quantum • From Theory to Applications • From Basic to Research Level</small>
</div>
""", unsafe_allow_html=True)
