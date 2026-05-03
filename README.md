# Jarvis AI Assistant

A **production-level local AI assistant** built with Python, FastAPI, React, and Ollama. Jarvis can understand natural language (English + Hindi), control your system, automate tasks, and act as a personal assistant — all running locally on your machine.

## Features

### Core Intelligence (Brain)
- Natural Language Understanding (NLU) with intent detection and entity extraction
- Multi-turn conversation handling with context memory
- Confidence scoring with rule-based and LLM-based classification
- Personalization — learns user habits over time

### Voice Interface
- Wake word detection ("Jarvis")
- Speech-to-text via **faster-whisper** (local, offline)
- Text-to-speech via **edge-tts** with pyttsx3 fallback
- Noise filtering with WebRTC VAD
- Hindi + English support

### System Control
- **App Control**: Open, close, switch, minimize, maximize applications
- **OS Operations**: Shutdown, restart, lock screen, sleep (with confirmation)
- **File Manager**: Create, delete, move, copy, search files and folders
- **Volume & Brightness**: Adjust volume, mute/unmute, brightness control
- **Battery Monitoring**: Real-time battery status

### Web Automation
- Google search and open websites by name
- Browser automation and URL opening
- Web scraping (text extraction)
- File downloading

### AI Capabilities (Ollama LLM)
- Q&A and general conversation
- Code debugging and generation
- Content generation and summarization
- Translation
- Streaming responses

### Task Automation
- **Scheduled Tasks**: Cron-based and interval-based scheduling
- **Event Triggers**: Battery low, high CPU/memory, and custom triggers
- **Multi-step Workflows**: Dependency-aware sequential execution

### Personal Assistant
- Reminders with recurring support
- To-do list with priorities and tags
- Calendar event management
- Alarm system with snooze
- Daily briefing generator

### Communication
- Send and read emails (SMTP/IMAP)
- System notifications (cross-platform)

### System Monitoring
- Real-time CPU, RAM, disk, network stats
- Battery status
- Process list (top processes by CPU)

### Security
- Password-based authentication with session tokens
- Voice authentication (basic voice print matching)
- Risky action confirmation system
- Path traversal protection

### Plugin System
- Modular plugin architecture with `BasePlugin` class
- Auto-discovery and loading from plugins directory
- Hot-reload support
- Built-in example and weather plugins

### Advanced Control
- Mouse and keyboard control (pyautogui)
- Screenshot capture
- Screen recording (ffmpeg)
- Presentation control

### Memory System
- **Long-term**: SQLite database for conversations, preferences, commands
- **Short-term**: Redis cache with in-memory fallback
- Conversation history search
- User preference learning

### Frontend Dashboard
- Modern React UI with dark theme
- Real-time chat via WebSocket
- System monitor with live metrics
- Command history log
- Settings panel

### Developer Features
- Async/await throughout
- Event-driven architecture
- Comprehensive logging with rotation
- Error handling with custom exceptions
- Rate limiting via Redis
- Full test suite

---

## Tech Stack

| Component    | Technology                         |
|-------------|-----------------------------------|
| Backend     | Python 3.10+ / FastAPI / Uvicorn  |
| AI/LLM      | Ollama (local inference)          |
| Voice STT   | faster-whisper                    |
| Voice TTS   | edge-tts / pyttsx3               |
| Automation   | pyautogui / Playwright            |
| Database     | SQLite (via aiosqlite)            |
| Cache        | Redis (with in-memory fallback)   |
| Frontend     | React 18 / Vite                   |
| DevOps       | Docker / docker-compose           |

---

## Project Structure

```
jarvis-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration management
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Brain, intent, NLU, LLM
│   │   ├── voice/               # STT, TTS, wake word
│   │   ├── system/              # App, OS, file, volume control
│   │   ├── automation/          # Web, scheduler, workflows
│   │   ├── assistant/           # Reminders, todos, calendar
│   │   ├── communication/       # Email, notifications
│   │   ├── monitoring/          # System resource monitoring
│   │   ├── security/            # Auth, confirmations
│   │   ├── plugins/             # Plugin system
│   │   ├── advanced/            # Input control, screenshots
│   │   ├── memory/              # Database, cache, preferences
│   │   └── utils/               # Logger, errors, helpers
│   ├── cli.py                   # CLI mode
│   └── pyproject.toml           # Python project config
├── frontend/                    # React dashboard
├── plugins/                     # User plugins
├── tests/                       # Test suite
├── docker-compose.yml
├── Dockerfile
├── setup.sh
└── README.md
```

---

## Quick Start

### Option 1: Local Setup

```bash
# Clone the repository
git clone https://github.com/karanrathod7031/jarvis-ai-assistant.git
cd jarvis-ai-assistant

# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -e "backend/[dev]"

# Copy environment config
cp .env.example .env

# Start the backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start the frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Option 2: Docker

```bash
docker-compose up --build
```

### Option 3: CLI Mode

```bash
source venv/bin/activate
cd backend
python cli.py
```

---

## API Endpoints

Once running, visit **http://localhost:8000/docs** for interactive API documentation.

### Core
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/assistant/command` | Process a text command |
| POST | `/api/assistant/voice` | Process voice input (audio file) |
| GET  | `/api/assistant/history` | Get conversation history |
| WS   | `/ws` | WebSocket for real-time chat |

### System
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/system/app/open` | Open an application |
| POST | `/api/system/app/close` | Close an application |
| POST | `/api/system/os/shutdown` | Shutdown system |
| POST | `/api/system/os/lock` | Lock screen |
| POST | `/api/system/file/create` | Create a file |
| GET  | `/api/system/file/search` | Search files |
| POST | `/api/system/volume` | Control volume |
| POST | `/api/system/brightness` | Control brightness |

### Monitoring
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/monitoring/status` | Full system status |
| GET | `/api/monitoring/cpu` | CPU info |
| GET | `/api/monitoring/memory` | Memory info |
| GET | `/api/monitoring/processes` | Process list |

### Automation
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/automation/web/search` | Google search |
| POST | `/api/automation/web/open` | Open URL |
| POST | `/api/automation/workflow/create` | Create workflow |

### Plugins
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET  | `/api/plugins/list` | List plugins |
| POST | `/api/plugins/execute` | Execute plugin command |

---

## Configuration

Edit `.env` to customize:

```env
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Voice
WAKE_WORD=jarvis
TTS_VOICE=en-US-GuyNeural
STT_MODEL=base
LANGUAGE=en

# Security
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-password
```

---

## Installing Ollama (for AI features)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3

# Verify
ollama list
```

---

## Running Tests

```bash
source venv/bin/activate
cd backend
pytest ../tests/ -v --tb=short
```

---

## Creating Plugins

1. Create a directory under `plugins/`:
```
plugins/my_plugin/
├── __init__.py
└── plugin.py
```

2. Extend `BasePlugin`:
```python
from app.plugins.base import BasePlugin, PluginInfo

class MyPlugin(BasePlugin):
    def get_info(self):
        return PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            commands=["my_command"],
        )

    def get_commands(self):
        return ["my_command"]

    async def execute(self, command, args):
        return {"status": "success", "message": "Hello from my plugin!"}
```

3. Restart Jarvis — plugins are auto-discovered.

---

## Example Usage

### CLI Mode
```
You > open chrome
Jarvis > Executing: open_app [system_control] (confidence: 0.85)

You > what's the cpu usage?
Jarvis > CPU: 23.5% | RAM: 61.2% (4.89/8.00 GB)

You > remind me to study DSA at 8 pm
Jarvis > Reminder set: "study DSA" at 8:00 PM

You > search for python machine learning tutorials
Jarvis > Opening Google search...

You > shutdown
Jarvis > ⚠️ Are you sure you want to shutdown? Confirm with 'yes' or 'no'.
You > no
Jarvis > Cancelled: shutdown.
```

### WebSocket (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
ws.send(JSON.stringify({ text: 'open youtube' }));
```

---

## Known Limitations

1. **Ollama required for AI**: Without Ollama running, the assistant falls back to rule-based responses
2. **Voice features require hardware**: Microphone needed for STT; speakers for TTS
3. **Platform-specific**: Some system control features are Linux-first (volume, brightness)
4. **Redis optional**: Falls back to in-memory cache when Redis is unavailable
5. **Email requires credentials**: SMTP/IMAP credentials needed for email features
6. **WhatsApp automation**: Not included for safety/ToS compliance — can be added via plugin
7. **Voice authentication**: Basic implementation using cosine similarity — not production-grade biometric

---

## License

MIT License — see [LICENSE](LICENSE) for details.
