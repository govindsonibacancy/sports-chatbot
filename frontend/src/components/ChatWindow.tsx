import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "../types/chat";
import { ChatMessage } from "./ChatMessage";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
}

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  return (
    <div className="chat-window" aria-live="polite">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="chat-message chat-message--assistant">
          <span className="chat-message__role">SportsBuddy</span>
          <p className="chat-message__content chat-message__content--typing">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="visually-hidden">SportsBuddy is thinking…</span>
          </p>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
