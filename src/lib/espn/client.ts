import {
  ESPNConfig,
  ESPNLeagueResponse,
  ESPNPlayer,
  ESPNPlayerResponse,
  ESPNTeam,
} from './types';
import {
  ESPNAuthenticationError,
  ESPNNotFoundError,
  ESPNParseError,
  ESPNResponseError,
} from './errors';
import { RateLimiter } from './rate-limiter';

export class ESPNClient {
  private baseUrl = 'https://fantasy.espn.com/apis/v3/games/fba';
  private rateLimiter: RateLimiter;

  constructor(private config: ESPNConfig) {
    this.rateLimiter = new RateLimiter();
  }

  private get headers() {
    return {
      'Cookie': `espn_s2=${this.config.espnS2}; SWID=${this.config.swid}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Referer': 'https://fantasy.espn.com/basketball/team',
    };
  }

  private async request<T>(
    endpoint: string,
    options: {
      params?: Record<string, string>;
      headers?: Record<string, string>;
      method?: string;
      body?: any;
    } = {}
  ): Promise<T> {
    const { params = {}, headers = {}, method = 'GET', body } = options;
    
    return this.rateLimiter.withRateLimit(async () => {
      const searchParams = new URLSearchParams(params);
      const url = `${this.baseUrl}${endpoint}${searchParams.toString() ? '?' + searchParams.toString() : ''}`;

      console.log(`ESPN API Request: ${method} ${url}`);
      console.log('Headers:', { ...this.headers, ...headers, Cookie: '***REDACTED***' });

      const response = await fetch(url, {
        method,
        headers: { ...this.headers, ...headers },
        body: body ? JSON.stringify(body) : undefined,
        next: { revalidate: 300 }, // Cache for 5 minutes
      });

      // Handle common error cases
      if (response.status === 401 || response.status === 403) {
        throw new ESPNAuthenticationError();
      }

      if (response.status === 404) {
        throw new ESPNNotFoundError(endpoint);
      }

      if (!response.ok) {
        const text = await response.text();
        console.error('ESPN API Error:', {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          text: text.substring(0, 1000),
        });
        throw new ESPNResponseError(
          'ESPN API request failed',
          response.status,
          response.statusText,
          text
        );
      }

      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        const text = await response.text();
        console.error('ESPN API Non-JSON Response:', { contentType, text });
        throw new ESPNParseError('ESPN API returned non-JSON response');
      }

      try {
        return await response.json();
      } catch (error) {
        console.error('ESPN API JSON Parse Error:', error);
        throw new ESPNParseError();
      }
    });
  }

  async getLeague(options: { view?: string; scoringPeriodId?: number } = {}): Promise<ESPNLeagueResponse> {
    const { view = 'mRoster', scoringPeriodId } = options;
    
    return this.request<ESPNLeagueResponse>(
      `/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}`,
      {
        params: {
          view,
          ...(scoringPeriodId && { scoringPeriodId: String(scoringPeriodId) }),
        },
        headers: {
          'x-fantasy-filter': JSON.stringify({ filterActive: { value: true } }),
        },
      }
    );
  }

  async getTeam(teamId: number): Promise<ESPNTeam> {
    const league = await this.getLeague();
    const team = league.teams.find(t => t.id === teamId);
    
    if (!team) {
      throw new ESPNNotFoundError(`Team ${teamId}`);
    }

    return team;
  }

  async getFreeAgents(options: {
    scoringPeriodId?: number;
    limit?: number;
    offset?: number;
  } = {}): Promise<ESPNPlayer[]> {
    const { scoringPeriodId, limit = 50, offset = 0 } = options;

    const response = await this.request<ESPNPlayerResponse>(
      `/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}/players`,
      {
        params: {
          view: 'kona_player_info',
          status: 'FREEAGENT',
          limit: String(limit),
          offset: String(offset),
          ...(scoringPeriodId && { scoringPeriodId: String(scoringPeriodId) }),
        },
      }
    );

    return response.players || [];
  }

  async getPlayer(playerId: number): Promise<ESPNPlayer | null> {
    const response = await this.request<ESPNPlayerResponse>(
      `/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}/players`,
      {
        params: {
          view: 'kona_player_info',
          playerId: String(playerId),
        },
      }
    );

    return response.players?.[0] || null;
  }

  async getRecentActivity(limit = 10): Promise<any> {
    return this.request(
      `/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}/communication/`,
      {
        params: {
          view: 'kona_league_communication',
          limit: String(limit),
        },
      }
    );
  }
}

// Create a singleton instance with environment variables
export const espnClient = new ESPNClient({
  leagueId: process.env.LEAGUE_ID!,
  season: process.env.SEASON!,
  espnS2: process.env.ESPN_S2!,
  swid: process.env.SWID!,
});
