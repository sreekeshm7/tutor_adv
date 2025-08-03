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

Always use proper LaTeX formatting for mathematical expressions and provide step-by-step derivations with clear explanations.
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700;800&family=Fira+Math&display=swap');
        
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
            --border-primary: #334155;
            --shadow-primary: rgba(0, 229, 255, 0.15);
            --shadow-dark: rgba(0, 0, 0, 0.5);
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
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
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
        
        /* Enhanced Title Design with Logo */
        .main-logo {
            text-align: center;
            font-size: 4rem;
            margin-bottom: 1rem;
            color: var(--accent-primary);
            text-shadow: 0 0 30px rgba(0, 229, 255, 0.5);
        }
        
        .main-title {
            text-align: center;
            font-size: clamp(2.5rem, 5vw, 3.5rem);
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
            font-size: clamp(1.0rem, 2.5vw, 1.4rem);
            color: var(--text-secondary);
            margin-bottom: 3rem;
            font-weight: 500;
            line-height: 1.6;
            font-family: 'Inter', sans-serif;
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
            box-shadow: 0 8px 25px var(--shadow-primary);
            position: relative;
            overflow: hidden;
        }
        
        /* Revolutionary Response Design with Reduced Font Sizes */
        .response-header {
            background: var(--accent-gradient);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 24px 24px 0 0;
            font-size: clamp(1.2rem, 3vw, 1.6rem);
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
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 4px 15px var(--shadow-primary);
        }
        
        /* REDUCED Font Sizes for Response Content */
        .response-content {
            padding: 3rem;
            font-size: 1.3rem;  /* REDUCED from 1.8rem */
            line-height: 1.8;   /* Adjusted line height */
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
            font-size: 1.9rem;  /* REDUCED from 2.6rem */
            font-weight: 800;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 2px solid var(--accent-primary);
            padding-bottom: 0.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .response-content h2 {
            font-size: 1.6rem;  /* REDUCED from 2.3rem */
            font-weight: 700;
            color: var(--accent-primary) !important;
            margin-top: 2rem;
            margin-bottom: 1.3rem;
            position: relative;
            padding-left: 1.2rem;
        }
        
        .response-content h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 60%;
            background: var(--accent-gradient);
            border-radius: 2px;
        }
        
        .response-content h3 {
            font-size: 1.4rem;  /* REDUCED from 2.0rem */
            font-weight: 600;
            color: var(--accent-secondary) !important;
            margin-top: 1.8rem;
            margin-bottom: 1.2rem;
            position: relative;
            padding-left: 0.8rem;
        }
        
        .response-content h4 {
            font-size: 1.3rem;  /* REDUCED from 1.8rem */
            font-weight: 600;
            color: var(--text-secondary) !important;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .response-content p {
            margin-bottom: 1.8rem;
            text-align: justify;
            font-size: 1.3rem;  /* REDUCED from 1.8rem */
            line-height: 1.8;
            text-indent: 1.5rem;
        }
        
        .response-content p:first-of-type {
            font-size: 1.4rem;  /* REDUCED from 2.0rem */
            font-weight: 500;
            color: var(--text-secondary);
            text-indent: 0;
        }
        
        .response-content ul, .response-content ol {
            margin: 1.8rem 0;
            padding-left: 2.5rem;
            font-size: 1.3rem;  /* REDUCED from 1.8rem */
        }
        
        .response-content li {
            margin-bottom: 0.8rem;
            font-size: 1.3rem;  /* REDUCED from 1.8rem */
            line-height: 1.7;
            position: relative;
        }
        
        /* Enhanced Mathematical Content with LaTeX support */
        .response-content code {
            background: rgba(15, 23, 42, 0.95);
            color: var(--accent-primary);
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border-primary);
            font-size: 1.2rem;  /* REDUCED from 1.6rem */
            font-weight: 500;
            box-shadow: 0 2px 8px var(--shadow-dark);
        }
        
        .response-content pre {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.95));
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid var(--border-primary);
            overflow-x: auto;
            margin: 2rem 0;
            font-size: 1.1rem;  /* REDUCED from 1.5rem */
            line-height: 1.6;
            box-shadow: 0 8px 25px var(--shadow-dark);
            position: relative;
        }
        
        /* Enhanced LaTeX Rendering */
        .katex {
            font-family: 'Fira Math', 'Latin Modern Math', 'STIX Two Math', serif !important;
            font-size: 1.3em !important;  /* Optimal size for LaTeX */
            color: var(--accent-primary) !important;
        }
        
        .katex-display {
            margin: 1.5rem 0 !important;
            padding: 1rem !important;
            background: rgba(15, 23, 42, 0.3) !important;
            border-radius: 8px !important;
            border-left: 4px solid var(--accent-primary) !important;
        }
        
        /* REDUCED Font Sizes for Form Elements */
        .stTextArea > div > div > textarea {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 1.0rem !important;  /* REDUCED from 1.3rem */
            padding: 1.2rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 3px var(--shadow-primary) !important;
        }
        
        .stSelectbox > div > div > div {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;  /* REDUCED from 1.2rem */
        }
        
        .stMultiSelect > div > div > div {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            font-size: 0.9rem !important;  /* REDUCED */
        }
        
        .stTextInput > div > div > input {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.9)) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;  /* REDUCED from 1.2rem */
        }
        
        /* Revolutionary Button Design */
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 1rem 2.5rem !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            transition: all 0.4s ease !important;
            box-shadow: 0 6px 20px var(--shadow-primary) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 30px var(--shadow-primary) !important;
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
            border-radius: 12px !important;
            padding: 1.2rem !important;
            margin-bottom: 1.2rem !important;
            border: 1px solid var(--glass-border) !important;
            box-shadow: 0 4px 15px var(--shadow-dark) !important;
        }
        
        /* Physics Domain Grid */
        .physics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.2rem;
            margin: 1.8rem 0;
        }
        
        .physics-domain {
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            border: 2px solid var(--glass-border);
            transition: all 0.4s ease;
            cursor: pointer;
            font-size: 1.0rem;
            font-weight: 600;
            color: var(--text-primary);
            position: relative;
            overflow: hidden;
        }
        
        .physics-domain:hover {
            border-color: var(--accent-primary);
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 30px var(--shadow-primary);
            color: white;
        }
        
        /* Comprehensive Topics */
        .comprehensive-topics {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1));
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.2rem 0;
            border-left: 4px solid #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        /* Footer Styling */
        .footer {
            text-align: center;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            color: var(--text-accent);
            margin-top: 2rem;
            padding: 1.5rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 2rem;
                margin: 1rem;
            }
            
            .response-content {
                padding: 2rem;
                font-size: 1.2rem;
            }
            
            .main-title {
                font-size: 2.2rem;
            }
            
            .main-logo {
                font-size: 3rem;
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
        "Quantum Hall Effect", "Topological Insulators", "2D Materials & Graphene"
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
        "💎 Solid State Physics": all_physics_topics[62:]
    }
    
    for category, topics in topic_categories.items():
        with st.expander(f"{category} ({len(topics)} topics)"):
            for i, topic in enumerate(topics):
                # FIXED: Using unique keys with category prefix
                unique_key = f"{category.split()[1].lower()}_{i}_{abs(hash(topic)) % 10000}"
                if st.button(topic, key=unique_key):
                    st.session_state.selected_topic = topic
                    st.rerun()

# --- Main Application Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Enhanced header design with logo
st.markdown('<div class="main-logo">🧠⚛️🔬</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Physics GPT Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-badge"><span>by Sreekesh M</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Revolutionary AI Physics Tutor with Enhanced LaTeX and Theoretical Analysis</div>', unsafe_allow_html=True)

# Enhanced physics domains visualization
st.markdown("### 🌟 Complete Physics Mastery")
physics_domains = [
    "🧮 Mathematical Physics", "⚛️ Classical Mechanics", "🌊 Quantum Mechanics", "⚡ Electromagnetic Theory",
    "🔥 Statistical Mechanics", "💎 Solid State Physics", "🔬 Atomic Physics", "☢️ Nuclear Physics",
    "🚀 Particle Physics", "💻 Electronics", "🌈 Optics & Photonics", "🧊 Condensed Matter"
]

st.markdown('<div class="physics-grid">', unsafe_allow_html=True)
for domain in physics_domains:
    st.markdown(f'<div class="physics-domain">{domain}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Advanced metrics dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Physics Topics", f"{len(all_physics_topics)}", "Complete Coverage")
with col2:
    st.metric("🔬 Domains Covered", len(physics_domains), "All Fields")
with col3:
    st.metric("🧮 LaTeX Support", "Enhanced", "Premium Quality")
with col4:
    st.metric("🚀 AI Capability", "Revolutionary", "Next-Gen")

# Ultra-advanced input form
with st.form(key="physics_gpt_pro_form", clear_on_submit=False):
    # Main theoretical question input
    default_question = ""
    if hasattr(st.session_state, 'selected_topic'):
        default_question = f"Provide comprehensive theoretical analysis with complete mathematical derivations for {st.session_state.selected_topic}, including LaTeX equations, historical development, and advanced applications"
    
    query = st.text_area(
        "🎯 Ask Physics GPT Pro for Revolutionary Analysis with LaTeX:",
        value=default_question,
        placeholder="e.g., Derive the Schrödinger equation with complete LaTeX formatting and explain its physical significance, or Provide detailed analysis of Maxwell's equations with vector calculus derivations",
        height=140,
        key="physics_gpt_pro_question"
    )
    
    # Advanced configuration matrix
    col1, col2, col3 = st.columns(3)
    
    with col1:
        response_style = st.selectbox(
            "📋 Response Style:",
            ["Ultra-Comprehensive Analysis", "Mathematical Derivation Focus", 
             "Theoretical Investigation", "LaTeX-Heavy Explanation",
             "Historical Development", "Cross-Domain Synthesis"]
        )
    
    with col2:
        academic_level = st.selectbox(
            "🎓 Academic Level:",
            ["Advanced Graduate", "Research Professional", "Theoretical Physicist", 
             "Post-Doctoral", "Faculty Level", "Auto-Adaptive"]
        )
    
    with col3:
        latex_focus = st.multiselect(
            "🧮 LaTeX & Math Focus:",
            ["Complete Derivations", "Step-by-Step Proofs", "Elegant Equations", 
             "Vector Calculus", "Differential Equations", "Advanced Notation",
             "Graphical Representations", "Numerical Examples"]
        )
    
    # Research materials integration
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "📄 Reference Materials:",
            type=["pdf", "docx"],
            help="Upload research papers or textbooks"
        )
    
    with col2:
        url_input = st.text_input(
            "🌐 Research URLs:",
            placeholder="https://arxiv.org/abs/...",
            help="Link to research papers"
        )
    
    # Revolutionary submit button
    submit_button = st.form_submit_button("🚀 Generate Enhanced Physics Analysis", use_container_width=True)

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

# --- Enhanced Answer Generation ---
if submit_button and query:
    # Enhanced loading animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🧠 Physics GPT Pro initializing enhanced analysis...")
    progress_bar.progress(20)
    time.sleep(0.5)
    
    status_text.text("🔬 Processing LaTeX and mathematical frameworks...")
    progress_bar.progress(60)
    time.sleep(0.5)
    
    status_text.text("🌟 Generating comprehensive content...")
    progress_bar.progress(100)
    
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

    # Enhanced prompt construction
    enhanced_prompt = f"""
PHYSICS GPT PRO - ENHANCED ANALYSIS REQUEST

RESPONSE CONFIGURATION:
- STYLE: {response_style}
- ACADEMIC LEVEL: {academic_level}
- LATEX FOCUS: {', '.join(latex_focus) if latex_focus else 'Standard mathematical notation'}

LATEX REQUIREMENTS:
- Use proper LaTeX syntax: $\\psi(x,t) = A e^{{i(kx - \\omega t)}}$
- Display equations: $$\\nabla^2 \\psi + \\frac{{2m}}{{\\hbar^2}}(E-V)\\psi = 0$$
- Include vector notation: $\\vec{{F}} = m\\vec{{a}}$
- Use proper Greek letters and mathematical symbols
- Format matrices and integrals correctly

{f"REFERENCE CONTEXT:\n{context}\n" if context else ""}

PHYSICS QUESTION: {query}

Provide comprehensive analysis with enhanced LaTeX formatting, step-by-step derivations, and clear mathematical explanations.
"""

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Generate response
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"question": enhanced_prompt})

    # Enhanced Response Display
    st.markdown('<div class="response-header">🧠 Physics GPT Pro - Enhanced Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Response metadata
    st.markdown('<div class="response-meta">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="response-badge">Style: {response_style.split()[0]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="response-badge">Level: {academic_level.split()[0]}</div>', unsafe_allow_html=True)
    with col3:
        if latex_focus:
            st.markdown(f'<div class="response-badge">Enhanced LaTeX</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main response content with reduced font size
    st.markdown('<div class="response-content">{}</div>'.format(response), unsafe_allow_html=True)
    
    # Enhanced signature
    st.markdown('<div style="background: rgba(15, 23, 42, 0.9); padding: 1.5rem; text-align: center; border-top: 1px solid #334155; font-size: 1.1rem; color: #CBD5E1; font-style: italic;">Enhanced Analysis by <strong style="background: linear-gradient(135deg, #00E5FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT Pro</strong><br>Next-Generation AI Tutor by <strong>Sreekesh M</strong></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer ---
st.markdown(f"""
<div class="footer">
    <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; font-family: 'Playfair Display', serif;">
        🧠 <strong style="background: linear-gradient(135deg, #00E5FF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Physics GPT Pro</strong>
    </div>
    <div style="font-size: 1.2rem; margin-bottom: 1rem;">
        <em>by <strong>Sreekesh M</strong></em>
    </div>
    <div style="font-size: 1.0rem; line-height: 1.6;">
        🌟 <strong>{len(all_physics_topics)} Topics</strong> • 🧮 <strong>Enhanced LaTeX</strong> • 🔬 <strong>Complete Coverage</strong>
    </div>
</div>
""", unsafe_allow_html=True)
