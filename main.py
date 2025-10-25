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
    page_icon="🔬", 
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f6fa;
        }
        .main-title {
            text-align: center;
            font-size: 2.2rem;
            color: #333333;
            margin-bottom: 1rem;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        .stButton > button {
            width: 100%;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem;
            font-size: 1rem;
            font-weight: 600;
            margin-top: 1rem;
        }
        .stButton > button:hover {
            background-color: #0052a3;
        }
        div[data-testid="stMarkdownContainer"] > div.answer-box {
            background-color: white;
            border: 1px solid #dddddd;
            border-radius: 12px;
            padding: 1.2rem;
            font-size: 1.05rem;
            color: #111;
            line-height: 1.6;
            margin-top: 1.5rem;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown(
    '<div class="main-title">🧠 Physics Tutor by Sreekesh M</div>', 
    unsafe_allow_html=True
)

# --- Session State for Chat History (Optional Enhancement) ---
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
            
            # Modern LCEL chain (replaces deprecated LLMChain)
            output_parser = StrOutputParser()
            chain = prompt | llm | output_parser
            
            # Invoke the chain
            response = chain.invoke({"question": query})
            
            # Store in session state (optional)
            st.session_state.messages.append({
                "question": query,
                "answer": response
            })
            
            # Display the response
            st.markdown("### 📖 Answer:")
            
            # Use st.write for proper LaTeX rendering
            st.write(response)
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and internet connection.")

# --- Optional: Display Chat History ---
if st.session_state.messages:
    with st.expander("📚 View Previous Questions", expanded=False):
        for i, msg in enumerate(reversed(st.session_state.messages[:-1]), 1):
            st.markdown(f"**Q{i}:** {msg['question']}")
            st.markdown(f"*A:* {msg['answer'][:200]}...")
            st.divider()
