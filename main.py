# Compatibility fix for older code paths that might check these attributes
import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False

import re
import streamlit as st
from groq_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# -------- Theory-only System Prompt (no equations, no LaTeX) --------
SYSTEM_PROMPT_CONCEPTS = """
You are a highly intelligent and professional Physics Tutor for IIT‑JAM, CSIR‑NET, and GATE Physics.

Answer using theory statements only:
- Do not include equations, LaTeX, symbols, or derivations.
- Avoid mathematical notation such as equals signs, integrals, gradients, vectors, subscripts, superscripts, or Greek symbols.
- Use plain language descriptions of laws, definitions, assumptions, boundary conditions, and qualitative trends.
- When a calculation is requested, explain the conceptual method and the reasoning steps in words without writing formulas or numbers connected by operators.
- Keep explanations concise, syllabus-aligned, and focused on intuition, physical meaning, and exam-useful insights.
- Highlight symmetry, applicable conditions, limitations, and common pitfalls in words.
- If the user asks for formulas, politely summarize the idea in words and do not print any formula.

Tone: clear, structured, and suitable for high-scoring preparation. Use short paragraphs and bullet points. Avoid any mathematical markup.
"""


# -------- Post-processor to remove any math/notation that slips through --------
MATH_PATTERNS = [
    r"\$\$[\s\S]*?\$\$",        # $$ ... $$
    r"\\\[([\s\S]*?)\\\]",      # \[ ... \]
    r"\$(?!\$)[\s\S]*?\$",      # $ ... $
    r"\\\(([\s\S]*?)\\\)",      # \( ... \)
    r"``````",     # fenced latex blocks
    r"\\[a-zA-Z]+(\{[^{}]*\})*",# LaTeX commands like \frac{...}{...}, \alpha etc.
    r"[∇∂±≈≃≅≡≤≥×·∙⋅∞ΣΠ∫∮∇→←↔^_{}]", # common math symbols
]

MATH_REGEX = re.compile("|".join(MATH_PATTERNS))

OPS_REGEX = re.compile(r"(\s[=+\-/*^><≈≃≅≤≥]+|\b\d+\s*[/^*+\-]\s*\d+)")
EXTRA_SPACES = re.compile(r"\n{3,}")

def strip_math(text: str) -> str:
    s = text.replace("\r\n", "\n")
    s = MATH_REGEX.sub("", s)
    s = OPS_REGEX.sub(" ", s)             # remove operator-like fragments
    s = s.replace("{}", "")               # leftover braces
    s = EXTRA_SPACES.sub("\n\n", s).strip()
    return s


# -------- UI configuration (dark, minimal, no LaTeX loaders) --------
st.set_page_config(
    page_title="🧠 Physics Tutor – Theory Only",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
        #MainMenu, footer, header { visibility: hidden; }
        .main-title {
            text-align: center; font-size: 2.4rem; font-weight: 700;
            background: linear-gradient(135deg, #67e8f9 0%, #a78bfa 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin: 1rem 0 1.5rem 0;
        }
        .stForm {
            background: rgba(26,31,46,0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102,126,234,0.25);
            border-radius: 16px; padding: 1.6rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        }
        .stTextInput > div > div > input {
            background-color: #1a1f2e !important;
            border: 2px solid rgba(102,126,234,0.35) !important;
            border-radius: 12px !important;
            padding: 0.85rem 1rem !important;
            color: #e2e8f0 !important; transition: all 0.2s ease !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #7dd3fc !important;
            box-shadow: 0 0 0 3px rgba(125,211,252,0.25) !important;
            background-color: #20263a !important;
        }
        .stButton > button {
            width: 100%; background: linear-gradient(135deg, #67e8f9 0%, #a78bfa 100%) !important;
            color: #0b1020 !important; border: none !important; border-radius: 12px !important;
            padding: 0.8rem 1.3rem !important; font-weight: 700 !important;
            box-shadow: 0 6px 18px rgba(103,232,249,0.28) !important;
        }
        .stButton > button:hover { transform: translateY(-1px); }
        .answer-box {
            background: rgba(26,31,46,0.82); border: 1px solid rgba(102,126,234,0.25);
            border-radius: 16px; padding: 1.2rem; color: #e5e7eb; line-height: 1.8;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35); margin-top: 1rem;
        }
        .answer-box h3 { color: #7dd3fc; border-bottom: 1px solid rgba(125,211,252,0.25); padding-bottom: .4rem; }
        .answer-box ul { margin-top: .25rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Physics Tutor (Theory Only)</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------- Input --------
with st.form(key="physics_form"):
    query = st.text_input(
        "📌 Enter your Physics question (theory-only):",
        placeholder="Explain Gauss's law conceptually (no equations).",
        key="question"
    )
    submit_button = st.form_submit_button("🚀 Get Theory Answer")


# -------- Run LLM and show theory-only output --------
if submit_button and query:
    with st.spinner("🧠 Thinking in concepts..."):
        try:
            llm = get_llm()

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT_CONCEPTS),
                ("human", "{question}")
            ])

            chain = prompt | llm | StrOutputParser()
            raw = chain.invoke({"question": query})

            theory_only = strip_math(raw)

            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown("### 📖 Theory Answer")
            st.markdown(theory_only)
            st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.messages.append({"question": query, "answer": theory_only})

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Tip: If you previously loaded a math renderer, remove it; this app intentionally strips equations.")


# -------- History --------
if st.session_state.messages:
    with st.expander("📚 View Previous Questions", expanded=False):
        for i, msg in enumerate(reversed(st.session_state.messages[:-1]), 1):
            st.markdown(f"**Q{i}:** {msg['question']}")
            st.markdown(msg["answer"][:280] + ("..." if len(msg["answer"]) > 280 else ""))
            st.divider()
