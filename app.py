import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Import our custom modules
from prompt_engineering import get_system_prompt, get_tech_questions_prompt
from data_handling import extract_candidate_info, save_conversation
from llm_integration import get_chatbot_response, generate_technical_questions

# Load environment variables from .env file
load_dotenv()

# Set page config
st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="👔",
    layout="centered"
)

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {
        "name": None,
        "email": None,
        "phone": None,
        "experience": None,
        "position": None,
        "location": None,
        "tech_stack": None
    }

if "current_stage" not in st.session_state:
    st.session_state.current_stage = "greeting"

if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False

def process_user_input(user_input):
    """
    Process the user's input and generate a response.
    
    Args:
        user_input (str): The user's input text.
        
    Returns:
        str: The chatbot's response.
    """
    if st.session_state.conversation_ended:
        return "The conversation has ended. Please refresh the page to start a new session."
    
    # Check for conversation-ending keywords
    exit_keywords = ["exit", "quit", "bye", "goodbye", "end", "stop"]
    if any(keyword in user_input.lower() for keyword in exit_keywords) and st.session_state.current_stage != "farewell":
        st.session_state.current_stage = "farewell"
        return end_conversation()
    
    # Extract candidate information from the conversation
    st.session_state.candidate_info = extract_candidate_info(
        user_input, 
        st.session_state.candidate_info, 
        st.session_state.current_stage
    )
    
    # Prepare conversation history for context
    conversation_history = "\n".join([f"{'Bot' if i % 2 == 0 else 'User'}: {msg}" for i, msg in enumerate(st.session_state.messages)])
    
    # Prepare the system prompt based on the current stage
    system_prompt = get_system_prompt(st.session_state.current_stage)
    
    # Prepare user information context
    user_info_context = get_user_info_context()
    
    # Create messages for API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": user_info_context},
        {"role": "system", "content": f"Current conversation stage: {st.session_state.current_stage}"},
        {"role": "system", "content": f"Previous conversation:\n{conversation_history}"}
    ]
    
    # Add tech questions context if available
    if st.session_state.tech_questions and st.session_state.current_stage == "technical_questions":
        tech_questions_context = "Technical questions to ask:\n"
        for i, q in enumerate(st.session_state.tech_questions):
            tech_questions_context += f"{i+1}. {q}\n"
        
        tech_questions_context += f"\nCurrent question index: {st.session_state.question_index}"
        messages.append({"role": "system", "content": tech_questions_context})
    
    # Add the user's latest input
    messages.append({"role": "user", "content": user_input})
    
    # Get response from the LLM
    assistant_response = get_chatbot_response(messages)
    
    # Handle stage transitions
    assistant_response = handle_stage_transitions(assistant_response, user_input)
    
    return assistant_response

def get_user_info_context():
    """Generate context string with the candidate's information."""
    info = st.session_state.candidate_info
    context = "Candidate Information:\n"
    
    for key, value in info.items():
        if value:
            formatted_key = key.replace("_", " ").capitalize()
            context += f"- {formatted_key}: {value}\n"
    
    return context

def handle_stage_transitions(assistant_response, user_input):
    """
    Handle transitions between conversation stages.
    
    Args:
        assistant_response (str): The assistant's response.
        user_input (str): The user's input text.
        
    Returns:
        str: The potentially modified assistant response.
    """
    current_stage = st.session_state.current_stage
    info = st.session_state.candidate_info
    
    # First message from user (greeting)
    if current_stage == "greeting" and user_input.lower().strip() == "hey":
        st.session_state.current_stage = "collecting_name"
        return "Hello! I'm TalentScout, an AI hiring assistant. I'll be conducting your initial screening interview. Could you please tell me your full name?"
    
    # Handle name collection
    elif current_stage == "greeting" and info["name"]:
        st.session_state.current_stage = "collecting_email"
        return f"Thank you, {info['name']}! What's your email address?"
    
    # Handle email collection
    elif current_stage == "collecting_email" and info["email"]:
        st.session_state.current_stage = "collecting_phone"
        return f"Great! Now, could you please provide your phone number?"
    
    # Handle phone collection
    elif current_stage == "collecting_phone" and info["phone"]:
        st.session_state.current_stage = "collecting_position"
        return f"Thanks! What area or position would you like to work in? (e.g., Web Development, Data Science, DevOps, etc.)"
    
    # Handle position collection
    elif current_stage == "collecting_position" and info["position"]:
        st.session_state.current_stage = "collecting_experience"
        return f"Got it! How many years of experience do you have in {info['position']}?"
    
    # Handle experience collection
    elif current_stage == "collecting_experience" and info["experience"]:
        st.session_state.current_stage = "collecting_tech_stack"
        
        # Customize the tech stack question based on the position
        position = info["position"].lower()
        tech_question = "Please list your technical skills relevant to this position. "
        
        if "web" in position or "front" in position:
            tech_question += "For example: HTML, CSS, JavaScript, React, Angular, Vue, etc."
        elif "back" in position:
            tech_question += "For example: Node.js, Python, Java, PHP, Ruby, databases, etc."
        elif "data" in position:
            tech_question += "For example: Python, R, SQL, Pandas, Matplotlib, machine learning libraries, etc."
        elif "devops" in position:
            tech_question += "For example: Docker, Kubernetes, AWS, CI/CD, Linux, etc."
        elif "mobile" in position:
            tech_question += "For example: Swift, Kotlin, React Native, Flutter, etc."
        else:
            tech_question += "For example: programming languages, frameworks, tools, and technologies you're proficient in."
        
        return f"Thank you! {tech_question}"
    
    # Handle tech stack collection and generate questions
    elif current_stage == "collecting_tech_stack" and info["tech_stack"]:
        st.session_state.current_stage = "tech_stack_confirmation"
        return f"Thank you for sharing your skills in {info['tech_stack']}. Is there anything else you'd like to add before we move on to some technical questions?"
    
    # Generate technical questions based on tech stack and position
    elif current_stage == "tech_stack_confirmation" and not st.session_state.tech_questions:
        # Generate questions based on both position and tech stack
        position_context = f"Position: {info['position']}" if info['position'] else ""
        st.session_state.tech_questions = generate_technical_questions(
            f"{position_context} Tech stack: {info['tech_stack']}"
        )
        st.session_state.current_stage = "technical_questions"
        
        return f"Great! Now I'll ask you some technical questions based on your experience.\n\n{st.session_state.tech_questions[0]}"
    
    # Handle technical questions progression
    elif current_stage == "technical_questions":
        # Move to the next question or end the technical questions
        st.session_state.question_index += 1
        if st.session_state.question_index < len(st.session_state.tech_questions):
            return f"Thank you for your answer. Next question:\n\n{st.session_state.tech_questions[st.session_state.question_index]}"
        else:
            st.session_state.current_stage = "farewell"
            return end_conversation()
    
    return assistant_response

def end_conversation():
    """End the conversation and provide closing message."""
    st.session_state.conversation_ended = True
    
    # Prepare closing message
    closing_message = f"""Thank you for taking the time to chat with me, {st.session_state.candidate_info['name'] or 'candidate'}! 

I've collected your information and technical responses, which will be reviewed by our recruitment team. If your profile matches any of our current openings, a recruiter will contact you at {st.session_state.candidate_info['email'] or 'your email address'} or {st.session_state.candidate_info['phone'] or 'your phone number'} for the next steps in the process.

Best of luck with your job search, and we hope to speak with you again soon!

- TalentScout Hiring Assistant"""
    
    # Save conversation to a file
    save_conversation(
        st.session_state.candidate_info,
        st.session_state.messages,
        st.session_state.tech_questions
    )
    
    return closing_message

# UI Elements
st.title("👔 TalentScout")
st.subheader("Intelligent Hiring Assistant")

# Display chat messages
for message in st.session_state.messages:
    if message.startswith("TalentScout:"):
        st.markdown(f"**Assistant**: {message.replace('TalentScout: ', '')}")
    else:
        st.markdown(f"**You**: {message.replace('You: ', '')}")

# Handle user input
if "user_input_key" not in st.session_state:
    st.session_state.user_input_key = "user_input_" + str(len(st.session_state.messages))

user_input = st.text_input("Type your message here...", key=st.session_state.user_input_key)
send_button = st.button("Send")

if send_button and user_input:
    # Add user message to chat history
    user_message = f"You: {user_input}"
    st.session_state.messages.append(user_message)
    
    # Get and display bot response
    response = process_user_input(user_input)
    bot_message = f"TalentScout: {response}"
    st.session_state.messages.append(bot_message)
    
    # Create a new key for the text input to clear it
    st.session_state.user_input_key = "user_input_" + str(len(st.session_state.messages))
    
    # Force a rerun to update the chat history display
    st.experimental_rerun()

# Initialize the conversation if it's empty
if not st.session_state.messages:
    # Simulate initial greeting from the bot
    initial_greeting = """Hello! I'm TalentScout, an AI hiring assistant for tech positions. 

I'll be conducting your initial screening interview to learn more about your background and technical skills. 

To get started, could you please tell me your full name?"""
    
    st.session_state.messages.append(f"TalentScout: {initial_greeting}")
    st.markdown(f"**Assistant**: {initial_greeting}")

# Add some information at the bottom of the page
with st.expander("About TalentScout"):
    st.write("""
    TalentScout is an intelligent hiring assistant designed to help with the initial screening of candidates for tech positions.
    
    This chatbot will collect your basic information and ask technical questions related to your expertise.
    All information is handled securely and in compliance with data privacy standards.
    
    To end the conversation at any time, simply type 'exit', 'quit', or 'goodbye'.
    """)
