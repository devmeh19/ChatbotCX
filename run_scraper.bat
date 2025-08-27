@echo off
echo Starting Xbox ROG Ally Comprehensive Web Scraper...
echo.
echo Installing scraper dependencies...
pip install -r scraper_requirements.txt
echo.
echo Running comprehensive data extraction...
echo This will extract ALL data from the Xbox ROG Ally website
echo including tabs, buttons, interactive elements, and more...
echo.
python advanced_scraper.py
echo.
echo Scraping completed! Check xbox_rog_ally_complete_data.json for results.
pause 