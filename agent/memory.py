from typing import List, Dict, Any

class ConversationBufferMemory:
    def __init__(self, max_turns: int = 5):
        """
        Manages rolling multi-turn conversation states.
        A single turn equals 1 User message + 1 Assistant message.
        """
        self.max_turns = max_turns
        # Store history as a list of dicts: [{"role": "user"/"assistant", "content": "..."}]
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, text: str) -> None:
        """Adds a user query to the history log."""
        self.messages.append({"role": "user", "content": text})
        self._enforce_limit()

    def add_assistant_message(self, text: str) -> None:
        """Adds an agent response to the history log."""
        self.messages.append({"role": "assistant", "content": text})
        self._enforce_limit()

    def _enforce_limit(self) -> None:
        """
        Ensures the buffer does not exceed max_turns.
        Max turns * 2 items (1 user + 1 assistant) = max individual messages.
        Older entries are automatically pruned from the front.
        """
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            # Drop the oldest full turn (2 messages) from the beginning
            excess = len(self.messages) - max_messages
            self.messages = self.messages[excess:]

    def get_history_as_string(self) -> str:
        """Formats the existing log into a clean string context block."""
        if not self.messages:
            return "No prior conversation history."
            
        formatted_turns = []
        for msg in self.messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            formatted_turns.append(f"{role_label}: {msg['content']}")
            
        return "\n".join(formatted_turns)

    def clear(self) -> None:
        """Resets the internal session state."""
        self.messages = []