interface ESPNConfig {
  leagueId: string;
  season: string;
  espnS2: string;
  swid: string;
}

interface ESPNPlayer {
  id: number;
  fullName: string;
  proTeamId: number;
  defaultPositionId: number;
  injured: boolean;
  injuryStatus: string;
  stats: {
    averageStats?: Record<string, number>;
    stats?: Record<string, number>;
  };
}

interface ESPNTeam {
  id: number;
  name: string;
  roster: {
    entries: Array<{
      playerId: number;
      player: ESPNPlayer;
    }>;
  };
}

interface ESPNLeagueResponse {
  teams: ESPNTeam[];
}

export class ESPNClient {
  private baseUrl = 'https://fantasy.espn.com/apis/v3/games/fba';
  private config: ESPNConfig;

  constructor(config: ESPNConfig) {
    this.config = config;
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

  private async fetch<T>(endpoint: string, params: Record<string, string> = {}): Promise<T> {
    const searchParams = new URLSearchParams(params);
    const url = `${this.baseUrl}${endpoint}?${searchParams.toString()}`;

    console.log('Fetching ESPN API:', url);
    console.log('Headers:', { ...this.headers, Cookie: '***REDACTED***' });

    const response = await fetch(url, {
      headers: this.headers,
      next: { revalidate: 300 }, // Cache for 5 minutes
    });

    if (!response.ok) {
      const text = await response.text();
      console.error('ESPN API Error Response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        text: text.substring(0, 1000), // Log first 1000 chars only
      });
      throw new Error(`ESPN API error: ${response.status} ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.error('ESPN API Non-JSON Response:', {
        contentType,
        text: await response.text(),
      });
      throw new Error('ESPN API returned non-JSON response');
    }

    try {
      return await response.json();
    } catch (error) {
      console.error('ESPN API JSON Parse Error:', error);
      throw new Error('Failed to parse ESPN API response as JSON');
    }
  }

  async getLeague(view = 'mRoster'): Promise<ESPNLeagueResponse> {
    const response = await fetch(
      `${this.baseUrl}/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}?view=${view}`,
      {
        headers: {
          ...this.headers,
          'x-fantasy-filter': JSON.stringify({ filterActive: { value: true } }),
        },
        next: { revalidate: 300 },
      }
    );

    if (!response.ok) {
      const text = await response.text();
      console.error('ESPN League API Error:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        text: text.substring(0, 1000),
      });
      throw new Error(`ESPN API error: ${response.status} ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.error('ESPN League API Non-JSON Response:', {
        contentType,
        text: await response.text(),
      });
      throw new Error('ESPN API returned non-JSON response');
    }

    try {
      return await response.json();
    } catch (error) {
      console.error('ESPN League API JSON Parse Error:', error);
      throw new Error('Failed to parse ESPN API response as JSON');
    }
  }

  async getTeamRoster(teamId: number): Promise<ESPNTeam> {
    const league = await this.getLeague();
    const team = league.teams.find(t => t.id === teamId);
    
    if (!team) {
      throw new Error(`Team with ID ${teamId} not found`);
    }

    return team;
  }

  async getFreeAgents(): Promise<ESPNPlayer[]> {
    const response = await this.fetch<any>(
      `/seasons/${this.config.season}/segments/0/leagues/${this.config.leagueId}/players`,
      {
        view: 'kona_player_info',
        status: 'FREEAGENT',
      }
    );

    return response.players || [];
  }
}

// Create a singleton instance with environment variables
export const espnClient = new ESPNClient({
  leagueId: process.env.LEAGUE_ID!,
  season: process.env.SEASON!,
  espnS2: process.env.ESPN_S2!,
  swid: process.env.SWID!,
});
