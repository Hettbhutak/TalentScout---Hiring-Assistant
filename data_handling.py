"""
Data handling module for TalentScout Hiring Assistant.
This module contains functions for extracting, validating, and storing candidate information.
"""

import re
import json
from datetime import datetime
import os
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional

# Define data models
class CandidateInfo(BaseModel):
    """Pydantic model for candidate information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    experience: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None
    
    # Validators
    @validator('email')
    def validate_email(cls, v):
        if v:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove non-numeric characters for validation
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

class ConversationRecord(BaseModel):
    """Pydantic model for conversation records."""
    timestamp: str
    candidate_info: CandidateInfo
    conversation: List[str]
    technical_questions: List[str]

def extract_candidate_info(user_input, current_info, current_stage):
    """
    Extract candidate information from user input.
    
    Args:
        user_input (str): The user's input text.
        current_info (dict): Current candidate information.
        current_stage (str): Current conversation stage.
        
    Returns:
        dict: Updated candidate information.
    """
    info = current_info.copy()
    
    # Only try to extract if we're in the appropriate stages
    if current_stage not in ["greeting", "collecting_info", "tech_stack_confirmation"]:
        return info
    
    # Extract name from greeting response
    if current_stage == "greeting" and not info["name"]:
        # Simple extraction - assumes the user has provided their name
        words = user_input.strip().split()
        if len(words) >= 1:
            # Take up to 3 words as the name, avoiding single word responses that might not be names
            potential_name = " ".join(words[:3])
            if len(potential_name) > 2 and not any(exit_word in potential_name.lower() for exit_word in ["hi", "hello", "hey"]):
                info["name"] = potential_name
    
    # Look for email patterns
    if not info["email"] and "@" in user_input and "." in user_input:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, user_input)
        if email_matches:
            info["email"] = email_matches[0]
    
    # Look for phone patterns
    if not info["phone"] and any(c.isdigit() for c in user_input):
        # This pattern looks for sequences of digits, possibly separated by spaces, dashes, or parentheses
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phone_matches = re.findall(phone_pattern, user_input)
        if phone_matches:
            info["phone"] = phone_matches[0]
    
    # Look for years of experience
    if not info["experience"] and any(c.isdigit() for c in user_input):
        # Look for patterns like "X years" or "X+ years"
        exp_patterns = [
            r'(\d+)[\+]?\s*years?',
            r'(\d+)[\+]?\s*yrs',
            r'(\d+)[\+]?\s*y\.?e\.?'
        ]
        
        for pattern in exp_patterns:
            exp_matches = re.findall(pattern, user_input.lower())
            if exp_matches:
                info["experience"] = f"{exp_matches[0]} years"
                break
    
    # For position and location, we'll use simpler heuristics
    words = user_input.strip().split()
    
    # Look for common job titles if not already captured
    if not info["position"] and len(words) >= 2:
        job_titles = ["developer", "engineer", "analyst", "manager", "designer", 
                      "architect", "consultant", "specialist", "administrator"]
        for title in job_titles:
            if title in user_input.lower():
                # Get a window around the job title
                index = user_input.lower().find(title)
                start = max(0, index - 20)
                end = min(len(user_input), index + 30)
                info["position"] = user_input[start:end].strip()
                break
    
    # Tech stack would be too complex for regex, will rely on the conversation flow
    if not info["tech_stack"] and current_stage == "collecting_info" and len(user_input.split()) >= 3:
        # This is a very simplified approach - in reality, you'd want more sophisticated tech stack parsing
        tech_keywords = ["python", "java", "javascript", "js", "typescript", "ts", "c#", "c++", 
                        "ruby", "php", "go", "rust", "swift", "kotlin", "react", "angular", 
                        "vue", "node", "django", "flask", "spring", "rails", "laravel", 
                        "aws", "azure", "gcp", "sql", "nosql", "mongodb", "mysql", 
                        "postgresql", "oracle", "docker", "kubernetes", "devops", "ml", 
                        "ai", "data science", "frontend", "backend", "fullstack"]
        
        found_techs = []
        for tech in tech_keywords:
            if tech in user_input.lower():
                found_techs.append(tech)
        
        if found_techs:
            info["tech_stack"] = ", ".join(found_techs)
    
    return info

def save_conversation(candidate_info, messages, technical_questions):
    """
    Save the conversation for review.
    
    Args:
        candidate_info (dict): Candidate information.
        messages (list): List of conversation messages.
        technical_questions (list): List of technical questions asked.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create a record of the conversation
        conversation_record = ConversationRecord(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            candidate_info=candidate_info,
            conversation=messages,
            technical_questions=technical_questions
        )
        
        # Generate a filename based on the candidate's name and timestamp
        name_part = candidate_info.get("name", "unknown").lower().replace(" ", "_")
        timestamp_part = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/conversation_{name_part}_{timestamp_part}.json"
        
        # Save to file
        with open(filename, "w") as f:
            f.write(conversation_record.json(indent=2))
        
        return True
        
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")
        return False
