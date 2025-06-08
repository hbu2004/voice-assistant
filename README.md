# 🎙️ Voice Assistant

A real-time voice assistant built with ElevenLabs Conversational AI and Streamlit, featuring web search, file operations, and live conversation tracking.

## ✨ Features

- **Voice Interaction**: Real-time speech-to-text and text-to-speech
- **Web Search**: Integrated web search functionality using DuckDuckGo
- **File Operations**: Save conversations to text files and create HTML reports
- **Live Interface**: Real-time conversation display with Streamlit web interface
- **Tool Monitoring**: Track assistant activities and tool usage

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd voice-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit elevenlabs python-dotenv langchain-community duckduckgo-search
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   AGENT_ID=your_elevenlabs_agent_id
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

## 🚀 Usage

### Command Line Interface
```bash
python main.py
```

### Web Interface
```bash
streamlit run streamlit_app.py
```
Then open your browser to `http://localhost:8501`

## 📁 Project Structure

```
voice-assistant/
├── main.py              # Command line interface
├── streamlit_app.py     # Web interface
├── tools.py             # Assistant tools (search, file operations)
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore file
├── README.md           # This file
└── venv/               # Virtual environment (not in git)
```

## 🔧 Available Tools

The assistant has access to these tools:

- **🔍 Web Search**: Search the internet for information
- **💾 Text File Saving**: Save conversations and summaries to text files
- **🌐 HTML Creation**: Generate HTML reports and webpages

## 💬 Example Commands

- "Search for the latest news about AI"
- "Save our conversation to a text file"
- "Create a webpage summary of what we discussed"
- "Search for Python programming tutorials"

## 🎯 Web Interface Features

- Real-time conversation display
- Activity monitoring
- Connection status indicator
- Tool usage tracking
- Message timestamps
- Auto-refresh functionality

## 📋 Requirements

- Python 3.7+
- ElevenLabs API account and API key
- Microphone access for voice input
- Internet connection for web search

## 🔑 Environment Variables

- `AGENT_ID`: Your ElevenLabs agent ID
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## ⚠️ Important Notes

- Never commit your `.env` file with API keys
- Ensure you have proper microphone permissions
- The assistant requires an active internet connection for web search functionality