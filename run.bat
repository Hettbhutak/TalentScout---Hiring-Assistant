@echo off
echo Starting TalentScout Hiring Assistant...

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements if needed
pip install -r requirements.txt

:: Start the Streamlit app
streamlit run app.py

:: Deactivate virtual environment when the app is closed
call venv\Scripts\deactivate.bat
