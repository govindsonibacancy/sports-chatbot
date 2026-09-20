import { useState } from "react";
import type { FormEvent } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const canSend = value.trim().length > 0 && !disabled;

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <label htmlFor="chat-input-field" className="visually-hidden">
        Ask SportsBuddy
      </label>
      <input
        id="chat-input-field"
        className="chat-input__field"
        type="text"
        placeholder="Ask SportsBuddy..."
        value={value}
        onChange={(event) => setValue(event.target.value)}
        disabled={disabled}
        autoComplete="off"
      />
      <button
        type="submit"
        className="chat-input__send"
        disabled={!canSend}
        aria-label="Send message"
      >
        ➤
      </button>
    </form>
  );
}
