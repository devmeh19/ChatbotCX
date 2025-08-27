from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any
import json
import re

app = FastAPI(title="ROG Xbox Ally Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files not needed for this chatbot

# Templates
templates = Jinja2Templates(directory="templates")

# Comprehensive knowledge base for ROG Xbox Ally from Xbox website
CHATBOT_KNOWLEDGE = {
    "general": {
        "what_is": "The ROG Xbox Ally is a handheld gaming device that combines the power of Xbox with the freedom of Windows, crafted by ROG (Republic of Gamers). It's designed for portable gaming with Xbox Game Pass integration and offers next-gen power in your hands.",
        "models": "There are two models: ROG Xbox Ally X (24GB RAM, 1TB storage) and ROG Xbox Ally (16GB RAM, 512GB storage). The Ally X is the premium 'next-gen power' model, while the Ally offers 'handheld freedom for everyone'.",
        "price": "Prices vary by retailer and region. The Ally X is the premium model with higher specs, while the Ally offers great value for most users. Both models come with a 65W charger and stand included.",
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
    },
    "gaming": {
        "game_pass": "Yes! You get instant access to hundreds of high-quality games from the Xbox Game Pass library plus select games you own. Stream games directly or download them for offline play.",
        "cloud_gaming": "Supports Xbox Cloud Gaming (Beta) for streaming games, including select games you own or buy (requires Game Pass Ultimate membership). Stream directly to your handheld without downloading.",
        "play_anywhere": "Buy once, play anywhere! Select PC games can be downloaded and played on the go. Xbox Play Anywhere games work across PC, Xbox console, and supported gaming handhelds at no additional cost.",
        "remote_play": "Play games installed on your Xbox console remotely from your ROG Xbox Ally device. Requires internet connection and your Xbox to be turned on or in Sleep mode.",
        "game_library": "Access supported games from Xbox and other PC game storefronts. Your progress, saves, add-ons, and achievements go with you across devices.",
        "streaming": "Stream games with cloud gaming, including select games you own or buy. Requires Game Pass Ultimate membership for cloud gaming features."
    },
    "features": {
        "controls": "Inspired by Xbox controls with iconic ABXY buttons, contoured grips inspired by Xbox Wireless Controllers for all-day comfort, impulse triggers (Ally X) or Hall Effect analogue triggers (Ally), L & R bumpers, Xbox button, View button, Menu button, Command Centre button, Library button, 2x assignable back buttons, 2x full-size analogue sticks, HD haptics, and 6-Axis IMU for motion controls.",
        "connectivity": "WiFi 6E (2x2) + Bluetooth 5.4, USB-C ports with DisplayPort support, microSD card reader (UHS-II, supports SD/SDXC/SDHC), and 3.5mm combo audio jack.",
        "xbox_experience": "Boots directly into Xbox full-screen experience optimized for handheld gaming. Press the Xbox button for Game Bar with quick access to essential tools and customizable widgets. Hold the Xbox button to navigate all open apps.",
        "xbox_button": "The Xbox button provides instant access to Game Bar, customizable widgets, and more. It's the central hub for Xbox functionality on the device.",
        "grips": "Contoured grips inspired by Xbox Wireless Controllers deliver all-day comfort, making extended gaming sessions comfortable and ergonomic.",
        "triggers": "Ally X features impulse triggers for enhanced control and haptic feedback, while Ally uses Hall Effect analogue triggers for precise analog input."
    },
    "ports": {
        "ally_x_ports": "1x USB 4 Type-C with DisplayPort 2.1 / Power Delivery 3.0 (Thunderbolt 4 compatible), 1x USB 3.2 Gen 2 Type-C with DisplayPort 2.1 / Power Delivery 3.0, 1x UHS-II microSD card reader, 1x 3.5mm combo audio jack.",
        "ally_ports": "2x USB 3.2 Gen 2 Type-C with DisplayPort 1.4 / Power Delivery 3.0, 1x UHS-II microSD card reader, 1x 3.5mm combo audio jack.",
        "usb_c": "USB-C ports support DisplayPort for external displays and Power Delivery for charging. Ally X has Thunderbolt 4 compatibility for faster data transfer.",
        "microsd": "UHS-II microSD card reader supports SD, SDXC, and SDHC cards. UHS-I cards work with DDR200 mode for expanded storage options.",
        "audio": "3.5mm combo audio jack for headphones or external audio devices."
    },
    "comparison": {
        "ally_x_vs_ally": "ROG Xbox Ally X offers: Higher RAM (24GB vs 16GB), larger storage (1TB vs 512GB), better processor (Z2 Extreme vs Z2 A), larger battery (80Wh vs 60Wh), impulse triggers vs Hall Effect triggers, USB 4 with Thunderbolt 4 compatibility vs USB 3.2 Gen 2, and DisplayPort 2.1 vs 1.4. Both share the same display, dimensions, and core gaming features.",
        "ram_difference": "Ally X has 24GB LPDDR5X-8000 RAM vs Ally's 16GB LPDDR5X-6400. The higher capacity and speed enable better multitasking and future-proofing.",
        "storage_difference": "Ally X comes with 1TB storage vs Ally's 512GB. Both use M.2 2280 SSDs that are easily upgradeable.",
        "processor_difference": "Ally X uses AMD Ryzen AI Z2 Extreme vs Ally's AMD Ryzen Z2 A. The Extreme variant offers better performance and AI capabilities.",
        "battery_difference": "Ally X has an 80Wh battery vs Ally's 60Wh, providing approximately 33% longer battery life for extended gaming sessions.",
        "trigger_difference": "Ally X features impulse triggers with haptic feedback for enhanced control, while Ally uses Hall Effect analogue triggers for precise analog input."
    },
    "gaming_experience": {
        "xbox_interface": "Boots directly into Xbox full-screen experience inspired and optimized specifically for handheld gaming. The interface is designed for touch and controller navigation.",
        "game_bar": "Press the Xbox button for quick access to essential tools and customizable widgets with Game Bar. Hold the Xbox button to navigate all open apps and switch between games.",
        "library_access": "Access your aggregated game library from Xbox and other PC game storefronts. All your games in one place, accessible anywhere you go.",
        "progress_sync": "Your game saves, add-ons, and achievements go with you across devices. Progress is automatically synced when you play Xbox Play Anywhere games.",
        "handheld_optimization": "The entire experience is optimized for handheld gaming, from the interface design to the control layout and performance settings."
    },
    "technical_details": {
        "refresh_rate": "120Hz refresh rate with AMD FreeSync Premium for smooth, tear-free gaming at variable frame rates.",
        "brightness": "500 nits brightness ensures good visibility even in bright lighting conditions.",
        "glass_protection": "Corning Gorilla Glass Victus provides excellent scratch resistance and durability for the display.",
        "anti_reflection": "DXC Anti-Reflection coating reduces glare and improves visibility in various lighting conditions.",
        "wifi_specs": "WiFi 6E (2x2) provides faster, more stable wireless connections with lower latency for online gaming.",
        "bluetooth": "Bluetooth 5.4 offers improved connectivity for wireless accessories and lower power consumption."
    },
    "accessories": {
        "included": "Both models come with: ROG Xbox Ally device, 65W charger, and stand for comfortable desktop use.",
        "stand": "Included stand allows you to prop up the device for comfortable viewing and use when not holding it.",
        "charger": "65W charger provides fast charging and can power the device during intensive gaming sessions.",
        "compatibility": "Compatible with Xbox accessories, PC gaming peripherals, and standard USB-C devices."
    },
    "use_cases": {
        "portable_gaming": "Perfect for gaming on the go, during travel, or when you want to play Xbox games away from your console.",
        "pc_gaming": "Full Windows 11 compatibility means you can play PC games, use applications, and browse the web.",
        "xbox_extension": "Extends your Xbox gaming experience beyond the living room, allowing you to play anywhere in your home or on the go.",
        "cloud_gaming": "Stream games without downloading, perfect for trying new games or playing when storage is limited.",
        "remote_play": "Continue playing your Xbox console games remotely, perfect for when someone else is using the TV."
    }
}

def get_chatbot_response(user_message: str) -> str:
    """Generate comprehensive chatbot response based on user input"""
    user_message = user_message.lower().strip()
    
    # General device questions
    if any(word in user_message for word in ["what", "tell me", "explain", "describe"]):
        if any(word in user_message for word in ["rog", "ally", "handheld", "device"]):
            return CHATBOT_KNOWLEDGE["general"]["what_is"] + "\n\n" + CHATBOT_KNOWLEDGE["general"]["tagline"]
        elif any(word in user_message for word in ["purpose", "why", "use"]):
            return CHATBOT_KNOWLEDGE["general"]["purpose"]
    
    # Specifications questions
    elif any(word in user_message for word in ["specs", "specifications", "technical", "hardware"]):
        if any(word in user_message for word in ["processor", "cpu", "amd", "ryzen"]):
            return CHATBOT_KNOWLEDGE["specs"]["processor"]
        elif any(word in user_message for word in ["ram", "memory", "24gb", "16gb"]):
            return CHATBOT_KNOWLEDGE["specs"]["memory"]
        elif any(word in user_message for word in ["storage", "ssd", "1tb", "512gb", "upgrade"]):
            return CHATBOT_KNOWLEDGE["specs"]["storage"]
        elif any(word in user_message for word in ["display", "screen", "7 inch", "1080p", "120hz"]):
            return CHATBOT_KNOWLEDGE["specs"]["display"]
        elif any(word in user_message for word in ["battery", "power", "60wh", "80wh", "life"]):
            return CHATBOT_KNOWLEDGE["specs"]["battery"]
        elif any(word in user_message for word in ["size", "dimensions", "weight", "measurements"]):
            return CHATBOT_KNOWLEDGE["specs"]["dimensions"]
        elif any(word in user_message for word in ["os", "windows", "operating system"]):
            return CHATBOT_KNOWLEDGE["specs"]["operating_system"]
        else:
            return "Here are the key specifications:\n\n" + CHATBOT_KNOWLEDGE["specs"]["processor"] + "\n\n" + CHATBOT_KNOWLEDGE["specs"]["memory"] + "\n\n" + CHATBOT_KNOWLEDGE["specs"]["storage"] + "\n\n" + CHATBOT_KNOWLEDGE["specs"]["display"] + "\n\n" + CHATBOT_KNOWLEDGE["specs"]["battery"]
    
    # Model comparison questions
    elif any(word in user_message for word in ["models", "versions", "difference", "compare", "ally x", "ally x vs", "vs ally"]):
        if any(word in user_message for word in ["ram", "memory"]):
            return CHATBOT_KNOWLEDGE["comparison"]["ram_difference"]
        elif any(word in user_message for word in ["storage", "ssd", "1tb", "512gb"]):
            return CHATBOT_KNOWLEDGE["comparison"]["storage_difference"]
        elif any(word in user_message for word in ["processor", "cpu", "extreme", "z2"]):
            return CHATBOT_KNOWLEDGE["comparison"]["processor_difference"]
        elif any(word in user_message for word in ["battery", "power", "80wh", "60wh"]):
            return CHATBOT_KNOWLEDGE["comparison"]["battery_difference"]
        elif any(word in user_message for word in ["triggers", "impulse", "hall effect"]):
            return CHATBOT_KNOWLEDGE["comparison"]["trigger_difference"]
        else:
            return CHATBOT_KNOWLEDGE["general"]["models"] + "\n\n" + CHATBOT_KNOWLEDGE["comparison"]["ally_x_vs_ally"]
    
    # Gaming questions
    elif any(word in user_message for word in ["game", "gaming", "play", "xbox"]):
        if any(word in user_message for word in ["game pass", "gamepass"]):
            return CHATBOT_KNOWLEDGE["gaming"]["game_pass"]
        elif any(word in user_message for word in ["cloud", "streaming", "stream"]):
            return CHATBOT_KNOWLEDGE["gaming"]["cloud_gaming"]
        elif any(word in user_message for word in ["play anywhere", "anywhere"]):
            return CHATBOT_KNOWLEDGE["gaming"]["play_anywhere"]
        elif any(word in user_message for word in ["remote", "remote play"]):
            return CHATBOT_KNOWLEDGE["gaming"]["remote_play"]
        elif any(word in user_message for word in ["library", "games", "store"]):
            return CHATBOT_KNOWLEDGE["gaming"]["game_library"]
        elif any(word in user_message for word in ["progress", "saves", "achievements"]):
            return CHATBOT_KNOWLEDGE["gaming"]["progress_sync"]
        else:
            return "Gaming features include:\n\n" + CHATBOT_KNOWLEDGE["gaming"]["game_pass"] + "\n\n" + CHATBOT_KNOWLEDGE["gaming"]["cloud_gaming"] + "\n\n" + CHATBOT_KNOWLEDGE["gaming"]["play_anywhere"]
    
    # Controls and interface questions
    elif any(word in user_message for word in ["controls", "buttons", "triggers", "grips", "interface", "ui"]):
        if any(word in user_message for word in ["xbox button", "game bar"]):
            return CHATBOT_KNOWLEDGE["features"]["xbox_button"] + "\n\n" + CHATBOT_KNOWLEDGE["features"]["game_bar"]
        elif any(word in user_message for word in ["grips", "comfort", "ergonomic"]):
            return CHATBOT_KNOWLEDGE["features"]["grips"]
        elif any(word in user_message for word in ["triggers", "impulse", "hall effect"]):
            return CHATBOT_KNOWLEDGE["features"]["triggers"]
        else:
            return CHATBOT_KNOWLEDGE["features"]["controls"]
    
    # Connectivity and ports questions
    elif any(word in user_message for word in ["connectivity", "ports", "wifi", "bluetooth", "usb", "microsd", "audio"]):
        if any(word in user_message for word in ["usb", "usb-c", "thunderbolt"]):
            return CHATBOT_KNOWLEDGE["ports"]["usb_c"]
        elif any(word in user_message for word in ["microsd", "sd card", "expandable"]):
            return CHATBOT_KNOWLEDGE["ports"]["microsd"]
        elif any(word in user_message for word in ["audio", "headphone", "3.5mm"]):
            return CHATBOT_KNOWLEDGE["ports"]["audio"]
        elif any(word in user_message for word in ["wifi", "6e", "bluetooth"]):
            return CHATBOT_KNOWLEDGE["technical_details"]["wifi_specs"] + "\n\n" + CHATBOT_KNOWLEDGE["technical_details"]["bluetooth"]
        else:
            return "Connectivity features:\n\n" + CHATBOT_KNOWLEDGE["features"]["connectivity"]
    
    # Xbox experience questions
    elif any(word in user_message for word in ["xbox experience", "boot", "startup", "interface", "game bar"]):
        return CHATBOT_KNOWLEDGE["gaming_experience"]["xbox_interface"] + "\n\n" + CHATBOT_KNOWLEDGE["gaming_experience"]["game_bar"]
    
    # Technical details questions
    elif any(word in user_message for word in ["120hz", "refresh rate", "freesync", "brightness", "gorilla glass", "anti reflection"]):
        if any(word in user_message for word in ["120hz", "refresh", "freesync"]):
            return CHATBOT_KNOWLEDGE["technical_details"]["refresh_rate"]
        elif any(word in user_message for word in ["brightness", "nits", "500"]):
            return CHATBOT_KNOWLEDGE["technical_details"]["brightness"]
        elif any(word in user_message for word in ["gorilla glass", "protection", "scratch"]):
            return CHATBOT_KNOWLEDGE["technical_details"]["glass_protection"]
        elif any(word in user_message for word in ["anti reflection", "glare", "visibility"]):
            return CHATBOT_KNOWLEDGE["technical_details"]["anti_reflection"]
    
    # Accessories questions
    elif any(word in user_message for word in ["accessories", "included", "stand", "charger", "65w"]):
        return CHATBOT_KNOWLEDGE["accessories"]["included"] + "\n\n" + CHATBOT_KNOWLEDGE["accessories"]["stand"] + "\n\n" + CHATBOT_KNOWLEDGE["accessories"]["charger"]
    
    # Use case questions
    elif any(word in user_message for word in ["use", "purpose", "when", "scenarios", "portable", "travel"]):
        if any(word in user_message for word in ["portable", "travel", "go"]):
            return CHATBOT_KNOWLEDGE["use_cases"]["portable_gaming"]
        elif any(word in user_message for word in ["pc", "windows", "applications"]):
            return CHATBOT_KNOWLEDGE["use_cases"]["pc_gaming"]
        elif any(word in user_message for word in ["home", "extension", "living room"]):
            return CHATBOT_KNOWLEDGE["use_cases"]["xbox_extension"]
        elif any(word in user_message for word in ["cloud", "streaming", "download"]):
            return CHATBOT_KNOWLEDGE["use_cases"]["cloud_gaming"]
        elif any(word in user_message for word in ["remote", "tv", "someone else"]):
            return CHATBOT_KNOWLEDGE["use_cases"]["remote_play"]
    
    # Price and availability questions
    elif any(word in user_message for word in ["price", "cost", "how much", "buy", "purchase", "available"]):
        return CHATBOT_KNOWLEDGE["general"]["price"]
    
    # Default response with comprehensive help
    return "I'm your comprehensive ROG Xbox Ally expert! I can answer ANY question about the device. Here are some topics you can ask about:\n\n" + \
           "🎮 **Gaming**: Game Pass, cloud gaming, Play Anywhere, remote play\n" + \
           "⚙️ **Specs**: Processor, RAM, storage, display, battery, dimensions\n" + \
           "🔍 **Models**: Ally vs Ally X differences, comparisons\n" + \
           "🎯 **Controls**: Buttons, triggers, grips, Xbox button, Game Bar\n" + \
           "🔌 **Connectivity**: USB-C, WiFi 6E, Bluetooth, microSD, audio\n" + \
           "💻 **Experience**: Xbox interface, Windows 11, optimization\n" + \
           "📱 **Use Cases**: Portable gaming, travel, home use\n" + \
           "📦 **Accessories**: What's included, stand, charger\n\n" + \
           "Just ask me anything about the ROG Xbox Ally!"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: str = Form(...)):
    response = get_chatbot_response(message)
    return {"response": response}

@app.get("/api/chat")
async def chat_api(message: str):
    response = get_chatbot_response(message)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 