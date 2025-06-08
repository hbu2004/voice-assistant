import streamlit as st
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from tools import client_tools

load_dotenv()

st.set_page_config(
    page_title="Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
    .agent-message {
        background-color: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        text-align: left;
    }
    .activity-message {
        background-color: #ffc107;
        color: #212529;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 90%;
        font-style: italic;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
    }
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .timestamp {
        font-size: 0.8em;
        color: #666;
        margin-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

MESSAGES_FILE = "conversation_log.json"

if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = None

def write_message_to_file(msg_type, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_data = {
        "type": msg_type,
        "message": message,
        "timestamp": timestamp
    }
    
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = []
        
        messages.append(message_data)
        
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing to file: {e}")

def read_messages_from_file():
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error reading from file: {e}")
        return []

def clear_messages_file():
    try:
        if os.path.exists(MESSAGES_FILE):
            os.remove(MESSAGES_FILE)
    except Exception as e:
        print(f"Error clearing file: {e}")

def init_conversation():
    try:
        agent_id = os.getenv("AGENT_ID")
        api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not agent_id or not api_key:
            st.error("Missing AGENT_ID or ELEVENLABS_API_KEY in environment variables")
            return False
        
        elevenlabs = ElevenLabs(api_key=api_key)
        
        def on_agent_response(response):
            write_message_to_file("agent", response)
            
        def on_agent_response_correction(original, corrected):
            write_message_to_file("agent", f"Corrected: {original} → {corrected}")
            
        def on_user_transcript(transcript):
            write_message_to_file("user", transcript)
        
        conversation = Conversation(
            elevenlabs,
            agent_id,
            client_tools=client_tools,
            requires_auth=bool(api_key),
            audio_interface=DefaultAudioInterface(),
            callback_agent_response=on_agent_response,
            callback_agent_response_correction=on_agent_response_correction,
            callback_user_transcript=on_user_transcript,
        )
        
        st.session_state.conversation = conversation
        return True
        
    except Exception as e:
        st.error(f"Error initializing conversation: {str(e)}")
        return False

def start_conversation():
    if st.session_state.conversation:
        try:
            st.session_state.conversation.start_session()
            st.session_state.is_connected = True
            write_message_to_file("activity", "🚀 Connected to Voice Assistant!")
            st.session_state.last_activity = "Connected successfully"
            st.success("Connected! You can now start speaking.")
            
        except Exception as e:
            st.error(f"Error starting conversation: {str(e)}")
            write_message_to_file("activity", f"❌ Connection failed: {str(e)}")

def end_conversation():
    if st.session_state.conversation and st.session_state.is_connected:
        try:
            st.session_state.conversation.end_session()
            st.session_state.is_connected = False
            write_message_to_file("activity", "🛑 Conversation ended")
            st.session_state.last_activity = "Disconnected"
            st.success("Conversation ended successfully!")
        except Exception as e:
            st.error(f"Error ending conversation: {str(e)}")

original_searchweb = None
original_save_to_text = None
original_create_html = None

def monitor_tool_usage():
    global original_searchweb, original_save_to_text, original_create_html
    
    if original_searchweb is None:
        from tools import searchweb, save_to_text, create_html_file
        
        original_searchweb = searchweb
        original_save_to_text = save_to_text
        original_create_html = create_html_file
        
        def wrapped_searchweb(parameters):
            query = parameters.get("query", "")
            write_message_to_file("activity", f"🔍 Searching web for: {query}")
            result = original_searchweb(parameters)
            write_message_to_file("activity", f"✅ Search completed")
            return result
        
        def wrapped_save_to_text(parameters):
            filename = parameters.get("filename", "")
            write_message_to_file("activity", f"💾 Saving to file: {filename}")
            result = original_save_to_text(parameters)
            write_message_to_file("activity", f"✅ File saved successfully")
            return result
        
        def wrapped_create_html(parameters):
            filename = parameters.get("filename", "")
            title = parameters.get("title", "")
            write_message_to_file("activity", f"🌐 Creating HTML file: {filename}")
            result = original_create_html(parameters)
            write_message_to_file("activity", f"✅ HTML file created")
            return result
        
        import tools
        tools.searchweb = wrapped_searchweb
        tools.save_to_text = wrapped_save_to_text
        tools.create_html_file = wrapped_create_html

monitor_tool_usage()

st.markdown("<h1 class='main-header'>🎙️ Voice Assistant</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Controls")
    
    if st.session_state.is_connected:
        st.markdown("<div class='status-connected'>✅ Connected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-disconnected'>❌ Disconnected</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Connect", disabled=st.session_state.is_connected):
            if not st.session_state.conversation:
                if init_conversation():
                    start_conversation()
            else:
                start_conversation()
    
    with col2:
        if st.button("🛑 Disconnect", disabled=not st.session_state.is_connected):
            end_conversation()
    
    if st.button("🗑️ Clear Chat"):
        clear_messages_file()
        st.session_state.last_activity = "Chat cleared"
        st.rerun()
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    st.subheader("Environment Status")
    agent_id = os.getenv("AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    st.write(f"**Agent ID:** {'✅ Set' if agent_id else '❌ Missing'}")
    st.write(f"**API Key:** {'✅ Set' if api_key else '❌ Missing'}")
    
    if st.session_state.last_activity:
        st.subheader("Last Activity")
        st.write(st.session_state.last_activity)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Conversation")
    
    messages = read_messages_from_file()
    
    if messages:
        for chat in messages:
            timestamp = chat.get("timestamp", "")
            
            if chat["type"] == "user":
                st.markdown(f"""
                <div class='user-message'>
                    👤 {chat['message']}
                    <span class='timestamp'>{timestamp}</span>
                </div>
                """, unsafe_allow_html=True)
                
            elif chat["type"] == "agent":
                st.markdown(f"""
                <div class='agent-message'>
                    🤖 {chat['message']}
                    <span class='timestamp'>{timestamp}</span>
                </div>
                """, unsafe_allow_html=True)
                
            elif chat["type"] == "activity":
                st.markdown(f"""
                <div class='activity-message'>
                    {chat['message']}
                    <span class='timestamp'>{timestamp}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No conversation yet. Connect and start speaking to see the conversation here!")

with col2:
    st.subheader("📊 Activity Log")
    
    messages = read_messages_from_file()
    activities = [chat for chat in messages if chat["type"] == "activity"]
    
    if activities:
        st.write("**Recent Activities:**")
        for activity in activities[-5:]:
            st.write(f"• {activity['message']}")
    else:
        st.write("No activities yet")
    
    if st.session_state.is_connected:
        st.success("🎤 Listening...")
        st.write("Speak into your microphone")
        st.write(f"Total messages: {len(messages)}")
    else:
        st.warning("Not connected")

if not st.session_state.is_connected:
    st.markdown("---")
    st.subheader("🚀 Getting Started")
    
    with st.expander("Setup Instructions", expanded=True):
        st.markdown("""
        1. **Environment Variables**: Make sure you have a `.env` file with:
           ```
           AGENT_ID=your_agent_id
           ELEVENLABS_API_KEY=your_api_key
           ```
        
        2. **Audio Permissions**: Your browser will ask for microphone permissions.
        
        3. **Start Conversation**: Click "🚀 Connect" to initialize the Voice Assistant.
        
        4. **Voice Interaction**: Once connected, speak directly to the Voice Assistant.
        
        5. **Available Tools**:
           - 🔍 Web search functionality
           - 💾 Text file saving
           - 🌐 HTML file creation
        
        6. **Real-time Updates**: Messages are saved to a file and will appear when you refresh.
        """)

if st.session_state.is_connected:
    time.sleep(2)
    st.rerun()

st.markdown("---")
messages = read_messages_from_file()
st.markdown(
    f"<div style='text-align: center; color: #666;'>Built with Streamlit | Messages: {len(messages)}</div>", 
    unsafe_allow_html=True
)