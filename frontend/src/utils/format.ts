// The catalogue is the source of truth for currency - never guess or
// convert based on how the user phrased their budget.
const LOCALE_BY_CURRENCY: Record<string, string> = {
  USD: "en-US",
  INR: "en-IN",
};

export function formatPrice(price: number, currency: string): string {
  try {
    return new Intl.NumberFormat(LOCALE_BY_CURRENCY[currency], {
      style: "currency",
      currency,
    }).format(price);
  } catch {
    return `${price.toFixed(2)} ${currency}`;
  }
}
