from flask import Flask
import views
import psycopg2 as dbapi2
import os

def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", methods=["POST", "GET"], view_func=views.home_page)
    app.add_url_rule("/login", methods=["POST", "GET"], view_func=views.checkSignIn)
    app.add_url_rule("/players/detail_<int:personid>", methods=["POST","GET"], view_func=views.player_page)
    app.add_url_rule("/player/add_card_to_player_<int:playerid>", methods=["POST","GET"], view_func=views.add_card_to_player)
    app.add_url_rule("/players/search_player", methods=["POST","GET"], view_func=views.search_player)
    app.add_url_rule("/player/delete_<int:personid>", methods=["POST"], view_func=views.delete_player)
    app.add_url_rule("/player/add_goal_<int:personid>", methods=["GET","POST"], view_func=views.add_goal)
    app.add_url_rule("/players", methods=["POST", "GET"], view_func=views.players_page)
    app.add_url_rule("/teams", view_func=views.teams_page)
    app.add_url_rule("/teams/search_team", methods=["POST","GET"], view_func=views.search_team)
    app.add_url_rule("/teams/detail_<int:teamid>", methods=["POST","GET"], view_func=views.team_page)
    app.add_url_rule("/teams/delete_<int:teamid>", methods=["POST"], view_func=views.delete_team)
    app.add_url_rule("/teams/add_player_to_squad_<int:teamid>", methods=["GET","POST"], view_func=views.add_player_to_squad)
    app.add_url_rule("/teams/delete_player_from_squad_<int:playerid>", methods=["POST"], view_func=views.delete_player_from_squad)
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/leagues", view_func=views.leagues_page)
    app.add_url_rule("/league_<int:leagueid>", view_func=views.league)
    app.add_url_rule("/add_data", view_func=views.add_data_page)
    app.add_url_rule("/add_person", methods=["POST", "GET"], view_func=views.add_person)
    app.add_url_rule("/add_match", methods=["POST", "GET"], view_func=views.add_match)
    app.add_url_rule("/add_team", methods=["POST", "GET"], view_func=views.add_team)
    app.add_url_rule("/add_league", methods=["POST", "GET"], view_func=views.add_league)
    app.add_url_rule("/add_stadium", methods=["POST", "GET"], view_func=views.add_stadium)
    app.config["signed"] = False
    db_uri = os.environ.get('DB_URI', None)
    app.config['db_url'] = db_uri
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
