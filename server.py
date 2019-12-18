from flask import Flask
from flask_login import LoginManager
import views
import psycopg2 as dbapi2
import os
from classes import User
from datetime import timedelta

SECRET_KEY = "15151009163008301724"
login_manager = LoginManager()
db_uri = os.environ.get('DB_URI', None)

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        get_user = "SELECT a.username, a.password, a.name, a.age, a.email FROM ACCOUNT a WHERE(a.username='%s')"%(user_id)
        user = views.getOneRowQuery(db_uri, get_user)
        user = User(user[0], user[1], user[2], user[4], user[3])
        return user
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return views.checkSignIn()


def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", methods=["POST", "GET"], view_func=views.home_page)
    app.add_url_rule("/login", methods=["POST", "GET"], view_func=views.checkSignIn)
    app.add_url_rule("/logout", methods=["POST", "GET"], view_func=views.logOut)
    app.add_url_rule("/signup", methods=["POST", "GET"], view_func=views.signUp)
    app.add_url_rule("/update_user", methods=["POST", "GET"], view_func=views.update_account)
    app.add_url_rule("/delete_user", methods=["POST", "GET"], view_func=views.signUp)
    app.add_url_rule("/players/detail_<int:personid>", methods=["POST","GET"], view_func=views.player_page)
    app.add_url_rule("/player/add_card_to_player_<int:playerid>", methods=["POST","GET"], view_func=views.add_card_to_player)
    app.add_url_rule("/player/delete_card_<int:cardid>", methods=["POST"], view_func=views.delete_card)
    app.add_url_rule("/player/delete_goal_<int:goalid>", methods=["POST"], view_func=views.delete_goal)
    app.add_url_rule("/substitution/delete_<int:subid>", methods=["POST"], view_func=views.delete_substitution)
    app.add_url_rule("/players/search_player", methods=["POST","GET"], view_func=views.search_player)
    app.add_url_rule("/player/delete_<int:personid>", methods=["POST"], view_func=views.delete_player)
    app.add_url_rule("/player/add_goal_<int:personid>", methods=["GET","POST"], view_func=views.add_goal)
    app.add_url_rule("/person/update_<int:personid>", methods=["GET","POST"], view_func=views.update_person)
    app.add_url_rule("/players", methods=["POST", "GET"], view_func=views.players_page)
    app.add_url_rule("/coachs", methods=["POST", "GET"], view_func=views.coachs_page)
    app.add_url_rule("/coachs/search_coach", methods=["POST","GET"], view_func=views.search_coach)
    app.add_url_rule("/coachs/detail_<int:personid>", methods=["POST","GET"], view_func=views.coach_page)
    app.add_url_rule("/teams", view_func=views.teams_page)
    app.add_url_rule("/teams/search_team", methods=["POST","GET"], view_func=views.search_team)
    app.add_url_rule("/teams/detail_<int:teamid>", methods=["POST","GET"], view_func=views.team_page)
    app.add_url_rule("/teams/update_<int:teamid>", methods=["POST","GET"], view_func=views.update_team)
    app.add_url_rule("/teams/add_player_to_squad_<int:teamid>", methods=["GET","POST"], view_func=views.add_player_to_squad)
    app.add_url_rule("/teams/delete_player_from_squad_<int:playerid>", methods=["POST"], view_func=views.delete_player_from_squad)
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/match_detail_<int:matchid>", methods=["POST","GET"], view_func=views.match_detail)
    app.add_url_rule("/add_match_detail_<int:matchid>", methods=["POST","GET"], view_func=views.add_match_detail)
    app.add_url_rule("/delete_match_<int:matchid>", methods=["POST","GET"], view_func=views.delete_match)
    app.add_url_rule("/leagues", view_func=views.leagues_page)
    app.add_url_rule("/league_<int:leagueid>", methods=["POST","GET"], view_func=views.league)
    app.add_url_rule("/add_data", view_func=views.add_data_page)
    app.add_url_rule("/add_person", methods=["POST", "GET"], view_func=views.add_person)
    app.add_url_rule("/add_match", methods=["POST", "GET"], view_func=views.add_match)
    app.add_url_rule("/add_team", methods=["POST", "GET"], view_func=views.add_team)
    app.add_url_rule("/add_league", methods=["POST", "GET"], view_func=views.add_league)
    app.add_url_rule("/add_stadium", methods=["POST", "GET"], view_func=views.add_stadium)
    app.add_url_rule("/stadiums", view_func=views.stadiums_page)
    app.add_url_rule("/stadiums/search_stadium", methods=["POST","GET"], view_func=views.search_stadium)
    app.add_url_rule("/stadiums/order_by_<int:ordertype>", methods=["POST","GET"], view_func=views.order_stadium)
    app.add_url_rule("/stadiums/update_<int:stadiumid>", methods=["POST","GET"], view_func=views.update_stadium)
    app.config['db_url'] = db_uri
    app.config['SECRET_KEY'] = "15151009163008301724"
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(seconds=5)
    login_manager.init_app(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
