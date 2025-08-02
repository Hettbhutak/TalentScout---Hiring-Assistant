# TalentScout - Intelligent Hiring Assistant Chatbot

## Project Overview
TalentScout is an intelligent Hiring Assistant chatbot for a fictional recruitment agency specializing in technology placements. The chatbot assists in the initial screening of candidates by gathering essential information and posing relevant technical questions based on the candidate's declared tech stack.

## Features
- Greets candidates and provides a brief overview of its purpose
- Collects essential candidate details (name, email, phone, experience, desired position, location, tech stack)
- Generates 3-5 technical questions tailored to the candidate's tech stack
- Maintains context throughout the conversation
- Handles unexpected inputs with a fallback mechanism
- Gracefully concludes the conversation

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/TalentScout.git
   cd TalentScout
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage
1. Start the application:
   ```
   streamlit run app.py
   ```

2. The application will open in your default web browser at `http://localhost:8501`

3. Interact with the chatbot to simulate a candidate screening process

## Technical Details
- **Frontend**: Streamlit
- **Backend**: Python
- **LLM Integration**: OpenAI GPT model
- **Architecture**: The application follows a modular architecture with separate components for:
  - UI handling
  - Prompt engineering
  - LLM integration
  - Conversation management

## Prompt Design
The prompts are designed to guide the language model to:
- Gather initial candidate information in a conversational manner
- Generate relevant technical questions based on the declared tech stack
- Maintain context throughout the conversation
- Handle unexpected inputs gracefully

## Challenges & Solutions
- **Context Management**: Implemented a session-based approach to maintain conversation context
- **Tech Stack Parsing**: Developed a robust mechanism to parse and understand diverse tech stacks
- **Question Generation**: Carefully engineered prompts to generate relevant and appropriately challenging technical questions
- **Data Privacy**: Implemented measures to handle sensitive information securely

## Future Improvements
- Integration with ATS (Applicant Tracking Systems)
- Support for more languages
- Advanced analytics on candidate responses
- Video interview integration
