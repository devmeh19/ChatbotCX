# ROG Xbox Ally Chatbot

A modern, interactive chatbot web application designed to answer queries about the ROG Xbox Ally handheld gaming device. Built with FastAPI and featuring a beautiful Xbox-themed UI.

## 🎮 Features

- **Intelligent Chatbot**: AI-powered responses about ROG Xbox Ally specifications and features
- **Modern UI**: Xbox-themed design with responsive layout
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Quick Questions**: Pre-built question buttons for common queries
- **Device Information**: Comprehensive specs and feature overview
- **Mobile Responsive**: Works seamlessly on all devices

## 🚀 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with Xbox theme
- **Icons**: Font Awesome
- **Server**: Uvicorn

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## 🎯 What the Chatbot Knows

The chatbot is trained on comprehensive information about the ROG Xbox Ally devices:

### Device Models
- **ROG Xbox Ally X**: 24GB RAM, 1TB storage, AMD Ryzen AI Z2 Extreme
- **ROG Xbox Ally**: 16GB RAM, 512GB storage, AMD Ryzen Z2 A

### Specifications
- **Processor**: AMD Ryzen AI Z2 Extreme / Z2 A
- **Memory**: 16GB/24GB LPDDR5X RAM
- **Storage**: 512GB/1TB M.2 2280 SSD (upgradeable)
- **Display**: 7" FHD (1080p) IPS, 120Hz, 500 nits
- **Battery**: 60Wh/80Wh for extended gaming

### Gaming Features
- **Xbox Game Pass**: Instant access to hundreds of games
- **Cloud Gaming**: Xbox Cloud Gaming (Beta) support
- **Xbox Play Anywhere**: Buy once, play anywhere
- **Remote Play**: Play Xbox console games remotely

### Controls & Interface
- **Xbox-Inspired Controls**: ABXY buttons, contoured grips
- **Advanced Triggers**: Impulse triggers (Ally X) or Hall Effect (Ally)
- **Xbox Experience**: Full-screen Xbox interface optimized for handheld
- **Game Bar**: Quick access to tools and widgets

### Connectivity
- **WiFi 6E** and **Bluetooth 5.4**
- **USB-C ports** with DisplayPort support
- **microSD card reader** for expandable storage
- **3.5mm audio jack**

## 💬 Sample Questions

Try asking the chatbot:

- "What are the differences between Ally and Ally X?"
- "Does it support Xbox Game Pass?"
- "What are the specifications?"
- "How does cloud gaming work?"
- "Tell me about the controls"
- "What's the battery life like?"
- "Can I upgrade the storage?"
- "How does the display look?"

## 🔧 API Endpoints

- **GET /** - Main chat interface
- **POST /chat** - Send a message and get response
- **GET /api/chat?message=...** - API endpoint for programmatic access

## 🎨 Customization

### Adding New Knowledge

To add new information to the chatbot, edit the `CHATBOT_KNOWLEDGE` dictionary in `main.py`:

```python
CHATBOT_KNOWLEDGE = {
    "new_category": {
        "new_topic": "Your new information here"
    }
}
```

### Modifying Responses

Update the `get_chatbot_response()` function to handle new keywords and provide appropriate responses.

### Styling Changes

Modify the CSS in `templates/index.html` to change colors, fonts, or layout.

## 🌐 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
For production deployment, consider using:
- **Gunicorn** with FastAPI
- **Docker** containerization
- **Cloud platforms** like Heroku, AWS, or Azure

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Gaming handhelds

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `main.py` or kill the process using the port
2. **Dependencies not found**: Ensure you've run `pip install -r requirements.txt`
3. **Template not found**: Ensure the `templates` folder exists with `index.html`

### Error Logs

Check the console output for any error messages when running the application.

## 🤝 Contributing

Feel free to contribute by:
- Adding new features
- Improving the knowledge base
- Enhancing the UI/UX
- Fixing bugs
- Adding new API endpoints

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Microsoft Xbox for the ROG Xbox Ally product information
- FastAPI team for the excellent web framework
- Font Awesome for the beautiful icons

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the console logs
3. Ensure all dependencies are installed
4. Verify the file structure is correct

---

**Happy Gaming with ROG Xbox Ally! 🎮✨** 