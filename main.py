import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import time

# --- Enhanced System Prompt for Balanced Analysis ---
SYSTEM_PROMPT = """
You are Physics GPT Pro, an advanced AI physics tutor created by Sreekesh M. You provide comprehensive physics education with perfect balance between mathematical rigor, theoretical depth, and excellent user experience.

CORE REQUIREMENTS:
1. **MATHEMATICAL RIGOR**: Complete step-by-step derivations with clear explanations
2. **THEORETICAL DEPTH**: Comprehensive conceptual understanding from first principles
3. **USER EXPERIENCE**: Clear, engaging, and well-structured presentation

RESPONSE STRUCTURE:
1. **Overview & Concepts** (3-4 comprehensive paragraphs)
2. **Mathematical Framework** (Complete derivations with steps)
3. **Theoretical Examples** (Multiple detailed examples)
4. **Applications & Connections** (Real-world applications)
5. **Summary & Key Points** (Concise conclusion)

Provide balanced, comprehensive responses that excel in mathematics, theory, and presentation quality.
"""

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="🧠 Physics GPT Pro by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Clean CSS Styling ---
st.markdown("""
<style>
    .main-container {
        background: linear-gradient(135deg, #1f2937, #374151);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem;
        border: 1px solid #4b5563;
        color: #f9fafb;
    }
    
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #3b82f6;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #e5e7eb;
        margin-bottom: 2rem;
    }
    
    .balance-section {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .response-container {
        background: #374151;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #4b5563;
    }
</style>
""", unsafe_allow_html=True)

# --- Physics Topics List ---
physics_topics = [
    "Classical Mechanics", "Quantum Mechanics", "Electromagnetic Theory", 
    "Thermodynamics", "Statistical Mechanics", "Solid State Physics",
    "Atomic Physics", "Nuclear Physics", "Particle Physics", "Relativity",
    "Optics", "Electronics", "Mathematical Physics", "Plasma Physics",
    "Condensed Matter Physics", "Astrophysics", "Biophysics"
]

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT Pro")
    st.markdown("**Complete Physics Mastery**")
    
    # Balance configuration
    st.markdown("#### ⚖️ Analysis Balance")
    
    math_weight = st.slider("Mathematical Rigor", 0.0, 1.0, 0.33, 0.01)
    theory_weight = st.slider("Theoretical Depth", 0.0, 1.0, 0.33, 0.01)
    ux_weight = st.slider("User Experience", 0.0, 1.0, 0.34, 0.01)
    
    # Balance validation
    total_weight = math_weight + theory_weight + ux_weight
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"⚠️ Weights should sum to 1.0 (currently {total_weight:.2f})")
    else:
        st.success("✅ Perfect balance achieved!")
    
    # Topic selection
    st.markdown("#### 📚 Physics Topics")
    selected_topic = st.selectbox("Choose Topic:", ["Select..."] + physics_topics)
    
    # Settings
    st.markdown("#### ⚙️ Settings")
    math_detail = st.slider("Mathematical Detail", 1, 5, 4)
    theory_depth = st.slider("Theoretical Depth", 1, 5, 4)
    include_examples = st.checkbox("Include Examples", True)
    show_applications = st.checkbox("Show Applications", True)

# --- Main Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="title">🧠 Physics GPT Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">by Sreekesh M - Balanced Physics Education</div>', unsafe_allow_html=True)

# Balance display
st.markdown('<div class="balance-section">', unsafe_allow_html=True)
st.markdown("### ⚖️ Perfect Balance Configuration")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mathematics", f"{math_weight*100:.0f}%", "Rigorous")
with col2:
    st.metric("Theory", f"{theory_weight*100:.0f}%", "Comprehensive")
with col3:
    st.metric("User Experience", f"{ux_weight*100:.0f}%", "Excellent")
st.markdown('</div>', unsafe_allow_html=True)

# Main form
with st.form("physics_form"):
    # Question input with template
    default_question = ""
    if selected_topic != "Select...":
        default_question = f"Provide comprehensive analysis with complete mathematical derivations for {selected_topic}"
    
    query = st.text_area(
        "🎯 Physics Question:",
        value=default_question,
        placeholder="Enter your physics question for balanced analysis...",
        height=100
    )
    
    # Configuration options
    col1, col2 = st.columns(2)
    with col1:
        response_style = st.selectbox(
            "Response Style:",
            ["Comprehensive Analysis", "Mathematical Focus", "Theoretical Focus", "Balanced Treatment"]
        )
    with col2:
        academic_level = st.selectbox(
            "Academic Level:",
            ["Undergraduate", "Graduate", "Research Level"]
        )
    
    # File upload
    uploaded_file = st.file_uploader("Reference Materials:", type=["pdf", "docx"])
    
    submit = st.form_submit_button("🚀 Generate Balanced Analysis", use_container_width=True)

# --- Helper Functions ---
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error reading DOCX: {e}"

def generate_balanced_prompt(query, config):
    return f"""
    Generate a comprehensive physics analysis with PERFECT BALANCE:
    
    MATHEMATICAL COMPONENT ({config['math_weight']*100:.0f}%):
    - Complete step-by-step derivations
    - Clear mathematical explanations
    - Multiple approaches where applicable
    
    THEORETICAL COMPONENT ({config['theory_weight']*100:.0f}%):
    - Fundamental principles and concepts
    - Historical context and development
    - Modern applications and connections
    
    USER EXPERIENCE COMPONENT ({config['ux_weight']*100:.0f}%):
    - Clear, engaging presentation
    - Well-organized structure
    - Accessible explanations
    
    SETTINGS:
    - Mathematical Detail: {config.get('math_detail', 4)}/5
    - Theoretical Depth: {config.get('theory_depth', 4)}/5
    - Include Examples: {config.get('include_examples', True)}
    - Show Applications: {config.get('show_applications', True)}
    
    QUESTION: {query}
    
    Provide a balanced, comprehensive response that excels in all three areas.
    """

# --- Response Generation ---
if submit and query:
    # Progress indicator
    with st.spinner("🧠 Generating balanced analysis..."):
        
        # Extract context from uploaded file
        context = ""
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                context = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                context = extract_text_from_docx(uploaded_file)
        
        # Configuration
        config = {
            'math_weight': math_weight,
            'theory_weight': theory_weight,
            'ux_weight': ux_weight,
            'math_detail': math_detail,
            'theory_depth': theory_depth,
            'include_examples': include_examples,
            'show_applications': show_applications
        }
        
        # Generate prompt
        balanced_prompt = generate_balanced_prompt(query, config)
        if context:
            balanced_prompt += f"\n\nADDITIONAL CONTEXT:\n{context[:5000]}"
        
        # Get response
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"question": balanced_prompt})
    
    # Display response
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    st.markdown("## 🧠 Physics GPT Pro Analysis")
    
    # Response metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Style", response_style, "Selected")
    with col2:
        st.metric("Level", academic_level, "Configured")
    with col3:
        st.metric("Balance", "Perfect", "Achieved")
    with col4:
        st.metric("Quality", "Excellent", "Guaranteed")
    
    # Main response
    st.markdown("---")
    st.markdown(response)
    
    # Footer
    st.markdown("---")
    st.markdown("**Perfect Balance Achieved by Physics GPT Pro • Created by Sreekesh M**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("### 🌟 Continue Learning")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧮 More Math Details"):
            st.info("Ask for more mathematical derivations!")
    with col2:
        if st.button("🔬 Deeper Theory"):
            st.info("Request deeper theoretical analysis!")
    with col3:
        if st.button("🎯 Applications"):
            st.info("Explore practical applications!")

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #9ca3af;">
    <h3>🧠 Physics GPT Pro</h3>
    <p><strong>by Sreekesh M</strong></p>
    <p>Perfect Balance: Mathematics • Theory • User Experience</p>
    <p>Comprehensive Physics Education with AI Excellence</p>
</div>
""", unsafe_allow_html=True)
