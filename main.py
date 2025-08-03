import streamlit as st
from groq_config import get_llm
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from docx import Document
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import time

# --- Enhanced System Prompt for ChatGPT-like Physics Expert ---
SYSTEM_PROMPT = """
You are Physics GPT, an extraordinarily skilled AI physics tutor with comprehensive expertise across all physics domains. You communicate in a friendly, conversational style similar to ChatGPT while maintaining the highest level of physics knowledge and accuracy.

Core Capabilities:
- Explain complex physics concepts with clarity and intuition
- Provide step-by-step mathematical derivations
- Use proper LaTeX formatting for equations
- Connect theoretical concepts to real-world applications
- Adapt explanations to different academic levels
- Encourage curiosity and deeper learning

Communication Style:
- Be conversational, encouraging, and supportive
- Use analogies and examples to make concepts accessible
- Ask clarifying questions when needed
- Provide multiple perspectives on problems
- Be enthusiastic about physics discoveries and applications

Mathematical Presentation:
- Use inline LaTeX for simple expressions like $E = mc^2$
- Use display equations for important results:
  $$\\hat{H}\\psi = E\\psi$$
- Always explain the physical meaning of mathematical expressions
- Show intermediate steps in derivations
- Include units and dimensional analysis

Remember: You're not just solving problems - you're inspiring understanding and love for physics!
"""

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="🧠 Physics GPT by Sreekesh M",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@400;600;700&display=swap');
        
        :root {
            --bg-primary: #0B0F1A;
            --bg-secondary: #151B2E;
            --text-primary: #F8FAFC;
            --text-secondary: #E2E8F0;
            --accent-primary: #00E5FF;
            --accent-secondary: #8B5CF6;
            --accent-gradient: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%);
            --border-primary: #334155;
            --glass-bg: rgba(30, 41, 59, 0.8);
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
        }
        
        .stApp {
            background: var(--bg-primary);
        }
        
        .main-container {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem;
            border: 1px solid var(--border-primary);
        }
        
        .chat-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .chat-subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        
        .chat-response {
            background: linear-gradient(145deg, var(--glass-bg), rgba(46, 57, 86, 0.9));
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            border: 1px solid var(--border-primary);
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        .stTextArea > div > div > textarea {
            background: var(--glass-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-size: 1rem !important;
        }
        
        .stSelectbox > div > div > div {
            background: var(--glass-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }
        
        .stButton > button {
            background: var(--accent-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.8rem 2rem !important;
            font-weight: 600 !important;
        }
        
        .katex {
            font-size: 1.2em !important;
            color: var(--accent-primary) !important;
        }
        
        .katex-display {
            margin: 1.5rem 0 !important;
            padding: 1rem !important;
            background: rgba(15, 23, 42, 0.4) !important;
            border-radius: 8px !important;
            border-left: 4px solid var(--accent-primary) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
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

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🧠 Physics GPT Chat")
    
    # Physics domains
    physics_domains = [
        "Classical Mechanics", "Quantum Mechanics", "Electromagnetism", 
        "Thermodynamics", "Statistical Mechanics", "Optics", "Nuclear Physics",
        "Particle Physics", "Solid State Physics", "Relativity", "Astrophysics",
        "Plasma Physics", "Biophysics", "Mathematical Physics", "Computational Physics"
    ]
    
    selected_domain = st.selectbox("Choose Physics Domain:", ["All Topics"] + physics_domains)
    
    st.markdown("---")
    
    # Chat settings
    st.markdown("### ⚙️ Chat Settings")
    
    explanation_style = st.selectbox(
        "Explanation Style:",
        ["Conversational & Detailed", "Step-by-Step Tutorial", "Quick Summary", "Research Deep-Dive"]
    )
    
    academic_level = st.selectbox(
        "Academic Level:",
        ["High School", "Undergraduate", "Graduate", "Research", "Auto-Detect"]
    )
    
    include_examples = st.checkbox("Include numerical examples", value=True)
    include_applications = st.checkbox("Include real-world applications", value=True)
    
    st.markdown("---")
    
    # File upload
    st.markdown("### 📁 Reference Materials")
    uploaded_file = st.file_uploader("Upload PDF/DOCX:", type=["pdf", "docx"])
    reference_url = st.text_input("Reference URL:")

# --- Main Chat Interface ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="chat-title">🧠 Physics GPT</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">Your friendly AI physics tutor by Sreekesh M</div>', unsafe_allow_html=True)

# Chat input
user_question = st.text_area(
    "💬 Ask me anything about physics:",
    placeholder="e.g., Explain quantum entanglement, derive the Schrödinger equation, or help me understand relativity...",
    height=120,
    key="physics_chat_input"
)

# Submit button
if st.button("🚀 Ask Physics GPT", use_container_width=True):
    if user_question.strip():
        # Process context from uploaded files or URLs
        context = ""
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                context = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                context = extract_text_from_docx(uploaded_file)
        elif reference_url:
            context = extract_text_from_url(reference_url)
        
        # Limit context length
        if len(context) > 3000:
            context = context[:3000] + "\n...[Content truncated]"
        
        # Construct the chat prompt
        chat_prompt = f"""
Domain Focus: {selected_domain}
Explanation Style: {explanation_style}
Academic Level: {academic_level}
Include Examples: {'Yes' if include_examples else 'No'}
Include Applications: {'Yes' if include_applications else 'No'}

{f"Reference Context: {context}" if context else ""}

Question: {user_question}

Please respond in a friendly, conversational manner like ChatGPT, but with deep physics expertise. Use LaTeX for equations and provide clear, engaging explanations.
"""
        
        # Generate response
        with st.spinner("🧠 Physics GPT is thinking..."):
            try:
                llm = get_llm()
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_PROMPT),
                    ("human", "{question}")
                ])
                chain = LLMChain(llm=llm, prompt=prompt_template)
                response = chain.run({"question": chat_prompt})
                
                # Display response
                st.markdown('<div class="chat-response">', unsafe_allow_html=True)
                st.markdown("### 🧠 Physics GPT Response:")
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        st.warning("Please enter a physics question!")

# Quick physics topics
st.markdown("### 🌟 Quick Physics Topics")
col1, col2, col3, col4 = st.columns(4)

quick_topics = [
    "Quantum Mechanics", "Relativity", "Electromagnetism", "Thermodynamics",
    "Nuclear Physics", "Particle Physics", "Optics", "Solid State",
    "Astrophysics", "Plasma Physics", "Biophysics", "Chaos Theory"
]

for i, topic in enumerate(quick_topics):
    col = [col1, col2, col3, col4][i % 4]
    with col:
        if st.button(topic, key=f"quick_{i}"):
            st.session_state.physics_chat_input = f"Explain {topic} in detail with examples and applications"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; padding: 1rem;">
    🧠 <strong>Physics GPT</strong> - ChatGPT-style AI Physics Tutor<br>
    <em>Created by <strong>Sreekesh M</strong></em><br>
    🌟 Friendly • Knowledgeable • Always Ready to Help
</div>
""", unsafe_allow_html=True)
