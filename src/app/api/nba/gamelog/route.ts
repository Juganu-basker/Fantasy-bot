import { NextRequest, NextResponse } from 'next/server';
import { nbaClient } from '@/lib/nba';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const playerId = searchParams.get('playerId');
  const season = searchParams.get('season') || '2024-25';

  if (!playerId) {
    return NextResponse.json(
      { error: 'Player ID is required' },
      { status: 400 }
    );
  }

  try {
    const gameLog = await nbaClient.getPlayerGameLog(Number(playerId), season);

    // Store game stats in database
    await Promise.all(gameLog.map(game =>
      prisma.stats.upsert({
        where: {
          playerId_date: {
            playerId: Number(playerId),
            date: new Date(game.gameDate),
          },
        },
        update: {
          minutes: game.minutes,
          points: game.points,
          rebounds: game.rebounds,
          assists: game.assists,
          steals: game.steals,
          blocks: game.blocks,
          turnovers: game.turnovers,
          fgm: game.fgm,
          fga: game.fga,
          ftm: game.ftm,
          fta: game.fta,
          tpm: game.tpm,
          tpa: game.tpa,
        },
        create: {
          playerId: Number(playerId),
          date: new Date(game.gameDate),
          minutes: game.minutes,
          points: game.points,
          rebounds: game.rebounds,
          assists: game.assists,
          steals: game.steals,
          blocks: game.blocks,
          turnovers: game.turnovers,
          fgm: game.fgm,
          fga: game.fga,
          ftm: game.ftm,
          fta: game.fta,
          tpm: game.tpm,
          tpa: game.tpa,
        },
      })
    ));

    return NextResponse.json({ games: gameLog });
  } catch (error) {
    console.error('Error fetching game log:', error);
    return NextResponse.json(
      { error: 'Failed to fetch game log' },
      { status: 500 }
    );
  }
}
