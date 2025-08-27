@echo off
echo Starting ROG Xbox Ally Chatbot...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the application...
echo.
echo The chatbot will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python main.py
pause 