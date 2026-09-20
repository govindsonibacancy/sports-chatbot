import type { ChatMessage as ChatMessageType, ChatRequirements } from "../types/chat";
import { ProductCard } from "./ProductCard";

interface ChatMessageProps {
  message: ChatMessageType;
}

interface CriteriaEntry {
  label: string;
  value: string;
}

function getCriteriaEntries(requirements: ChatRequirements): CriteriaEntry[] {
  const entries: CriteriaEntry[] = [];

  if (requirements.sport) entries.push({ label: "Sport", value: requirements.sport });
  if (requirements.category) entries.push({ label: "Category", value: requirements.category });
  if (requirements.subcategory) {
    entries.push({ label: "Subcategory", value: requirements.subcategory });
  }
  if (requirements.brand) entries.push({ label: "Brand", value: requirements.brand });
  // We don't know what currency the user meant, so the budget is shown as a
  // plain number rather than guessing a currency symbol.
  if (requirements.max_price !== null) {
    entries.push({ label: "Budget", value: `≤ ${requirements.max_price}` });
  }

  return entries;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const products = message.products ?? [];
  const totalMatches = message.totalMatches ?? 0;
  const criteriaEntries = message.requirements ? getCriteriaEntries(message.requirements) : [];

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      <span className="chat-message__role">{isUser ? "You" : "SportsBuddy"}</span>
      <p className="chat-message__content">{message.content}</p>

      {!isUser && criteriaEntries.length > 0 && (
        <div className="chat-message__criteria">
          <span className="chat-message__criteria-title">Search criteria</span>
          <ul>
            {criteriaEntries.map((entry) => (
              <li key={entry.label}>
                {entry.label}: {entry.value}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!isUser && products.length > 0 && (
        <>
          <p className="chat-message__result-count">
            {totalMatches} matching product{totalMatches === 1 ? "" : "s"}
          </p>
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
