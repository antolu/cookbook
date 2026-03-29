/**
 * Format time in minutes to human-readable string
 */
export function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Parse time string to minutes
 */
export function parseTime(timeStr: string): number | null {
  if (!timeStr) return null;

  const timeStr_ = timeStr.toLowerCase().trim();

  // Extract number and unit
  const match = timeStr_.match(/(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|h|m)?/);
  if (!match) return null;

  const value = parseFloat(match[1]);
  const unit = match[2] || 'minutes';

  // Convert to minutes
  if (['hours', 'hour', 'hrs', 'hr', 'h'].includes(unit)) {
    return Math.round(value * 60);
  } else {
    return Math.round(value);
  }
}

/**
 * Format duration for display
 */
export function formatDuration(minutes?: number): string {
  if (!minutes) return 'N/A';
  return formatTime(minutes);
}
