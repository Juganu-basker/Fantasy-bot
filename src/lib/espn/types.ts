export interface ESPNConfig {
  leagueId: string;
  season: string;
  espnS2: string;
  swid: string;
}

export interface ESPNStats {
  averageStats?: Record<string, number>;
  stats?: Record<string, number>;
  // Add specific stat fields as we discover them
  points?: number;
  rebounds?: number;
  assists?: number;
  steals?: number;
  blocks?: number;
  turnovers?: number;
  fieldGoalPercentage?: number;
  freeThrowPercentage?: number;
  threePointsMade?: number;
}

export interface ESPNPlayer {
  id: number;
  fullName: string;
  proTeamId: number;
  defaultPositionId: number;
  eligibleSlots: number[];
  injured: boolean;
  injuryStatus: string;
  ownership?: {
    percentOwned: number;
    percentStarted: number;
  };
  stats: ESPNStats;
}

export interface ESPNRosterEntry {
  playerId: number;
  player: ESPNPlayer;
  lineupSlotId: number;
  acquisitionDate?: number;
}

export interface ESPNTeam {
  id: number;
  name: string;
  abbrev: string;
  location?: string;
  nickname?: string;
  roster: {
    entries: ESPNRosterEntry[];
  };
}

export interface ESPNLeagueSettings {
  name: string;
  size: number;
  isPublic: boolean;
  scoringPeriodId: number;
  seasonId: number;
  draftSettings?: {
    date: number;
    type: string;
  };
  rosterSettings?: {
    lineupSlotCounts: Record<string, number>;
    positionLimits: Record<string, number>;
  };
}

export interface ESPNLeagueResponse {
  gameId: number;
  id: number;
  settings: ESPNLeagueSettings;
  status: {
    currentMatchupPeriod: number;
    latestScoringPeriod: number;
  };
  teams: ESPNTeam[];
}

export interface ESPNPlayerResponse {
  players: ESPNPlayer[];
}
