import streamlit as st
from groq_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# --- System Prompt ---
SYSTEM_PROMPT = """
You are a highly intelligent and professional Physics Tutor with expertise in competitive exams such as IIT-JAM, CSIR-NET, and GATE Physics. 

Your responsibilities:
- Provide conceptually sound, accurate, and syllabus-aligned explanations.
- Use step-by-step problem-solving, relevant equations, and mathematical derivations.
- Explain the underlying physics intuitively, building from first principles.
- Include real-world examples or analogies wherever helpful.
- Use LaTeX-style math formatting for clarity in equations (use $...$ for inline and $$...$$ for display equations).
- When appropriate, include graphs, diagrams, or brief derivations to aid understanding.
- Clearly state assumptions, boundary conditions, and approximations used in derivations or numerical solutions.
- Keep your answers focused on the question. Avoid philosophical, vague, or unrelated explanations.
- When multiple methods exist, briefly mention alternative approaches.

Respond in a teaching tone, suitable for students aiming for high scores in national-level physics exams.

Always assume the student has a basic undergraduate-level understanding of physics and mathematics, but may need guidance in advanced applications and exam tricks.

If a question is ambiguous, clearly state assumptions before answering.
"""


# --- Streamlit Config ---
st.set_page_config(
    page_title="🧠 Physics Tutor – JAM/NET/GATE", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Dark Theme CSS ---
st.markdown("""
    <style>
        /* Global dark theme */
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Title styling with gradient */
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 2rem;
            padding: 1rem;
            letter-spacing: 1px;
        }
        
        /* Form container */
        .stForm {
            background: rgba(26, 31, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Label styling */
        .stTextInput > label {
            color: #a0aec0 !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Input field - dark theme */
        .stTextInput > div > div > input {
            background-color: #1a1f2e !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 12px !important;
            padding: 0.875rem 1rem !important;
            font-size: 1rem !important;
            color: #e2e8f0 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
            background-color: #242938 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #4a5568 !important;
        }
        
        /* Button styling with gradient */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.875rem 1.5rem !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            margin-top: 1.25rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Answer container */
        div[data-testid="stMarkdownContainer"] {
            background: rgba(26, 31, 46, 0.8) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            margin-top: 2rem !important;
            color: #e2e8f0 !important;
            line-height: 1.8 !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Answer heading */
        div[data-testid="stMarkdownContainer"] h3 {
            color: #667eea !important;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3) !important;
            padding-bottom: 0.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Code blocks in answers */
        div[data-testid="stMarkdownContainer"] code {
            background-color: rgba(102, 126, 234, 0.1) !important;
            color: #a78bfa !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
        }
        
        /* LaTeX rendering */
        .katex {
            color: #e2e8f0 !important;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }
        
        /* Expander for history */
        .streamlit-expanderHeader {
            background-color: rgba(26, 31, 46, 0.6) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 12px !important;
            color: #e2e8f0 !important;
        }
        
        .streamlit-expanderContent {
            background-color: rgba(26, 31, 46, 0.4) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 0 0 12px 12px !important;
        }
        
        /* Divider */
        hr {
            border-color: rgba(102, 126, 234, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title with Brain Emoji ---
st.markdown(
    '<div class="main-title">🧠 Physics Tutor by Sreekesh M</div>', 
    unsafe_allow_html=True
)

# --- Session State for Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Form Input ---
with st.form(key="physics_form"):
    query = st.text_input(
        "📌 Enter your Physics question below:", 
        placeholder="e.g., Derive the Schrödinger equation.",
        key="question"
    )
    submit_button = st.form_submit_button("🚀 Get Answer")

# --- Generate Answer ---
if submit_button and query:
    with st.spinner("🧠 Thinking..."):
        try:
            # Get LLM from groq_config
            llm = get_llm()
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{question}")
            ])
            
            # Modern LCEL chain
            output_parser = StrOutputParser()
            chain = prompt | llm | output_parser
            
            # Invoke the chain
            response = chain.invoke({"question": query})
            
            # Store in session state
            st.session_state.messages.append({
                "question": query,
                "answer": response
            })
            
            # Display the response
            st.markdown("### 📖 Answer:")
            st.write(response)
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and internet connection.")

# --- Display Chat History ---
if st.session_state.messages:
    with st.expander("📚 View Previous Questions", expanded=False):
        for i, msg in enumerate(reversed(st.session_state.messages[:-1] if len(st.session_state.messages) > 1 else []), 1):
            st.markdown(f"**Q{i}:** {msg['question']}")
            with st.container():
                st.markdown(msg['answer'][:300] + "..." if len(msg['answer']) > 300 else msg['answer'])
            st.divider()
