@echo off
echo Starting ROG Xbox Ally ENHANCED Chatbot...
echo.
echo This chatbot now has access to 463 data points from the Xbox website!
echo Including all tabs, interactive elements, and complete specifications.
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the ENHANCED chatbot...
echo.
echo The enhanced chatbot will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python enhanced_chatbot.py
pause 