/**
 * Formats an ISO date string into a human-readable format.
 * @example formatDate("2024-01-15T00:00:00Z") // "15 Jan 2024"
 */
export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
