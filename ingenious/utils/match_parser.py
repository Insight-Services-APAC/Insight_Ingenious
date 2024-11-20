import json


class MatchDataParser:
    def __init__(self, payload, event_type):
        self.data = json.loads(payload)
        self.fixture = self.data.get("fixture", {})
        self.players = self.data.get("players", [])
        self.balls = self.data.get("balls", [])
        self.pay_load_type = event_type

    def get_team_info(self, team_key):
        team = self.fixture.get(team_key, {})
        return {
            "id": team.get("id"),
            "name": team.get("name", "Unknown Team"),
            "short_name": team.get("shortName", "Unknown"),
            "logo_url": team.get("logoUrl", "")
        }

    def get_player_info(self, player_id):
        player = next((p for p in self.players if p.get("id") == player_id), {})
        return {
            "id": player.get("id"),
            "name": player.get("displayName", "Unknown Player"),
            "team_id": player.get("teamId")
        }

    def get_current_batters(self):
        current_batters = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            # Filter batsmen who have faced balls
            active_batsmen = [b for b in batsmen if b.get("ballsFaced", 0) > 0]
            # Sort by batting order to get most recent
            active_batsmen.sort(key=lambda x: x.get("battingOrder", 0), reverse=True)
            # Get the two most recent active batters
            recent_batters = active_batsmen[:2]

            for batter in recent_batters:
                player_info = self.get_player_info(batter.get("playerId"))
                current_batters.append({
                    "player_id": player_info["id"],
                    "name": player_info["name"],
                    "team_id": player_info["team_id"],
                    "balls_faced": batter.get("ballsFaced", 0),
                    "runs_scored": batter.get("runsScored", 0),
                    "strike_rate": batter.get("strikeRate", 0),
                    "is_on_strike": batter.get("isOnStrike", False),
                    "batting_order": batter.get("battingOrder", 0)
                })

        return current_batters

    def get_match_summary(self):
        home_team = self.get_team_info("homeTeam")
        away_team = self.get_team_info("awayTeam")
        result = self.fixture.get("resultText", "Result not available")
        venue = self.fixture.get("venue", {}).get("name", "Unknown Venue")
        competition = self.fixture.get("competition", {}).get("name", "Unknown Competition")

        simple_summary = (
            f"Match: {competition} at {venue}\n"
            f"Teams: {home_team['name']} (ID: {home_team['id']}) vs "
            f"{away_team['name']} (ID: {away_team['id']})\n"
            f"Result: {result}\n"
        )

        over_number = self.balls[0].get("OverNumber", "0")
        ball_number = self.balls[0].get("BallNumber", "0")
        over_ball = f"{over_number}.{ball_number}"
        time_stamp = self.balls[0].get("BallDateTime", "0")
        match_id = self.fixture.get("competition", {}).get("id", "Unknown Match_id")
        feed_id = '<sample-feed-id>'

        return over_ball, time_stamp, match_id, feed_id, simple_summary

    def get_innings_summary(self):
        innings_data = self.fixture.get("innings", [])
        summaries = []

        for inning in innings_data:
            batting_team_id = inning.get("battingTeamId")
            batting_team = next(
                (team_key for team_key in ["homeTeam", "awayTeam"]
                 if self.fixture.get(team_key, {}).get("id") == batting_team_id),
                "Unknown Team"
            )
            team_info = self.get_team_info(batting_team)
            runs_scored = inning.get("runsScored", 0)
            wickets = inning.get("numberOfWicketsFallen", 0)
            overs = inning.get("oversBowled", "0.0")
            extras = inning.get("totalExtras", 0)
            overs_float = (float(overs.split('.')[0]) +
                           float(overs.split('.')[1]) / 6 if '.' in overs else float(overs))
            run_rate = round(runs_scored / overs_float if overs_float else 0, 2)

            summaries.append(
                f"{team_info['name']} (ID: {team_info['id']}) Innings:\n"
                f"Score: {runs_scored}/{wickets} in {overs} overs\n"
                f"Run Rate: {run_rate}\n"
                f"Extras: {extras}"
            )

        return "\n\n".join(summaries)

    def get_batting_highlights(self):
        highlights = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            top_scorers = sorted(
                batsmen,
                key=lambda x: x.get("runsScored", 0),
                reverse=True
            )[:3]
            for batsman in top_scorers:
                runs = batsman.get("runsScored", 0)
                balls = batsman.get("ballsFaced", 0)
                strike_rate = batsman.get("strikeRate", 0)
                player_id = batsman.get("playerId")
                player_info = self.get_player_info(player_id)
                milestones = []
                if runs >= 50 and runs < 100:
                    milestones.append("half-century")
                elif runs >= 100:
                    milestones.append("century")
                highlight_text = (
                    f"{player_info['name']} (ID: {player_info['id']}, "
                    f"Team ID: {player_info['team_id']}) scored {runs} runs "
                    f"off {balls} balls (SR: {strike_rate})"
                )
                if milestones:
                    highlight_text += f" achieving a {' and '.join(milestones)}"
                highlights.append(highlight_text)
        return highlights

    def get_bowling_highlights(self):
        highlights = []
        for inning in self.fixture.get("innings", []):
            bowlers = inning.get("bowlers", [])
            top_bowlers = sorted(
                bowlers,
                key=lambda x: (x.get("wicketsTaken", 0), -float(x.get("economy", 99))),
                reverse=True
            )[:3]
            for bowler in top_bowlers:
                wickets = bowler.get("wicketsTaken", 0)
                overs = bowler.get("oversBowled", "0")
                runs_conceded = bowler.get("runsConceded", 0)
                economy = bowler.get("economy", 0)
                player_id = bowler.get("playerId")
                player_info = self.get_player_info(player_id)
                milestones = []
                if wickets >= 5:
                    milestones.append("five-wicket haul")
                highlight_text = (
                    f"{player_info['name']} (ID: {player_info['id']}, "
                    f"Team ID: {player_info['team_id']}) took {wickets} wickets "
                    f"for {runs_conceded} runs in {overs} overs (Econ: {economy})"
                )
                if milestones:
                    highlight_text += f" achieving a {' and '.join(milestones)}"
                highlights.append(highlight_text)
        return highlights

    def get_key_partnerships(self):
        partnerships = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            sorted_batsmen = sorted(
                batsmen,
                key=lambda x: x.get("runsScored", 0),
                reverse=True
            )

            for i in range(len(sorted_batsmen) - 1):
                batsman1 = sorted_batsmen[i]
                batsman2 = sorted_batsmen[i + 1]
                runs1 = batsman1.get("runsScored", 0)
                runs2 = batsman2.get("runsScored", 0)

                if runs1 + runs2 >= 50:
                    player1_info = self.get_player_info(batsman1.get("playerId"))
                    player2_info = self.get_player_info(batsman2.get("playerId"))
                    partnerships.append(
                        f"Significant partnership between "
                        f"{player1_info['name']} (ID: {player1_info['id']}, {runs1}) "
                        f"and {player2_info['name']} (ID: {player2_info['id']}, "
                        f"{runs2}), total: {runs1 + runs2} runs"
                    )
        return partnerships

    def get_momentum_shifts(self):
        momentum_shifts = []
        for inning in self.fixture.get("innings", []):
            batting_team_id = inning.get("battingTeamId")
            batting_team = next(
                (team_key for team_key in ["homeTeam", "awayTeam"]
                 if self.fixture.get(team_key, {}).get("id") == batting_team_id),
                "Unknown Team"
            )
            team_info = self.get_team_info(batting_team)

            bowlers = inning.get("bowlers", [])
            for bowler in bowlers:
                wickets = bowler.get("wicketsTaken", 0)
                overs = bowler.get("oversBowled", "0")
                if wickets >= 2:
                    player_info = self.get_player_info(bowler.get("playerId"))
                    momentum_shifts.append(
                        f"Momentum Shift: {player_info['name']} "
                        f"(ID: {player_info['id']}) took {wickets} wickets in "
                        f"{overs} overs against {team_info['name']} "
                        f"(ID: {team_info['id']})"
                    )

            batsmen = inning.get("batsmen", [])
            for batsman in batsmen:
                runs = batsman.get("runsScored", 0)
                strike_rate = batsman.get("strikeRate", 0)
                if runs >= 30 and strike_rate >= 150:
                    player_info = self.get_player_info(batsman.get("playerId"))
                    momentum_shifts.append(
                        f"Momentum Shift: {player_info['name']} "
                        f"(ID: {player_info['id']}) scored {runs} runs at a "
                        f"strike rate of {strike_rate}"
                    )

        return momentum_shifts

    def get_current_batters(self):
        """
        Gets the most recent two batters who have faced balls in the match.
        """
        current_batters = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            # Filter out batsmen who never faced a ball
            active_batsmen = [b for b in batsmen if b.get("ballsFaced", 0) > 0]
            # Sort by batting order descending to get most recent first
            active_batsmen.sort(key=lambda x: x.get("battingOrder", 0), reverse=True)
            # Get the two most recent active batters
            recent_batters = active_batsmen[:2]

            for batter in recent_batters:
                player_info = self.get_player_info(batter.get("playerId"))
                current_batters.append({
                    "player_id": player_info["id"],
                    "name": player_info["name"],
                    "team_id": player_info["team_id"],
                    "balls_faced": batter.get("ballsFaced", 0),
                    "runs_scored": batter.get("runsScored", 0),
                    "strike_rate": batter.get("strikeRate", 0),
                    "is_on_strike": batter.get("isOnStrike", False),
                    "batting_order": batter.get("battingOrder", 0),
                    "fours": batter.get("foursScored", 0),
                    "sixes": batter.get("sixesScored", 0),
                    "dismissal_text": batter.get("dismissalText", ""),
                    "is_out": batter.get("isOut", False)
                })

        return current_batters

    def create_detailed_summary(self):
        overBall, time_stamp, match_id, feed_id, match_narrative = self.get_match_summary()
        innings_details = self.get_innings_summary()
        batting_highlights = self.get_batting_highlights()
        bowling_highlights = self.get_bowling_highlights()
        partnerships = self.get_key_partnerships()
        momentum_shifts = self.get_momentum_shifts()
        current_batters = self.get_current_batters()

        # Create batters text without the section title
        current_batters_formatted = []
        for batter in current_batters:
            status = "batting" if not batter['is_out'] else batter['dismissal_text']
            batter_text = (
                f"{batter['name']} (ID: {batter['player_id']}, Team ID: {batter['team_id']}): "
                f"{batter['runs_scored']} runs ({batter['fours']}x4, {batter['sixes']}x6) "
                f"off {batter['balls_faced']} balls (SR: {batter['strike_rate']}) "
                f"{status} {'*' if batter['is_on_strike'] else ''}"
            )
            current_batters_formatted.append(batter_text)

        current_batters_text = "\n".join(current_batters_formatted) if current_batters else ""

        sections = [
            ("Payload Type", self.pay_load_type),
            ("Match Summary", match_narrative),
            ("Current/Recent Batters", current_batters_text),
            ("Innings Details", innings_details),
            ("Batting Highlights", "\n".join(batting_highlights)),
            ("Bowling Highlights", "\n".join(bowling_highlights)),
            ("Key Partnerships", "\n".join(partnerships)),
            ("Momentum Shifts", "\n".join(momentum_shifts))
        ]

        return "\n\n".join(
            f"{title}:\n{content}" for title, content in sections if content.strip()
        ), overBall, time_stamp, match_id, feed_id