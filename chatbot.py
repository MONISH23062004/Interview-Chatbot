import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

# Setting up the Streamlit page configuration
st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="💬")
st.markdown(
    """
    <h1 style="
        text-align: center;
        background: linear-gradient(to right,
            blue,
            indigo,
            violet);
        -webkit-background-clip: text;
        color: transparent;
    ">
        AI Career Assistant 
    </h1>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []


# Helper
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True


# =======================
#   SETUP SCREEN
# =======================
if not st.session_state.setup_complete:
    st.subheader('Personal Information')

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input("Name", value=st.session_state["name"], max_chars=40)
    st.session_state["experience"] = st.text_area("Experience", value=st.session_state["experience"], max_chars=200)
    st.session_state["skills"] = st.text_area("Skills", value=st.session_state["skills"], max_chars=200)

    st.subheader('Company & Position')

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"],
        )
    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst",
             "Financial Analyst", "Software Engineer", "Frontend-Developer", "Backend-Developer")
        )

    st.session_state["company"] = st.selectbox(
        "Select a Company",
        ("Amazon", "Meta", "Udemy", "Tesla", "Nestle", "LinkedIn", "Spotify",
         "Flipkart", "Microsoft", "Apple"),
    )

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")


# =======================
#   INTERVIEW SCREEN
# =======================
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info("Start by introducing yourself 👋")

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"

    # Init system prompt once
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": (
                f"You are an HR interviewer. "
                f"Candidate name: {st.session_state['name']} "
                f"Experience: {st.session_state['experience']} "
                f"Skills: {st.session_state['skills']} "
                f"Interview for {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}. "
                f"Ask only ONE question at a time. "
                f"Ask ONLY 5 questions total. "
            )
        }]

    # replay chat
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # stop input if 5 user responses completed
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

    # main input
    if not st.session_state.chat_complete:
        if prompt := st.chat_input("Your response", max_chars=1000):

            # save user msg
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Only ask question if < 5 user turns completed
            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)

                st.session_state.messages.append({"role": "assistant", "content": response})

            # increment user count
            st.session_state.user_message_count += 1

    # block next questions
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True


# =======================
#   GET FEEDBACK
# =======================
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")


# =======================
#   FEEDBACK SCREEN
# =======================
if st.session_state.feedback_shown:
    st.subheader("Feedback")

    history = "\n".join([f"{msg['role']}: {msg['content']}"
                         for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback = feedback_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert HR evaluator.
                First line: Overall Score from 1–10.
                Then give feedback only. 
                No questions. No conversation.
                Format:
                Overall Score: x/10
                Feedback: ...
                """
            },
            {"role": "user", "content": history}
        ]
    )

    st.write(feedback.choices[0].message.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
