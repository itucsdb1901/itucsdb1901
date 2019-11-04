from flask import Flask

import views


def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/players", view_func=views.players_page)
    app.add_url_rule("/teams", view_func=views.teams_page)
    app.add_url_rule("/matches", view_func=views.matches_page)
    app.add_url_rule("/leagues", view_func=views.leagues_page)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
