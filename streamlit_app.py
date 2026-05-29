import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import subprocess
import uuid
import os

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# GROQ CLIENT
# =========================
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# =========================
# STREAMLIT PAGE SETTINGS
# =========================
st.set_page_config(
    page_title="AI Software Development Agent",
    page_icon="🤖",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("⚡ AI Agent")

    st.markdown("---")

    st.write("### Features")
    st.write("✅ AI Chat")
    st.write("✅ PDF Analysis")
    st.write("✅ Code Generator")
    st.write("✅ Bug Fixer")
    st.write("✅ Code Explainer")
    st.write("✅ Code Runner")

    st.markdown("---")

    # =========================
    # MODE SELECTION
    # =========================
    mode = st.selectbox(
        "Choose AI Mode",
        [
            "Code Generator",
            "Bug Fixer",
            "Code Explainer",
            "PDF Summarizer",
            "Code Runner"
        ]
    )

    # =========================
    # MODEL SELECTION
    # =========================
    model_name = st.selectbox(
        "Choose Model",
        [
            "llama-3.3-70b-versatile"
        ]
    )

    # =========================
    # CLEAR CHAT
    # =========================
    if st.button("Clear Chat"):

        st.session_state.messages = []
        st.session_state.file_text = ""

        st.rerun()

# =========================
# MAIN TITLE
# =========================
st.title("🤖 AI Software Development Agent")

# =========================
# FILE UPLOADER
# =========================
uploaded_file = st.file_uploader(
    "Upload Python or PDF File",
    type=["py", "pdf"]
)

# =========================
# STORE FILE CONTENT
# =========================
file_text = ""

# =========================
# READ FILE
# =========================
if uploaded_file:

    # =========================
    # PDF FILE
    # =========================
    if uploaded_file.name.endswith(".pdf"):

        try:

            pdf_reader = PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                text = page.extract_text()

                if text:
                    file_text += text

        except Exception as e:

            st.error(f"PDF Error: {e}")

    # =========================
    # PYTHON FILE
    # =========================
    else:

        try:

            file_text = uploaded_file.read().decode("utf-8")

        except Exception as e:

            st.error(f"File Error: {e}")

    # =========================
    # LIMIT LARGE FILES
    # =========================
    if len(file_text) > 5000:

        st.warning(
            "Large file detected. "
            "Using first 5000 characters only."
        )

        file_text = file_text[:5000]

    # SAVE FILE TEXT TO SESSION
    st.session_state.file_text = file_text

    # =========================
    # SHOW FILE CONTENT
    # =========================
    st.subheader("📄 Uploaded File Content")

    st.text_area(
        "Content",
        file_text,
        height=300
    )

    # =========================
    # ANALYZE FILE BUTTON
    # =========================
    if st.button("Analyze File"):

        with st.spinner("Analyzing File..."):

            # =========================
            # SYSTEM PROMPTS
            # =========================
            if mode == "Code Generator":

                system_prompt = (
                    "Generate clean professional Python code."
                )

            elif mode == "Bug Fixer":

                system_prompt = (
                    "Find and fix bugs in the code."
                )

            elif mode == "Code Explainer":

                system_prompt = (
                    "Explain the code clearly for beginners."
                )

            elif mode == "PDF Summarizer":

                system_prompt = (
                    "Summarize the uploaded PDF clearly."
                )

            elif mode == "Code Runner":

                system_prompt = (
                    "Generate ONLY executable Python code.\n"
                    "Do not explain anything.\n"
                    "Return only code."
                )

            else:

                system_prompt = (
                    "You are an expert AI assistant."
                )

            # =========================
            # AI RESPONSE
            # =========================
            try:

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": file_text
                        }
                    ]
                )

                result = response.choices[0].message.content

                st.subheader("🤖 AI Response")

                # =========================
                # SHOW CODE OUTPUT
                # =========================
                if mode in [
                    "Code Generator",
                    "Bug Fixer",
                    "Code Runner"
                ]:

                    st.code(result, language="python")

                else:

                    st.write(result)

            except Exception as e:

                st.error(f"API Error: {e}")

# =========================
# CHAT HISTORY
# =========================
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =========================
# CHAT INPUT
# =========================
prompt = st.chat_input(
    "Ask coding questions..."
)

# =========================
# HANDLE USER INPUT
# =========================
if prompt:

    # SAVE USER MESSAGE
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # SHOW USER MESSAGE
    with st.chat_message("user"):

        st.markdown(prompt)

    # =========================
    # SYSTEM PROMPTS
    # =========================
    if mode == "Code Generator":

        system_prompt = (
            "Generate clean professional Python code."
        )

    elif mode == "Bug Fixer":

        system_prompt = (
            "Find and fix bugs in the code."
        )

    elif mode == "Code Explainer":

        system_prompt = (
            "Explain code clearly for beginners."
        )

    elif mode == "PDF Summarizer":

        system_prompt = (
            "Answer questions based on uploaded PDF."
        )

    elif mode == "Code Runner":

        system_prompt = (
            "Generate ONLY executable Python code.\n"
            "Return only code."
        )

    else:

        system_prompt = (
            "You are an expert AI assistant."
        )

    # =========================
    # AI RESPONSE
    # =========================
    try:

        full_prompt = prompt

        # =========================
        # ADD PDF CONTEXT
        # =========================
        if st.session_state.file_text:

            full_prompt = (
                f"PDF Content:\n"
                f"{st.session_state.file_text}\n\n"
                f"User Question:\n{prompt}"
            )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )

        ai_response = response.choices[0].message.content

    except Exception as e:

        st.error(f"API Error: {e}")

        ai_response = ""

    # =========================
    # CODE RUNNER
    # =========================
    if mode == "Code Runner" and ai_response:

        try:

            # CREATE FOLDER
            os.makedirs(
                "generated_code",
                exist_ok=True
            )

            # UNIQUE FILE NAME
            filename = (
                f"generated_code/"
                f"{uuid.uuid4().hex}.py"
            )

            # CLEAN CODE
            clean_code = (
                ai_response
                .replace("```python", "")
                .replace("```", "")
            )

            # SAVE FILE
            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(clean_code)

            # RUN PYTHON FILE
            result = subprocess.run(
                ["python", filename],
                capture_output=True,
                text=True,
                timeout=10
            )

            # SHOW OUTPUT
            st.subheader("▶ Code Output")

            if result.stdout:

                st.code(result.stdout)

            if result.stderr:

                st.error(result.stderr)

        except subprocess.TimeoutExpired:

            st.error("Execution Timed Out")

        except Exception as e:

            st.error(f"Execution Error: {e}")

    # =========================
    # SAVE AI MESSAGE
    # =========================
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )

    # =========================
    # SHOW AI RESPONSE
    # =========================
    with st.chat_message("assistant"):

        if mode in [
            "Code Generator",
            "Bug Fixer",
            "Code Runner"
        ]:

            st.code(ai_response, language="python")

        else:

            st.markdown(ai_response)