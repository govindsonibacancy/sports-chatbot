export type Intent = "product_search" | "general_question" | "unknown";

export interface ChatRequirements {
  intent: Intent;
  query: string | null;
  sport: string | null;
  category: string | null;
  subcategory: string | null;
  brand: string | null;
  max_price: number | null;
  user_skill_level: string | null;
}

// Matches the raw product records returned by the backend catalogue
// (backend/data/sports-shop-products.json via ChatResponse.products).
export interface Product {
  id: string;
  name: string;
  brand: string;
  sport: string;
  category: string;
  subcategory: string;
  price: number;
  originalPrice: number;
  currency: string;
  rating: number;
  reviewCount: number;
  inStock: boolean;
  stockQuantity: number;
  description: string;
  features: string[];
  colors: string[];
  sizes: string[];
  gender: string;
  isNew: boolean;
  isBestSeller: boolean;
  sku: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: string;
  requirements: ChatRequirements;
  products: Product[];
  total_matches: number;
}

// Frontend-only conversation state, not sent to the backend.
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  totalMatches?: number;
  requirements?: ChatRequirements;
}
