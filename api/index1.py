from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import re
from typing import List, Dict, Any
import os
app = FastAPI(title="ROG Xbox Ally Enhanced Chatbot", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
# templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Point to the templates folder one level above
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Load comprehensive scraped data
def load_scraped_data():
    try:
        with open('xbox_rog_ally_complete_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: Scraped data file not found. Using fallback knowledge base.")
        return None

# Load the comprehensive data
SCRAPED_DATA = load_scraped_data()

# Enhanced knowledge base with scraped data
ENHANCED_KNOWLEDGE = {
    "general": {
        "what_is": "The ROG Xbox Ally is a handheld gaming device that combines the power of Xbox with the freedom of Windows, crafted by ROG (Republic of Gamers). It's designed for portable gaming with Xbox Game Pass integration and offers next-gen power in your hands.",
        "models": "There are two models: ROG Xbox Ally X (24GB RAM, 1TB storage) and ROG Xbox Ally (16GB RAM, 512GB storage). The Ally X is the premium 'next-gen power' model, while the Ally offers 'handheld freedom for everyone'.",
        "tagline": "Power of Xbox. Freedom of Windows. Craftsmanship of ROG. Xbox, anywhere you go.",
        "purpose": "Designed for handheld gaming freedom, allowing you to play Xbox games anywhere with the power of a gaming PC and the convenience of a handheld device."
    },
    "specs": {
        "processor": "ROG Xbox Ally X uses AMD Ryzen AI Z2 Extreme Processor, while ROG Xbox Ally uses AMD Ryzen Z2 A Processor. Both are ultra-efficient processors designed for handheld gaming.",
        "memory": "Ally X has 24GB LPDDR5X-8000 RAM, Ally has 16GB LPDDR5X-6400 RAM. The higher RAM in Ally X enables better multitasking and gaming performance.",
        "storage": "Ally X comes with 1TB M.2 2280 SSD, Ally has 512GB M.2 2280 SSD. Both use the larger 2280 form factor for easier upgrades compared to smaller handheld SSDs.",
        "display": "Both models feature a 7\" FHD (1080p) IPS display with 120Hz refresh rate, 500 nits brightness, AMD FreeSync Premium (Variable Refresh Rate), Corning Gorilla Glass Victus, and DXC Anti-Reflection coating for excellent visibility.",
        "battery": "Ally X has an 80Wh battery, Ally has a 60Wh battery for extended gaming sessions. The larger battery in Ally X provides longer playtime.",
        "dimensions": "Both models measure 290.8 x 121.5 x 50.7mm. Ally X weighs 715g, Ally weighs 670g.",
        "operating_system": "Both models run Windows 11 Home, providing full Windows compatibility and access to PC games and applications."
    }
}

def search_scraped_data(query: str) -> List[str]:
    """Search through scraped data for relevant information"""
    if not SCRAPED_DATA:
        return []
    
    query_lower = query.lower()
    results = []
    
    # Search through main content
    if 'main_content' in SCRAPED_DATA:
        main_content = SCRAPED_DATA['main_content']
        
        # Search headings
        if 'headings' in main_content:
            for heading in main_content['headings']:
                if query_lower in heading.get('text', '').lower():
                    results.append(f"**Heading**: {heading['text']}")
        
        # Search paragraphs
        if 'paragraphs' in main_content:
            for para in main_content['paragraphs']:
                if query_lower in para.lower():
                    results.append(f"**Content**: {para[:200]}...")
    
    # Search through specifications
    if 'comprehensive_specifications' in SCRAPED_DATA:
        specs = SCRAPED_DATA['comprehensive_specifications']
        for key, value in specs.items():
            if isinstance(value, dict):
                for spec_key, spec_value in value.items():
                    if query_lower in str(spec_value).lower():
                        results.append(f"**{spec_key}**: {spec_value}")
            elif isinstance(value, str) and query_lower in value.lower():
                results.append(f"**Specification**: {value}")
    
    # Search through interactive elements
    if 'interactive_elements' in SCRAPED_DATA:
        elements = SCRAPED_DATA['interactive_elements']
        for key, element in elements.items():
            if isinstance(element, dict):
                element_text = element.get('text', '')
                if query_lower in element_text.lower():
                    results.append(f"**Interactive Element**: {element_text}")
    
    # Search through tabs and sections
    if 'all_tabs_and_sections' in SCRAPED_DATA:
        tabs = SCRAPED_DATA['all_tabs_and_sections']
        for key, tab in tabs.items():
            if isinstance(tab, dict):
                tab_text = tab.get('text', '')
                tab_content = tab.get('content', '')
                if query_lower in tab_text.lower() or query_lower in tab_content.lower():
                    results.append(f"**Tab/Section**: {tab_text} - {tab_content[:100]}...")
    
    return results[:5]  # Limit to 5 results
def get_enhanced_chatbot_response(user_message: str) -> str:
    """Generate enhanced chatbot response using scraped data and improved fallback logic."""
    user_message = user_message.lower().strip()

    # === Polished Intro Greeting ===
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

    # === Get scraped data ===
    scraped_results = search_scraped_data(user_message)

    # Clean scraped results (remove JSON/HTML noise)
    def clean_results(results):
        clean = []
        for r in results:
            # Skip large JSON dumps or HTML
            if len(r) > 300 or "window.__PRELOADED_STATE__" in r or "{" in r or "<" in r:
                continue
            clean.append(r.strip())
        return clean

    scraped_results = clean_results(scraped_results)

    # === Main Knowledge Checks ===
    if any(word in user_message for word in ["what", "tell me", "explain", "describe"]):
        if any(word in user_message for word in ["rog", "ally", "handheld", "device"]):
            response = ENHANCED_KNOWLEDGE["general"]["what_is"] + "\n\n" + ENHANCED_KNOWLEDGE["general"]["tagline"]
        elif any(word in user_message for word in ["specs", "specifications", "processor", "ram", "storage"]):
            response = ENHANCED_KNOWLEDGE["specs"]["processor"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["memory"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["storage"]
        elif any(word in user_message for word in ["display", "screen", "battery"]):
            response = ENHANCED_KNOWLEDGE["specs"]["display"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["battery"]
        elif any(word in user_message for word in ["game", "gaming", "play"]):
            response = "The ROG Xbox Ally supports Xbox Game Pass, Cloud Gaming, Play Anywhere, and Remote Play. You can access hundreds of games and stream them directly to your handheld device."
        else:
            response = ENHANCED_KNOWLEDGE["general"]["what_is"]

    elif any(word in user_message for word in ["models", "versions", "difference", "compare", "ally x", "ally x vs", "vs ally"]):
        response = ENHANCED_KNOWLEDGE["general"]["models"]

    elif any(word in user_message for word in ["game pass", "xbox game pass"]):
        response = "Yes! You get instant access to hundreds of high-quality games from Xbox Game Pass. Stream or download them to your handheld."

    elif any(word in user_message for word in ["cloud", "streaming"]):
        response = "The ROG Xbox Ally supports Xbox Cloud Gaming for streaming your favorite titles without downloads."

    elif any(word in user_message for word in ["controls", "buttons", "triggers", "grips", "interface", "ui"]):
        response = "Xbox-inspired controls with ABXY buttons, ergonomic grips, and impulse triggers (Ally X) or Hall Effect triggers (Ally)."

    elif any(word in user_message for word in ["connectivity", "ports", "wifi", "bluetooth", "usb", "microsd", "audio"]):
        response = "WiFi 6E + Bluetooth 5.4, USB-C with DisplayPort, microSD slot (UHS-II), and 3.5mm audio jack."

    elif any(word in user_message for word in ["xbox experience", "boot", "startup", "interface", "game bar"]):
        response = "Boots into Xbox full-screen experience. Game Bar provides quick access to essential tools."

    elif any(word in user_message for word in ["120hz", "refresh rate", "freesync", "brightness", "gorilla glass", "anti reflection"]):
        response = "7\" FHD (1080p) 120Hz IPS display, 500 nits brightness, AMD FreeSync Premium, Gorilla Glass Victus."

    elif any(word in user_message for word in ["accessories", "included", "stand", "charger", "65w"]):
        response = "Comes with ROG Xbox Ally, 65W charger, and stand."

    elif any(word in user_message for word in ["use", "purpose", "when", "scenarios", "portable", "travel"]):
        response = "Perfect for gaming on the go, during travel, or playing Xbox and PC games anywhere."

    elif any(word in user_message for word in ["price", "cost", "how much", "buy", "purchase", "available"]):
        response = "Pricing varies by region. The Ally X offers higher specs; the Ally is more budget-friendly."

    else:
        # Final fallback
        if scraped_results:
            response = "📖 Here's what I found based on Xbox site data:\n" + "\n".join(scraped_results[:3])
        else:
            response = "Can you please elaborate?"

    return response





# def get_enhanced_chatbot_response(user_message: str) -> str:
#     """Generate enhanced chatbot response using scraped data"""
#     user_message = user_message.lower().strip()
    
#     # First, search through scraped data for specific information
#     scraped_results = search_scraped_data(user_message)
    
#     # Check for specific keywords and provide relevant responses
#     if any(word in user_message for word in ["what", "tell me", "explain", "describe"]):
#         if any(word in user_message for word in ["rog", "ally", "handheld", "device"]):
#             response = ENHANCED_KNOWLEDGE["general"]["what_is"] + "\n\n" + ENHANCED_KNOWLEDGE["general"]["tagline"]
#         elif any(word in user_message for word in ["specs", "specifications", "processor", "ram", "storage"]):
#             response = ENHANCED_KNOWLEDGE["specs"]["processor"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["memory"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["storage"]
#         elif any(word in user_message for word in ["display", "screen", "battery"]):
#             response = ENHANCED_KNOWLEDGE["specs"]["display"] + "\n\n" + ENHANCED_KNOWLEDGE["specs"]["battery"]
#         elif any(word in user_message for word in ["game", "gaming", "play"]):
#             response = "Based on the comprehensive data from the Xbox website:\n\n"
#             if scraped_results:
#                 response += "\n".join(scraped_results)
#             else:
#                 response += "The ROG Xbox Ally supports Xbox Game Pass, Cloud Gaming, Play Anywhere, and Remote Play. You can access hundreds of games and stream them directly to your handheld device."
#         else:
#             response = "Based on the comprehensive data from the Xbox website:\n\n"
#             if scraped_results:
#                 response += "\n".join(scraped_results)
#             else:
#                 response += ENHANCED_KNOWLEDGE["general"]["what_is"]
    
#     elif any(word in user_message for word in ["models", "versions", "difference", "compare", "ally x", "ally x vs", "vs ally"]):
#         response = ENHANCED_KNOWLEDGE["general"]["models"] + "\n\n"
#         if scraped_results:
#             response += "**Additional details from the website:**\n" + "\n".join(scraped_results)
#         else:
#             response += "ROG Xbox Ally X offers: Higher RAM (24GB vs 16GB), larger storage (1TB vs 512GB), better processor (Z2 Extreme vs Z2 A), larger battery (80Wh vs 60Wh), and impulse triggers. Both share the same display and core gaming features."
    
#     elif any(word in user_message for word in ["game pass", "xbox game pass"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Yes! You get instant access to hundreds of high-quality games from the Xbox Game Pass library plus select games you own. Stream games directly or download them for offline play."
    
#     elif any(word in user_message for word in ["cloud", "streaming"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Supports Xbox Cloud Gaming (Beta) for streaming games, including select games you own or buy (requires Game Pass Ultimate membership). Stream directly to your handheld without downloading."
    
#     elif any(word in user_message for word in ["controls", "buttons", "triggers", "grips", "interface", "ui"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Inspired by Xbox controls with iconic ABXY buttons, contoured grips inspired by Xbox Wireless Controllers for all-day comfort, impulse triggers (Ally X) or Hall Effect analogue triggers (Ally), and familiar Xbox button layout."
    
#     elif any(word in user_message for word in ["connectivity", "ports", "wifi", "bluetooth", "usb", "microsd", "audio"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "WiFi 6E (2x2) + Bluetooth 5.4, USB-C ports with DisplayPort support, microSD card reader (UHS-II, supports SD/SDXC/SDHC), and 3.5mm combo audio jack."
    
#     elif any(word in user_message for word in ["xbox experience", "boot", "startup", "interface", "game bar"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Boots directly into Xbox full-screen experience optimized for handheld gaming. Press the Xbox button for Game Bar with quick access to essential tools and customizable widgets. Hold the Xbox button to navigate all open apps."
    
#     elif any(word in user_message for word in ["120hz", "refresh rate", "freesync", "brightness", "gorilla glass", "anti reflection"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Both models feature a 7\" FHD (1080p) IPS display with 120Hz refresh rate, 500 nits brightness, AMD FreeSync Premium (Variable Refresh Rate), Corning Gorilla Glass Victus, and DXC Anti-Reflection coating for excellent visibility."
    
#     elif any(word in user_message for word in ["accessories", "included", "stand", "charger", "65w"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Both models come with: ROG Xbox Ally device, 65W charger, and stand for comfortable desktop use. The stand allows you to prop up the device for comfortable viewing and use when not holding it."
    
#     elif any(word in user_message for word in ["use", "purpose", "when", "scenarios", "portable", "travel"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Perfect for gaming on the go, during travel, or when you want to play Xbox games away from your console. Full Windows 11 compatibility means you can play PC games, use applications, and browse the web."
    
#     elif any(word in user_message for word in ["price", "cost", "how much", "buy", "purchase", "available"]):
#         response = "Based on the comprehensive Xbox website data:\n\n"
#         if scraped_results:
#             response += "\n".join(scraped_results)
#         else:
#             response += "Prices vary by retailer and region. The Ally X is the premium model with higher specs, while the Ally offers great value for most users. Both models come with a 65W charger and stand included."
    
#     else:
#         # Default response with comprehensive help
#         response = "I'm your ENHANCED ROG Xbox Ally expert with access to COMPLETE data from the Xbox website! I can answer ANY question about the device. Here are some topics you can ask about:\n\n" + \
#                    "🎮 **Gaming**: Game Pass, cloud gaming, Play Anywhere, remote play\n" + \
#                    "⚙️ **Specs**: Processor, RAM, storage, display, battery, dimensions\n" + \
#                    "🔍 **Models**: Ally vs Ally X differences, comparisons\n" + \
#                    "🎯 **Controls**: Buttons, triggers, grips, Xbox button, Game Bar\n" + \
#                    "🔌 **Connectivity**: USB-C, WiFi 6E, Bluetooth, microSD, audio\n" + \
#                    "💻 **Experience**: Xbox interface, Windows 11, optimization\n" + \
#                    "📱 **Use Cases**: Portable gaming, travel, home use\n" + \
#                    "📦 **Accessories**: What's included, stand, charger\n\n" + \
#                    "**NEW**: I now have access to ALL 463 data points from the Xbox website!\n\n" + \
#                    "Just ask me anything about the ROG Xbox Ally!"
    
#     # Add scraped data results if available and not already included
#     if scraped_results and "Based on the comprehensive Xbox website data" not in response:
#         response += "\n\n**Additional information from the Xbox website:**\n" + "\n".join(scraped_results[:3])
    
#     return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: str = Form(...)):
    response = get_enhanced_chatbot_response(message)
    return {"response": response}

@app.get("/api/chat")
async def chat_api(message: str):
    response = get_enhanced_chatbot_response(message)
    return {"response": response}

@app.get("/api/data-summary")
async def get_data_summary():
    """Get summary of available data"""
    if SCRAPED_DATA:
        return {
            "status": "success",
            "total_data_points": 463,
            "scraped_timestamp": SCRAPED_DATA.get("timestamp", "Unknown"),
            "data_categories": [
                "All Tabs & Sections (90 items)",
                "Interactive Elements (223 items)",
                "Comprehensive Specifications (14 items)",
                "Main Content (35 headings, 53 paragraphs, 98 images, 44 sections)",
                "Gaming Features (8 items)",
                "Model Comparisons (12 items)",
                "Controls & Interface (6 items)",
                "Connectivity & Ports (6 items)",
                "Technical Details (8 items)",
                "Accessories & Packaging (5 items)",
                "Use Cases & Scenarios (6 items)",
                "Pricing & Availability (6 items)",
                "Page Metadata (5 items)",
                "Scripts (51 items)",
                "Stylesheets (16 items)",
                "Inline Styles (3 items)"
            ]
        }
    else:
        return {"status": "error", "message": "Scraped data not available"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 

# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# import json
# import re
# from typing import List, Dict, Any
# from fastapi.templating import Jinja2Templates

# Btemplates = Jinja2Templates(directory="templates")

# # ======================
# # APP CONFIG
# # ======================

# app = FastAPI(title="ROG Xbox Ally Enhanced Chatbot", version="3.0.0")

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Jinja templates
# templates = Jinja2Templates(directory="templates")


# # ======================
# # DATA LOADING
# # ======================

# def load_scraped_data() -> Dict[str, Any]:
#     """
#     Load scraped Xbox ROG Ally data from JSON file.
#     """
#     try:
#         with open('xbox_rog_ally_complete_data.json', 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print("Warning: Scraped data file not found. Using fallback knowledge base.")
#         return None


# SCRAPED_DATA = load_scraped_data()

# # Knowledge base fallback
# ENHANCED_KNOWLEDGE = {
#     "general": {
#         "what_is": "The ROG Xbox Ally is a handheld gaming device combining Xbox's gaming ecosystem with Windows 11, created by ROG (Republic of Gamers).",
#         "models": "Two models: ROG Ally X (24GB RAM, 1TB SSD) and ROG Ally (16GB RAM, 512GB SSD).",
#         "tagline": "Power of Xbox. Freedom of Windows. Craftsmanship of ROG.",
#         "purpose": "Designed for portable gaming with Xbox Game Pass, Cloud Gaming, and full PC game compatibility."
#     },
#     "specs": {
#         "processor": "ROG Ally X uses AMD Ryzen AI Z2 Extreme, while Ally uses Ryzen Z2 A.",
#         "memory": "Ally X: 24GB LPDDR5X-8000; Ally: 16GB LPDDR5X-6400.",
#         "storage": "Ally X: 1TB SSD; Ally: 512GB SSD.",
#         "display": "7\" 1080p IPS, 120Hz refresh, Gorilla Glass Victus, anti-reflective coating.",
#         "battery": "Ally X: 80Wh, Ally: 60Wh for extended sessions.",
#         "dimensions": "Both: 290.8 x 121.5 x 50.7mm. Ally X weighs 715g, Ally 670g.",
#         "os": "Windows 11 Home with full PC compatibility."
#     }
# }


# # ======================
# # SEARCH HELPERS
# # ======================

# def deep_search(data: Any, keyword: str) -> List[str]:
#     """
#     Recursively search for a keyword in scraped JSON data.
#     """
#     results = []
#     if isinstance(data, dict):
#         for k, v in data.items():
#             if keyword in str(k).lower() or keyword in str(v).lower():
#                 results.append(f"**{k}**: {str(v)[:150]}...")
#             results.extend(deep_search(v, keyword))
#     elif isinstance(data, list):
#         for item in data:
#             results.extend(deep_search(item, keyword))
#     return results


# def extract_price(data: Dict[str, Any]) -> str:
#     """
#     Attempt to extract price information.
#     """
#     if not data:
#         return "Price not available."
#     results = deep_search(data, "price")
#     for res in results:
#         if re.search(r"\$?\d+(\.\d{1,2})?", res):
#             return res
#     return "Price not available."


# def extract_specs(data: Dict[str, Any]) -> List[str]:
#     """
#     Extract key specs like processor, RAM, storage, etc.
#     """
#     specs_keywords = ["processor", "ram", "memory", "storage", "display", "battery"]
#     specs = []
#     for kw in specs_keywords:
#         res = deep_search(data, kw)
#         if res:
#             specs.extend(res[:2])
#     return specs[:5]


# def classify_intent(query: str) -> str:
#     """
#     Classify the user's query intent.
#     """
#     q = query.lower()
#     if any(w in q for w in ["price", "cost", "how much", "buy", "purchase", "available"]):
#         return "price"
#     if any(w in q for w in ["specs", "specifications", "details", "processor", "ram", "storage"]):
#         return "specs"
#     if len(q.split()) <= 3 and "xbox" in q:
#         return "vague"
#     return "general"


# # ======================
# # CHATBOT RESPONSE
# # ======================

# def get_enhanced_chatbot_response(user_message: str) -> str:
#     """
#     Generate chatbot responses dynamically based on intent and data.
#     """
#     if not user_message.strip():
#         return "Please ask a question about Xbox or ROG Ally."

#     intent = classify_intent(user_message)
#     response = ""

#     if intent == "price":
#         price = extract_price(SCRAPED_DATA)
#         response = f"💲 **Price Info**: {price}"

#     elif intent == "specs":
#         specs = extract_specs(SCRAPED_DATA)
#         if specs:
#             response = "🔍 **Key Specs:**\n" + "\n".join(specs)
#         else:
#             response = "I couldn't find detailed specs, but it's a high-performance gaming handheld."

#     elif intent == "vague":
#         response = (
#             f"🎮 {ENHANCED_KNOWLEDGE['general']['what_is']}\n\n"
#             f"✨ {ENHANCED_KNOWLEDGE['general']['tagline']}\n"
#             "Ask about price, specs, or features for more details."
#         )

#     else:  # general
#         results = deep_search(SCRAPED_DATA, user_message.lower()) if SCRAPED_DATA else []
#         if results:
#             response = "📖 Here's what I found:\n" + "\n".join(results[:5])
#         else:
#             response = "I couldn't find an exact answer, but I can help with Xbox products, specs, pricing, and more."

#     return response


# # ======================
# # API ROUTES
# # ======================

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     """
#     Serve the chatbot UI.
#     """
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.post("/chat")
# async def chat(message: str = Form(...)):
#     """
#     Chat endpoint for frontend form submissions.
#     """
#     response = get_enhanced_chatbot_response(message)
#     return {"response": response}


# @app.get("/api/chat")
# async def chat_api(message: str):
#     """
#     API endpoint for chatbot queries (GET).
#     """
#     response = get_enhanced_chatbot_response(message)
#     return {"response": response}


# @app.get("/api/data-summary")
# async def get_data_summary():
#     """
#     Summarize available scraped data.
#     """
#     if SCRAPED_DATA:
#         return {
#             "status": "success",
#             "example_price": extract_price(SCRAPED_DATA),
#             "example_specs": extract_specs(SCRAPED_DATA),
#             "note": "Data dynamically extracted from xbox_rog_ally_complete_data.json"
#         }
#     else:
#         return {"status": "error", "message": "Scraped data not available"}


# # ======================
# # ENTRY POINT
# # ======================

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
