"""Command-line interface for Jarvis AI Assistant."""

from __future__ import annotations

import asyncio

from app.config import ensure_directories
from app.core.brain import Brain
from app.memory.database import Database
from app.memory.preferences import PreferencesManager
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.cli")

BANNER = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
       AI Assistant v1.0.0 — CLI Mode
"""

HELP_TEXT = """
Commands:
  /help           Show this help message
  /status         Show system status
  /history        Show conversation history
  /clear          Clear conversation context
  /voice <text>   Speak text aloud (TTS)
  /quit           Exit Jarvis

Otherwise, just type your command or question naturally.
Examples:
  > open chrome
  > what's the cpu usage?
  > remind me to study at 8 pm
  > search for python tutorials
"""


async def run_cli() -> None:
    """Run the Jarvis CLI."""
    print(BANNER)
    ensure_directories()

    brain = Brain()
    db = Database()
    await db.connect()
    prefs = PreferencesManager(db)

    greeting_name = await prefs.get("greeting_name", "User")
    print(f"Hello, {greeting_name}! I'm Jarvis, your AI assistant.")
    print("Type /help for available commands.\n")

    try:
        while True:
            try:
                user_input = input("You > ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd == "/quit" or cmd == "/exit":
                    print("Goodbye!")
                    break
                elif cmd == "/help":
                    print(HELP_TEXT)
                    continue
                elif cmd == "/clear":
                    brain.context.clear()
                    print("Context cleared.\n")
                    continue
                elif cmd == "/history":
                    for turn in brain.context.get_history():
                        role = turn["role"].upper()
                        print(f"  [{role}] {turn['content']}")
                    print()
                    continue
                elif cmd == "/status":
                    from app.monitoring.system_monitor import SystemMonitor

                    monitor = SystemMonitor()
                    report = monitor.get_full_report()
                    cpu = report["cpu"]
                    mem = report["memory"]
                    print(f"  CPU: {cpu.get('percent', 'N/A')}%")
                    print(f"  RAM: {mem.get('percent', 'N/A')}% "
                          f"({mem.get('used_gb', '?')}/{mem.get('total_gb', '?')} GB)")
                    battery = report.get("battery", {})
                    if battery.get("has_battery"):
                        print(f"  Battery: {battery.get('percent')}%")
                    print()
                    continue
                elif cmd.startswith("/voice "):
                    text = user_input[7:]
                    from app.voice.tts import TextToSpeech

                    tts = TextToSpeech()
                    path = await tts.synthesize(text)
                    print(f"  Audio saved: {path}\n")
                    continue

            # Process through the brain
            result = await brain.process(user_input)

            response = result.get("response", "")
            intent = result.get("intent", "")
            action = result.get("action", "")
            confidence = result.get("confidence", 0)

            if result.get("type") == "confirmation_required":
                print(f"\nJarvis > ⚠️  {response}")
            elif result.get("type") == "command":
                print(f"\nJarvis > Executing: {action} [{intent}] (confidence: {confidence:.2f})")
                if response:
                    print(f"         {response}")
            else:
                print(f"\nJarvis > {response}")

            print()

    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        await brain.close()
        await db.close()


def main() -> None:
    """Entry point for the CLI."""
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
