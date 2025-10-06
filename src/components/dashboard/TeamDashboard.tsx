'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface Player {
  id: number;
  name: string;
  team: string;
  position: string;
  injured: boolean;
  injuryStatus: string;
  stats: {
    averageStats?: Record<string, number>;
  };
}

interface Team {
  id: number;
  name: string;
  players: Player[];
}

export function TeamDashboard() {
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeam = async () => {
      try {
        const response = await fetch('/api/espn/league');
        const data = await response.json();
        setTeam(data.teams[0]); // Assuming first team is user's team
      } catch (err) {
        setError('Failed to fetch team data');
      } finally {
        setLoading(false);
      }
    };

    fetchTeam();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!team) {
    return <div>No team data available</div>;
  }

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-4">{team.name}</h1>
      <div className="grid gap-4">
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
          <div className="p-0">
            <table className="w-full">
              <thead>
                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                  <th className="h-12 px-4 text-left align-middle font-medium">Player</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Position</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Team</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Status</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">PPG</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">RPG</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">APG</th>
                </tr>
              </thead>
              <tbody>
                {team.players.map((player) => (
                  <tr
                    key={player.id}
                    className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                  >
                    <td className="p-4 align-middle">{player.name}</td>
                    <td className="p-4 align-middle">{player.position}</td>
                    <td className="p-4 align-middle">{player.team}</td>
                    <td className="p-4 align-middle">
                      <span
                        className={cn(
                          'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
                          player.injured
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        )}
                      >
                        {player.injured ? player.injuryStatus : 'Active'}
                      </span>
                    </td>
                    <td className="p-4 align-middle">
                      {player.stats.averageStats?.points?.toFixed(1) || '-'}
                    </td>
                    <td className="p-4 align-middle">
                      {player.stats.averageStats?.rebounds?.toFixed(1) || '-'}
                    </td>
                    <td className="p-4 align-middle">
                      {player.stats.averageStats?.assists?.toFixed(1) || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
