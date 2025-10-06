import { NextResponse } from 'next/server';
import { espnClient } from '@/lib/espn';

export async function GET() {
  try {
    // Log environment variables (redacted)
    console.log('ESPN API Configuration:', {
      leagueId: process.env.LEAGUE_ID || 'NOT_SET',
      season: process.env.SEASON || 'NOT_SET',
      espnS2: process.env.ESPN_S2 ? `${process.env.ESPN_S2.substring(0, 5)}...` : 'NOT_SET',
      swid: process.env.SWID ? `${process.env.SWID.substring(0, 5)}...` : 'NOT_SET',
    });

    // First try a direct fetch to test authentication
    const testUrl = `https://fantasy.espn.com/apis/v3/games/fba/seasons/${process.env.SEASON}/segments/0/leagues/${process.env.LEAGUE_ID}?view=mTeam`;
    console.log('Testing direct ESPN API access:', testUrl);

    const response = await fetch(testUrl, {
      headers: {
        'Cookie': `espn_s2=${process.env.ESPN_S2}; SWID=${process.env.SWID}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://fantasy.espn.com/basketball/team',
      },
    });

    console.log('ESPN API Response Status:', response.status);
    console.log('ESPN API Response Headers:', Object.fromEntries(response.headers.entries()));

    const contentType = response.headers.get('content-type');
    console.log('Content-Type:', contentType);

    const text = await response.text();
    console.log('Response Text Preview:', text.substring(0, 500));

    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.error('Failed to parse response as JSON:', e);
      return NextResponse.json({
        success: false,
        error: {
          name: 'ParseError',
          message: 'Failed to parse ESPN API response as JSON',
          details: {
            status: response.status,
            contentType,
            responsePreview: text.substring(0, 500),
          },
        },
      }, { status: 500 });
    }

    // If we got here, we successfully parsed the JSON
    return NextResponse.json({
      success: true,
      data: {
        leagueId: data.id,
        name: data.settings?.name,
        teams: data.teams?.map(team => ({
          id: team.id,
          name: team.name,
          playerCount: team.roster?.entries?.length || 0,
        })),
        status: {
          currentMatchupPeriod: data.status?.currentMatchupPeriod,
          latestScoringPeriod: data.status?.latestScoringPeriod,
        },
      },
    });

  } catch (error) {
    console.error('ESPN API Test Error:', error);
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? {
        name: error.name,
        message: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
      } : 'Unknown error',
      config: {
        leagueId: process.env.LEAGUE_ID ? 'SET' : 'NOT_SET',
        season: process.env.SEASON ? 'SET' : 'NOT_SET',
        espnS2: process.env.ESPN_S2 ? 'SET' : 'NOT_SET',
        swid: process.env.SWID ? 'SET' : 'NOT_SET',
      },
    }, { 
      status: 500 
    });
  }
}