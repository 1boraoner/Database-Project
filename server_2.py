# from flask import Flask, render_template,current_app
# from flask_login import LoginManager
# import jinja2 as jin
# import psycopg2 as dbapi2
# import views
#
#
#
# def create_app():
#     app = Flask(__name__)
#     #get_post = ["GET","POST"]
#     app.config.from_object("settings.Config")
#
#     app.add_url_rule("/",view_func=views.home_page)
#     app.add_url_rule("/signup_page",view_func=views.home_page, methods=["GET", ])
#     app.add_url_rule("/login_page",view_func=views.home_page)
#
#
#
# app = create_app()
# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=True)#host="127.0.0.1"
