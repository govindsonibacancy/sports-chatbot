import { useState } from "react";
import { ChatInput } from "./components/ChatInput";
import { ChatWindow } from "./components/ChatWindow";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ChatApiError, sendChatMessage } from "./services/chatApi";
import type { ChatMessage } from "./types/chat";

const GREETING: ChatMessage = {
  id: "greeting",
  role: "assistant",
  content:
    'Hi! I\'m SportsBuddy 👋 I can help you find sports products based on sport, category, brand, and budget. Try: "I need a badminton racket under 3000"',
};

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (text: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    setMessages((previous) => [...previous, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text);
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.message,
        products: response.products ?? [],
        totalMatches: response.total_matches ?? 0,
        requirements: response.requirements,
      };
      setMessages((previous) => [...previous, assistantMessage]);
    } catch (error) {
      const content =
        error instanceof ChatApiError
          ? error.message
          : "Sorry, I couldn't reach SportsBuddy right now. Please try again.";

      setMessages((previous) => [
        ...previous,
        { id: crypto.randomUUID(), role: "assistant", content },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <div className="app">
        <header className="app__header">
          <h1>SportsBuddy</h1>
          <p>Your AI Sports Shopping Assistant</p>
        </header>

        <main className="app__main">
          <ChatWindow messages={messages} isLoading={isLoading} />
        </main>

        <footer className="app__footer">
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
