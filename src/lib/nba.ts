interface NBAGameLog {
  gameId: string;
  gameDate: string;
  matchup: string;
  minutes: number;
  points: number;
  assists: number;
  rebounds: number;
  steals: number;
  blocks: number;
  turnovers: number;
  fgm: number;
  fga: number;
  ftm: number;
  fta: number;
  tpm: number;
  tpa: number;
}

interface NBAStatsResponse {
  resultSets: Array<{
    name: string;
    headers: string[];
    rowSet: any[][];
  }>;
}

export class NBAStatsClient {
  private baseUrl = 'https://stats.nba.com/stats';

  private get headers() {
    return {
      'Host': process.env.NBA_API_HOST || 'stats.nba.com',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'application/json',
      'Accept-Language': 'en-US,en;q=0.9',
      'Referer': process.env.NBA_API_REFERER || 'https://www.nba.com/',
      'Origin': 'https://www.nba.com',
      'Connection': 'keep-alive',
    };
  }

  private async fetch<T>(endpoint: string, params: Record<string, string> = {}): Promise<T> {
    const searchParams = new URLSearchParams(params);
    const url = `${this.baseUrl}${endpoint}?${searchParams.toString()}`;

    const response = await fetch(url, {
      headers: this.headers,
      next: { revalidate: 3600 }, // Cache for 1 hour
    });

    if (!response.ok) {
      throw new Error(`NBA Stats API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  private parseGameLog(response: NBAStatsResponse): NBAGameLog[] {
    const resultSet = response.resultSets[0];
    const headers = resultSet.headers;
    
    return resultSet.rowSet.map(row => {
      const game: any = {};
      headers.forEach((header, index) => {
        game[header.toLowerCase()] = row[index];
      });
      
      return {
        gameId: game.game_id,
        gameDate: game.game_date,
        matchup: game.matchup,
        minutes: game.min,
        points: game.pts,
        assists: game.ast,
        rebounds: game.reb,
        steals: game.stl,
        blocks: game.blk,
        turnovers: game.tov,
        fgm: game.fgm,
        fga: game.fga,
        ftm: game.ftm,
        fta: game.fta,
        tpm: game.fg3m,
        tpa: game.fg3a,
      };
    });
  }

  async getPlayerGameLog(playerId: number, season = '2024-25'): Promise<NBAGameLog[]> {
    const response = await this.fetch<NBAStatsResponse>(
      '/playergamelog',
      {
        'PlayerID': playerId.toString(),
        'Season': season,
        'SeasonType': 'Regular Season',
      }
    );

    return this.parseGameLog(response);
  }

  async getPlayerSeasonAverages(playerId: number, season = '2024-25'): Promise<any> {
    const response = await this.fetch<NBAStatsResponse>(
      '/playerprofilev2',
      {
        'PlayerID': playerId.toString(),
        'PerMode': 'PerGame',
        'Season': season,
      }
    );

    // Parse and return season averages
    const seasonStats = response.resultSets.find(set => set.name === 'SeasonTotalsRegularSeason');
    if (!seasonStats || !seasonStats.rowSet.length) {
      throw new Error('Season stats not found');
    }

    const stats = {};
    seasonStats.headers.forEach((header, index) => {
      stats[header.toLowerCase()] = seasonStats.rowSet[0][index];
    });

    return stats;
  }
}

// Create a singleton instance
export const nbaClient = new NBAStatsClient();
