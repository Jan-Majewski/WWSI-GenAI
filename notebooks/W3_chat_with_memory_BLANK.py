import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")

# File path for our memory storage
MEMORY_FILE = "conversation_memory.json"

def initialize_memory_file():
    """Initialize the JSON memory file if it doesn't exist"""
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w') as file:
            json.dump({}, file)

def get_conversation_history(conversation_id: str) -> List[Dict[str, str]]:
    """
    Retrieve conversation history for a given conversation ID
    
    Args:
        conversation_id: The unique ID for the conversation
    
    Returns:
        List of message dictionaries
    """
    initialize_memory_file()
    
    try:
        with open(MEMORY_FILE, 'r') as file:
            all_conversations = json.load(file)
            
        # Return the conversation history or empty list if not found
        return all_conversations.get(conversation_id, [])
    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}")
        return []

def save_conversation(conversation_id: str, messages: List[Dict[str, str]]):
    """
    Save conversation history to the JSON file
    
    Args:
        conversation_id: The unique ID for the conversation
        messages: List of message dictionaries
    """
    initialize_memory_file()

    ##TODO: open MEMORY_FILE, add new record with conversation_id as key and messages as value
    try:
        # Read existing conversations
        with open(MEMORY_FILE, 'r') as file:
            all_conversations = json.load(file)
        
        # Update with new messages
        all_conversations[conversation_id] = messages
        
        # Write back to file
        with open(MEMORY_FILE, 'w') as file:
            json.dump(all_conversations, file, indent=2)
            
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")

def format_messages_for_prompt(messages: List[Dict[str, str]]):
    """Convert stored messages to LangChain message format"""
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "human":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            formatted_messages.append(AIMessage(content=msg["content"]))
    return formatted_messages

# Prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """You are a helpful, friendly assistant that can answer general questions.
         You should maintain a consistent personality throughout the conversation.
         You should remember details the user has told you earlier in the conversation.
         
         If the user asks about personal preferences or opinions, you should provide thoughtful responses
         while acknowledging these are simulated preferences.
         
         If the user asks for harmful, illegal, unethical or deceptive information, 
         politely decline to provide such information.
         """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

def chatbot_response(user_input: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a response from the chatbot with memory
    
    Args:
        user_input: The user's query
        conversation_id: Optional ID to maintain conversation context
                         If None, a new conversation will be started
    
    Returns:
        Dictionary with response and conversation_id
    """
    # Generate a new conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())[:8]
    
    # Get conversation history
    messages = get_conversation_history(conversation_id)
    

    ##TODO: extract formatted history with format_messages_for_prompt function
    # Format messages for the prompt
    formatted_history = format_messages_for_prompt(messages)

    # Add user message to history
    
    
    
    # Generate response
    ##TODO: Combine prompt and llm to create a chain, invoke it with chat_history and input arguments

    chain = prompt | llm
    response = chain.invoke({"input":user_input, "chat_history": formatted_history})
    
    # Add AI response to history
    ##TODO: append AI response to messages list, select role from `ai`, `system` or `human`, use datetime.now for timestamp
    messages.append({"role": "human", "content": user_input, "timestamp": datetime.now().isoformat()})
    messages.append({"role": 'ai', "content": response.content, "timestamp": datetime.now().isoformat()})
    
    # Save updated conversation
    save_conversation(conversation_id, messages)
    
    return {
        "response": response.content,
        "conversation_id": conversation_id
    }

if __name__ == "__main__":
    # Example of a new conversation
    message1 = "Hi, my name is Alice. How are you today?"
    result = chatbot_response(message1)
    print(f"Conversation ID: {result['conversation_id']}")
    print(f"Human: {message1}")
    print(f"AI: {result['response']}\n")
    
    # Continue the same conversation
    conv_id = result['conversation_id']
    message2 = "I'm planning a trip to Spain next month. Have you been there?"
    result2 = chatbot_response( message2, conv_id)
    print(f"Human: {message2}")
    print(f"AI: {result2['response']}\n")
    
    
    # Ask something related to earlier information
    message3="Can you remind me what my name is?"
    result3 = chatbot_response(message3, conv_id)
    print(f"Human: {message3}")
    print(f"AI: {result3['response']}\n")