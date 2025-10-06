export class ESPNError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ESPNError';
  }
}

export class ESPNAuthenticationError extends ESPNError {
  constructor(message = 'ESPN authentication failed') {
    super(message);
    this.name = 'ESPNAuthenticationError';
  }
}

export class ESPNRateLimitError extends ESPNError {
  constructor(message = 'ESPN API rate limit exceeded') {
    super(message);
    this.name = 'ESPNRateLimitError';
  }
}

export class ESPNResponseError extends ESPNError {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public responseText?: string
  ) {
    super(message);
    this.name = 'ESPNResponseError';
  }
}

export class ESPNParseError extends ESPNError {
  constructor(message = 'Failed to parse ESPN API response') {
    super(message);
    this.name = 'ESPNParseError';
  }
}

export class ESPNNotFoundError extends ESPNError {
  constructor(resource: string) {
    super(`ESPN resource not found: ${resource}`);
    this.name = 'ESPNNotFoundError';
  }
}
