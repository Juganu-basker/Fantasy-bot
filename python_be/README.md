# Fantasy Basketball FastAPI Server

This FastAPI server provides endpoints to interact with ESPN Fantasy Basketball data.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and fill in your ESPN credentials:
```
ESPN_LEAGUE_ID=your_league_id
ESPN_SEASON_ID=your_season_id
ESPN_SWID=your_swid_cookie
ESPN_S2=your_espn_s2_cookie
```

To get your ESPN cookies (SWID and ESPN_S2):
1. Log in to ESPN Fantasy
2. Open browser developer tools (F12)
3. Go to Application/Storage > Cookies
4. Find and copy the values for SWID and ESPN_S2

## Running the Server

Start the server with:
```bash
uvicorn main:app --reload
```

The server will start at http://localhost:8000

## Available Endpoints

- GET `/api/v1/team/{team_id}` - Get team details
- GET `/api/v1/league/standings` - Get league standings
- GET `/api/v1/league/scoreboard` - Get league scoreboard
- GET `/api/v1/league/fantasycast` - Get live scoring
- GET `/api/v1/players/news` - Get player news
- GET `/api/v1/league/leaders` - Get league leaders

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc
