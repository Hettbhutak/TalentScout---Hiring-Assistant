"""
LLM integration module for TalentScout Hiring Assistant.
This module handles interactions with the OpenAI API for generating responses and technical questions.
"""

import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OpenAI API key not found. Using mock responses for demo purposes.")
openai.api_key = api_key

def get_chatbot_response(messages, temperature=0.7, max_tokens=500):
    """
    Get a response from the OpenAI API.
    
    Args:
        messages (list): List of message objects for the API call.
        temperature (float): Controls randomness. Lower values make responses more deterministic.
        max_tokens (int): Maximum number of tokens to generate.
        
    Returns:
        str: The generated response.
    """
    if not openai.api_key:
        # If no API key is provided, return a mock response
        return get_mock_response(messages)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or another appropriate model
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the response text
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to mock response in case of API error
        return get_mock_response(messages)

def get_mock_response(messages):
    """
    Generate a mock response for demo purposes when OpenAI API is not available.
    
    Args:
        messages (list): List of message objects.
        
    Returns:
        str: A simulated response.
    """
    user_message = messages[-1]["content"].lower() if messages and messages[-1]["role"] == "user" else ""
    
    # Check conversation stage from context messages
    stage = "greeting"
    for msg in messages:
        if msg["role"] == "system" and "Current conversation stage:" in msg["content"]:
            stage = msg["content"].split("Current conversation stage:")[1].strip()
    
    # Simple responses based on common inputs and stage
    if "name" in user_message and stage == "greeting":
        return "Nice to meet you! Could you please share your email address so our team can contact you?"
    
    elif "email" in user_message and "@" in user_message:
        return "Thanks for your email. What's your phone number in case we need to reach you quickly?"
    
    elif any(term in user_message for term in ["phone", "number", "contact"]):
        return "Great! How many years of experience do you have in your field?"
    
    elif any(term in user_message for term in ["experience", "year", "worked"]):
        return "Thank you. What position are you currently looking for?"
    
    elif any(term in user_message for term in ["position", "job", "role", "looking for"]):
        return "Where are you currently located? We want to match you with opportunities in your area."
    
    elif any(term in user_message for term in ["location", "city", "area", "based"]):
        return "Please tell me about your tech stack. What programming languages, frameworks, and tools are you proficient in?"
    
    elif stage == "technical_questions":
        return "Thank you for your answer. That shows good understanding of the technology."
    
    elif "bye" in user_message or "exit" in user_message:
        return "Thank you for your time! Our recruitment team will review your information and get back to you soon if there's a match. Have a great day!"
    
    else:
        return "Thank you for that information. Is there anything else you'd like to share about your skills or experience?"

def generate_technical_questions(tech_stack, num_questions=5):
    """
    Generate technical questions based on the candidate's tech stack.
    
    Args:
        tech_stack (str): The candidate's tech stack.
        num_questions (int): Number of questions to generate (default: 5).
        
    Returns:
        list: List of generated technical questions.
    """
    if not tech_stack:
        return ["Could you tell me about your technical skills and experience?"]
    
    if not openai.api_key:
        # If no API key is provided, return mock questions
        return get_mock_technical_questions(tech_stack)
    
    # Prepare the prompt
    prompt = f"""You are an expert technical interviewer for a tech recruitment agency.
Generate {num_questions} technical questions to assess a candidate's proficiency in the specified tech stack.
The questions should be challenging but appropriate for an initial screening.
Each question should focus on a different aspect of the technology.
Format the output as a simple list of questions without any introductory text or numbering.

Tech stack: {tech_stack}"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or another appropriate model
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and format the questions
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        # Filter out anything that doesn't look like a question
        questions = [q for q in questions if q.endswith('?')]
        
        return questions if questions else [f"Could you explain your experience with {tech_stack}?"]
        
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return get_mock_technical_questions(tech_stack)

def get_mock_technical_questions(tech_stack):
    """
    Generate mock technical questions for demo purposes.
    
    Args:
        tech_stack (str): The candidate's tech stack.
        
    Returns:
        list: List of technical questions based on the tech stack.
    """
    tech_stack = tech_stack.lower()
    
    # Dictionary of predefined questions for common technologies
    tech_questions = {
        "python": [
            "Can you explain the difference between a list and a tuple in Python?",
            "How do you handle exceptions in Python?",
            "What is the difference between __init__ and __new__ in Python classes?",
            "How does memory management work in Python?",
            "Can you explain decorators and provide a use case?"
        ],
        "javascript": [
            "What's the difference between let, const, and var in JavaScript?",
            "Can you explain closures in JavaScript?",
            "How does prototypal inheritance work?",
            "What are Promises and how do they differ from callbacks?",
            "How would you optimize the performance of a JavaScript application?"
        ],
        "react": [
            "What is the virtual DOM in React and how does it work?",
            "Explain the component lifecycle in React.",
            "What's the difference between state and props?",
            "How do you handle side effects in React components?",
            "What are hooks and how have they changed React development?"
        ],
        "java": [
            "What is the difference between an interface and an abstract class in Java?",
            "How does garbage collection work in Java?",
            "Explain the principles of SOLID in Java.",
            "What are the new features introduced in Java 8?",
            "How would you handle concurrency in a Java application?"
        ],
        "sql": [
            "What's the difference between INNER JOIN and LEFT JOIN?",
            "How would you optimize a slow SQL query?",
            "Explain normalization and when you might denormalize a database.",
            "What are indexes and how do they work?",
            "How would you handle large dataset operations in SQL?"
        ],
        "aws": [
            "What AWS services would you use for a highly available web application?",
            "Explain the difference between EC2, ECS, and Lambda.",
            "How would you design a scalable architecture on AWS?",
            "What security best practices would you implement in AWS?",
            "How would you monitor and troubleshoot issues in an AWS environment?"
        ],
        "devops": [
            "Explain the CI/CD pipeline and its benefits.",
            "What containerization technologies have you worked with?",
            "How would you handle scaling in a microservices architecture?",
            "What monitoring and alerting tools have you used?",
            "How do you approach infrastructure as code?"
        ]
    }
    
    # Find matching technologies in the tech stack
    questions = []
    for tech, tech_qs in tech_questions.items():
        if tech in tech_stack:
            questions.extend(tech_qs)
    
    # If no specific questions found, return generic ones
    if not questions:
        return [
            f"Could you explain your experience with {tech_stack}?",
            f"What projects have you worked on using {tech_stack}?",
            f"What challenges have you faced when working with {tech_stack}?",
            f"How do you stay updated with the latest developments in {tech_stack}?",
            f"Can you describe a complex problem you solved using {tech_stack}?"
        ]
    
    # Return at most 5 questions
    return questions[:5]
