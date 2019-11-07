from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import views
import psycopg2 as dbapi2



def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", methods=["POST", "GET"], view_func=views.home_page)
    app.add_url_rule("/players/detail_<int:personid>", methods=["POST","GET"], view_func=views.player_page)
    app.add_url_rule("/player/delete_<int:personid>", methods=["POST"], view_func=views.delete_player)
    app.add_url_rule("/players", methods=["POST", "GET"], view_func=views.players_page)
    app.add_url_rule("/teams", view_func=views.teams_page)
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/leagues", view_func=views.leagues_page)
    app.add_url_rule("/add_data", view_func=views.add_data_page)
    app.add_url_rule("/add_person", methods=["POST", "GET"], view_func=views.add_person)
    app.add_url_rule("/add_team", methods=["POST", "GET"], view_func=views.add_team)
    app.add_url_rule("/add_league", methods=["POST", "GET"], view_func=views.add_league)
    app.add_url_rule("/add_stadium", methods=["POST", "GET"], view_func=views.add_stadium)
    app.config['db_url'] = 'postgres://postgres:docker@localhost:5432/football'
    return app



if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
