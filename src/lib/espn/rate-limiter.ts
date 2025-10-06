interface RateLimitRule {
  windowMs: number;  // Time window in milliseconds
  maxRequests: number;  // Maximum requests allowed in the window
}

interface RequestRecord {
  timestamp: number;
}

export class RateLimiter {
  private requests: RequestRecord[] = [];
  private rules: RateLimitRule[];

  constructor(rules: RateLimitRule[] = [
    { windowMs: 1000, maxRequests: 2 },     // 2 requests per second
    { windowMs: 60000, maxRequests: 60 },   // 60 requests per minute
    { windowMs: 3600000, maxRequests: 1000 } // 1000 requests per hour
  ]) {
    this.rules = rules;
  }

  async checkRateLimit(): Promise<void> {
    // Clean up old requests
    const now = Date.now();
    const oldestWindow = Math.max(...this.rules.map(r => r.windowMs));
    this.requests = this.requests.filter(r => now - r.timestamp < oldestWindow);

    // Check each rule
    for (const rule of this.rules) {
      const windowStart = now - rule.windowMs;
      const requestsInWindow = this.requests.filter(r => r.timestamp > windowStart).length;

      if (requestsInWindow >= rule.maxRequests) {
        const waitMs = Math.min(...this.requests
          .filter(r => r.timestamp > windowStart)
          .map(r => r.timestamp + rule.windowMs - now)
        );

        // Wait until we can make another request
        await new Promise(resolve => setTimeout(resolve, waitMs));
        return this.checkRateLimit(); // Recheck after waiting
      }
    }

    // Record this request
    this.requests.push({ timestamp: now });
  }

  async withRateLimit<T>(fn: () => Promise<T>): Promise<T> {
    await this.checkRateLimit();
    return fn();
  }
}
