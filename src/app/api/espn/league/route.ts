import { NextResponse } from 'next/server';
import { espnClient } from '@/lib/espn';
import { prisma } from '@/lib/db';

export async function GET() {
  try {
    // Fetch league data from ESPN
    const leagueData = await espnClient.getLeague();

    // Extract all players from teams
    const players = leagueData.teams.flatMap(team => 
      team.roster.entries.map(entry => ({
        id: entry.playerId,
        name: entry.player.fullName,
        team: String(entry.player.proTeamId),
        position: String(entry.player.defaultPositionId),
        injured: entry.player.injured,
        injuryStatus: entry.player.injuryStatus,
      }))
    );

    // Upsert players into database
    await Promise.all(players.map(player =>
      prisma.player.upsert({
        where: { id: player.id },
        update: player,
        create: player,
      })
    ));

    return NextResponse.json({
      teams: leagueData.teams.map(team => ({
        id: team.id,
        name: team.name,
        players: team.roster.entries.map(entry => ({
          id: entry.playerId,
          name: entry.player.fullName,
          team: entry.player.proTeamId,
          position: entry.player.defaultPositionId,
          injured: entry.player.injured,
          injuryStatus: entry.player.injuryStatus,
          stats: entry.player.stats,
        })),
      })),
    });
  } catch (error) {
    console.error('Error fetching league data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch league data' },
      { status: 500 }
    );
  }
}
