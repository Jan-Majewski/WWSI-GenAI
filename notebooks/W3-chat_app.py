import streamlit as st
import time
from W3_chat_with_memory import chatbot_response

# Set page configuration
st.set_page_config(
    page_title="AI Chat with Memory",
    page_icon="💬",
    layout="centered"
)

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .user-message {
        background-color: #e0f7fa;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
        float: right;
        clear: both;
    }
    .ai-message {
        background-color: #f5f5f5;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-start;
        float: left;
        clear: both;
    }
    .chat-container {
        padding: 20px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .message-container {
        width: 100%;
        overflow: hidden;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for conversation history and ID
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# App title
st.title("AI Chat Assistant")
st.subheader("Chat with an AI that remembers your conversation")

# Display the conversation ID if it exists
if st.session_state.conversation_id:
    st.sidebar.success(f"Conversation ID: {st.session_state.conversation_id}")

# Option to start a new conversation
if st.sidebar.button("Start New Conversation"):
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.rerun()

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    with st.container():
        if role == "human":
            st.markdown(f'<div class="message-container"><div class="user-message">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-container"><div class="ai-message">{content}</div></div>', unsafe_allow_html=True)

# Input for new message
with st.container():
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to the display
        st.session_state.messages.append({"role": "human", "content": user_input})
        
        # Create a placeholder for the AI's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Get response from the chatbot
            response = chatbot_response(user_input, st.session_state.conversation_id)
            
            # Save the conversation ID
            st.session_state.conversation_id = response["conversation_id"]
            
            # Add AI message to the display
            st.session_state.messages.append({"role": "ai", "content": response["response"]})
            
            # Display typing effect
            full_response = response["response"]
            simulated_response = ""
            
            for chunk in full_response.split():
                simulated_response += chunk + " "
                message_placeholder.markdown(simulated_response + "▌")
                time.sleep(0.05)
            
            # Show the final response
            message_placeholder.markdown(full_response)
        
        # Force a rerun to update the UI with the new messages
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "This chatbot uses LangChain with GPT-4o to provide responses "
    "and maintains conversation history in memory."
)