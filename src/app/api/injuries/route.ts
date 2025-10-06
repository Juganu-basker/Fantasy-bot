import { NextRequest, NextResponse } from 'next/server';
import { injuryReporter } from '@/lib/injuries';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const playerName = searchParams.get('player');

  try {
    if (playerName) {
      // Get status for specific player
      const status = await injuryReporter.getPlayerStatus(playerName);
      return NextResponse.json({ status });
    }

    // Get all injuries
    const injuries = await injuryReporter.getLatestInjuries();

    // Store injuries in database
    await Promise.all(injuries.map(async (injury) => {
      // Find player by name (case-insensitive)
      const player = await prisma.player.findFirst({
        where: {
          name: {
            contains: injury.player,
            mode: 'insensitive',
          },
        },
      });

      if (player) {
        await prisma.injury.upsert({
          where: {
            playerId_date: {
              playerId: player.id,
              date: new Date(injury.date),
            },
          },
          update: {
            status: injury.status,
            description: injury.reason,
          },
          create: {
            playerId: player.id,
            date: new Date(injury.date),
            status: injury.status,
            description: injury.reason,
          },
        });
      }
    }));

    return NextResponse.json({ injuries });
  } catch (error) {
    console.error('Error fetching injuries:', error);
    return NextResponse.json(
      { error: 'Failed to fetch injury report' },
      { status: 500 }
    );
  }
}
