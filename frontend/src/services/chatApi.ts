import type { ChatResponse } from "../types/chat";

const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ChatApiError extends Error {}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
  } catch (error) {
    console.error("Failed to reach SportsBuddy backend:", error);
    throw new ChatApiError(
      "Sorry, I couldn't reach SportsBuddy right now. Please try again.",
    );
  }

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body: unknown = await response.json();
      if (
        body &&
        typeof body === "object" &&
        "detail" in body &&
        typeof (body as { detail: unknown }).detail === "string"
      ) {
        detail = (body as { detail: string }).detail;
      }
    } catch {
      // Response body wasn't JSON; fall back to the generic message below.
    }

    throw new ChatApiError(
      detail ?? "Something went wrong while talking to SportsBuddy. Please try again.",
    );
  }

  try {
    return (await response.json()) as ChatResponse;
  } catch (error) {
    console.error("Received an unparseable response from SportsBuddy:", error);
    throw new ChatApiError(
      "Received an unexpected response from SportsBuddy. Please try again.",
    );
  }
}
