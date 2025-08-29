ROG Xbox Ally Chatbot

A modern, interactive chatbot web application designed to answer queries about the ROG Xbox Ally handheld gaming device. Built with FastAPI and featuring a beautiful Xbox-themed UI.

🎮 Features

Intelligent Chatbot: AI-powered responses about ROG Xbox Ally specifications and features

Modern UI: Xbox-themed design with responsive layout

Real-time Chat: Interactive chat interface with typing indicators

Quick Questions: Pre-built question buttons for common queries

Device Information: Comprehensive specs and feature overview

Mobile Responsive: Works seamlessly on all devices

🚀 Technology Stack

Backend: FastAPI (Python)

Frontend: HTML5, CSS3, JavaScript (Vanilla)

Styling: Custom CSS with Xbox theme

Icons: Font Awesome

Server: Uvicorn

📋 Development Process & Code Changes
1. Polished Greeting Logic

Implemented in main.py inside get_chatbot_response():

if user_message in ["hi", "hello", "hey", "yo", "sup", "greetings"]:
    return (
        "🤖 **ENHANCED Xbox Ally Bot**: Hello there! I'm your **SUPER-ENHANCED AI expert** with **complete data** "
        "from the Xbox ROG Ally website! 🚀\n\n"
        "📊 463+ data points from the ROG Ally site\n"
        "🎯 All tabs, sections, & interactive elements\n"
        "⚙️ Full specifications & technical details\n"
        "🎮 Gaming features & performance insights\n"
        "🔍 Model comparisons & differences\n"
        "💻 Complete UI, controls, & interface info\n\n"
        "Ask me **anything** about the Xbox ROG Ally!"
    )


Ensures users are greeted with a rich, engaging introduction.

2. Keyword-Based Responses

Added multiple conditional checks for keywords like specs, display, gaming, models, controls, connectivity, accessories, price, use.

Located in get_chatbot_response():

elif any(word in user_message for word in ["specs", "processor", "ram", "storage"]):
    response = ENHANCED_KNOWLEDGE["specs"]["processor"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["memory"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["storage"]


Added similar blocks for other categories, referencing ENHANCED_KNOWLEDGE dictionary.

3. Scraped Data Integration

Created search_scraped_data(user_message) function.

Added cleaning logic to remove HTML, JSON, or large text blocks:

def clean_results(results):
    clean = []
    for r in results:
        if len(r) > 300 or "window.__PRELOADED_STATE__" in r or "{" in r or "<" in r:
            continue
        clean.append(r.strip())
    return clean


Ensures fallback responses are concise and readable.

4. Jinja2 Template Integration

Initialized templates:

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="../templates")  # templates one level above script


Changes ensure proper template directory recognition and dynamic rendering of the chat UI.

5. Enhanced Knowledge Base

Created ENHANCED_KNOWLEDGE dictionary in main.py:

ENHANCED_KNOWLEDGE = {
    "general": {
        "what_is": "The ROG Xbox Ally is a premium handheld gaming device with Xbox integration...",
        "models": "The Ally X vs Ally: differences in RAM, storage, and processor..."
    },
    "specs": {
        "processor": "...",
        "memory": "...",
        "storage": "...",
        "display": "...",
        "battery": "..."
    }
}


All keyword checks reference this dictionary to provide structured responses.

6. Fallback & Default Responses

Final fallback added for unrecognized queries:

if scraped_results:
    response = "📖 Here's what I found based on Xbox site data:\n" + "\n".join(scraped_results[:3])
else:
    response = "Hey there! Could you tell me a bit more so I can help you better?"

7. UI & Styling

Modified templates/index.html for:

Xbox-themed colors

Responsive layout

Chat message bubbles

Custom CSS ensures mobile and desktop friendliness.

8. Testing & Polishing

Verified conversation flows:

Greeting

Keyword queries

Scraped-data fallbacks

Resolved IndentationError issues in Python code.

Confirmed template rendering and chatbot responses in real-time.

💬 Sample Questions

"What are the differences between Ally and Ally X?"

"Does it support Xbox Game Pass?"

"What are the specifications?"

"How does cloud gaming work?"

"Tell me about the controls"

"What's the battery life like?"

"Can I upgrade the storage?"

"How does the display look?"

🔧 API Endpoints

GET / - Main chat interface

POST /chat - Send a message and get response

GET /api/chat?message=... - API endpoint for programmatic access

🌐 Deployment

Local Development: python main.py

Production Deployment: Use Gunicorn, Docker, or cloud platforms (Heroku/AWS/Azure)

📱 Mobile Support

Fully responsive across desktops, tablets, mobiles, and gaming handhelds

🤝 Contributing

Add new features

Improve knowledge base

Enhance UI/UX

Fix bugs

📄 License

MIT License

🙏 Acknowledgments

Microsoft Xbox for product information

FastAPI team

Font Awesome for icons

Happy Gaming with ROG Xbox Ally! 🎮✨