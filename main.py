import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
from chatbot_controller import ChatbotController

# Load environment variables from .env file
load_dotenv()

st.set_page_config(
    page_title="Technical Interview Chatbot",
    page_icon="💼",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "chat_controller" not in st.session_state:
        # Get API key from environment or Streamlit secrets
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        # For deployment, use Streamlit secrets
        if not api_key and hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            
        try:
            st.session_state.chat_controller = ChatbotController(api_key=api_key)
            st.session_state.chat_initialized = True
        except ValueError as e:
            st.session_state.chat_initialized = False
            st.session_state.init_error = str(e)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Add initial message from assistant
        if st.session_state.get("chat_initialized", False):
            initial_prompt = st.session_state.chat_controller.get_initial_prompt()
            st.session_state.messages.append({"role": "assistant", "content": initial_prompt})
    
    # Initialize typing state
    if "can_type" not in st.session_state:
        st.session_state.can_type = True

def main():
    st.title("Technical Interview Chatbot")
    
    initialize_session_state()
    
    # Check if chat could be initialized
    if not st.session_state.get("chat_initialized", False):
        st.error(f"Chat initialization failed: {st.session_state.get('init_error', 'Unknown error')}")
        
        with st.form(key="api_key_form"):
            api_key = st.text_input("Enter your Google API Key for Gemini:", type="password")
            submit_button = st.form_submit_button(label="Initialize Chatbot")
            
            if submit_button:
                try:
                    st.session_state.chat_controller = ChatbotController(api_key=api_key)
                    st.session_state.chat_initialized = True
                    st.session_state.messages = []  # Reset messages
                    initial_prompt = st.session_state.chat_controller.get_initial_prompt()
                    st.session_state.messages.append({"role": "assistant", "content": initial_prompt})
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to initialize with provided API key: {str(e)}")
        
        st.stop()
    
    # Create columns for layout
    col1, col2 = st.columns([7, 3])
    
    with col1:
        # Chat container
        chat_container = st.container(height=500)
        
        # Display chat messages
        with chat_container:
            for i, msg in enumerate(st.session_state.messages):
                message(msg["content"], is_user=msg["role"] == "user", key=f"msg_{i}")
        
        # User input area
        if st.session_state.get("can_type", True):
            user_input = st.chat_input("Type your response here...")
            
            if user_input:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.spinner("Processing..."):
                    # Get response from chatbot
                    response = st.session_state.chat_controller.process_user_input(user_input)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Check if interview is complete to display candidate info
                if st.session_state.chat_controller.is_interview_complete():
                    st.success("Interview completed!")
                    
                    # Display candidate information
                    candidate_info = st.session_state.chat_controller.get_candidate_info()
                    if candidate_info:
                        with st.expander("Candidate Information", expanded=True):
                            st.write("### Candidate Profile")
                            for key, value in candidate_info.items():
                                st.write(f"**{key.capitalize()}:** {value}")
                
                # Disable input if the interview is finished
                st.session_state.can_type = st.session_state.chat_controller.can_continue_typing()
                
                st.rerun()
        else:
            # Display a disabled input field
            st.text_input("Interview completed", "You can no longer type in this interview", disabled=True)
    
    with col2:
        # Controls and information section
        st.button("Reset Interview", on_click=reset_chat)
        
        # Display interview state for debugging
        interview_state = st.session_state.chat_controller.get_current_interview_state()
        
        # Show current interview progress
        st.write("### Interview Progress")
        current_step = interview_state["current_step"]
        if current_step in INTERVIEW_FLOW_KEYS:
            progress = (list(INTERVIEW_FLOW_KEYS).index(current_step) + 1) / len(INTERVIEW_FLOW_KEYS)
            st.progress(progress)
            st.write(f"Current step: **{current_step}**")
        elif current_step == "technical_questions":
            tech_stack = interview_state["tech_stack"]
            current_tech = interview_state["current_tech"]
            questions_asked = interview_state["questions_asked_for_current_tech"]
            
            if tech_stack:
                tech_progress = (tech_stack.index(current_tech)) / len(tech_stack)
                st.progress(tech_progress)
                st.write(f"Discussing technology: **{current_tech}**")
                st.write(f"Questions asked: {questions_asked}/3")
        elif current_step == "complete":
            st.progress(1.0)
            st.success("Interview completed!")
        
        # Show detected technologies
        if interview_state["tech_stack"]:
            st.write("### Detected Technologies")
            for tech in interview_state["tech_stack"]:
                st.write(f"- {tech}")
        
        with st.expander("About the Technical Interview Chatbot", expanded=False):
            st.write("""
            **Technical Interview Chatbot** is an AI-powered interviewer that:
            
            - Collects candidate information
            - Asks relevant technical questions based on the candidate's tech stack
            - Adapts questions based on previous responses
            - Provides a structured interview experience
            
            This tool helps conduct initial technical screening efficiently and consistently.
            """)

# Define interview flow keys for progress tracking
INTERVIEW_FLOW_KEYS = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]

def reset_chat():
    """Reset the chat session and messages."""
    if "chat_controller" in st.session_state:
        st.session_state.chat_controller.reset_chat()
    
    st.session_state.messages = []
    
    # Add initial message again
    if st.session_state.get("chat_initialized", False):
        initial_prompt = st.session_state.chat_controller.get_initial_prompt()
        st.session_state.messages.append({"role": "assistant", "content": initial_prompt})

if __name__ == "__main__":
    main()
