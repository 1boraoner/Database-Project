from flask import Flask, render_template,current_app, request, session, url_for, jsonify, redirect
from flask_login import LoginManager
import jinja2 as jin
import db_init
import psycopg2 as dbapi2
import classes as entity
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

url = """ user='postgres' password='bora' host='localhost' port='5432' dbname='postgres' """
app = Flask(__name__)
app.secret_key = "victoriasecret"

@app.route("/")
def home_page():
    return render_template('home_page.html')


@app.route("/home/signup_page", methods=["GET","POST"])
def signup_page():
    if request.method == "POST":
        if "nationality" in request.form.keys():
            data = request.form
            new_artist = entity.artist(data["name"],data["surname"],data["nationality"],data["contact_add"],data["art_style"],data["password"])
            with dbapi2.connect(url) as connection:
                cursor = connection.cursor()
                cmd = '''INSERT INTO photographer(artist_name,artist_surname,nationality, contact_add, artist_style, password) VALUES(%s,%s,%s,%s,%s,%s) RETURNING artist_id'''
                new_inf = [new_artist.name,new_artist.surname,new_artist.nationality, new_artist.contact, new_artist.style, new_artist.password]
                cursor.execute(cmd,new_inf)
                the_artist_id = cursor.fetchone()[0]
                print(the_artist_id)
                print(type(the_artist_id))

                connection.commit()
                cmd = """ INSERT INTO portfolio(artist_id) VALUES(%s)"""
                cursor.execute(cmd,(the_artist_id,))
                connection.commit()
                cursor.close()
        else:
            data = request.form
            new_user = entity.user(data["name"],data["surname"],data["contact_info"],data["password"])
            with dbapi2.connect(url) as connection:
                cursor = connection.cursor()
                cmd = '''INSERT INTO users(user_name,surname,contact, password) VALUES(%s,%s,%s,%s) RETURNING user_id'''
                new_inf = [new_user.name, new_user.surname, new_user.contact, new_user.password]
                cursor.execute(cmd,new_inf)

                the_user_id = cursor.fetchone()[0]
                connection.commit()

                cmd = """ INSERT INTO fav_list(user_id) VALUES(%s)"""
                cursor.execute(cmd,(the_user_id,))
                connection.commit()

                cursor.close()
        return render_template('home_page.html')
    return render_template('signup_page.html')


@app.route("/home/login_page", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":
        data = request.form
        print(data)
        if data["type"] == "on": #check box is ticked
            with dbapi2.connect(url) as connection:
                cursor = connection.cursor()
                cursor.execute('''SELECT * FROM photographer''')
                table = cursor.fetchall()
                cursor.close()

            for rows in table:
                if data["name"] == rows[1] and data["surname"] == rows[2] and data["password"] == rows[6]:

                    sess_artist = entity.artist(rows[1],rows[2], rows[3], rows[4], rows[5],rows[6])
                    sess_artist.artist_id_setter(rows[0])

                    session["flag"] = 1
                    session["type"] = "artist"
                    session["occupy_id"] = sess_artist.artist_id
                    print(session)
                    print(sess_artist)
                    return redirect(url_for("artist_page", name =str(sess_artist.name)+"_"+str(sess_artist.surname)))
        else:
            sess_user = entity.artist(data["name"], data["surname"], data["password"])
            with dbapi2.connect(url) as connection:
                cursor = connection.cursor()
                cursor.execute('''SELECT * FROM users''')
                table = cursor.fetchall()
                cursor.close()

            for rows in table:
                if data["name"] == rows[1] and data["surname"] == rows[2] and data["password"] == rows[6]:
                    sess_user = entity.artist(rows[1], rows[2], rows[3], rows[4], rows[5], rows[6])
                    sess_user.artist_id_setter(rows[0])

                    session["flag"] = 1           #logged in flag
                    session["type"] = "user"      #log in type
                    session["occupy"] = sess_user #session variable
                    return render_template(url_for("user_page"))


    return render_template("login_page.html")


@app.route("/artist")
def main_artist():
    return "This is the artist_page"

@app.route("/artist/<name>", methods=["GET","POST"])
def artist_page(name):
    if session["flag"] == 1:
        curr_artist_id = session["occupy_id"]
    else:
        return render_template("home_page.html")

    if request.method == "GET":

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM photographer WHERE artist_id=%s"""
            cursor.execute(cmd,(curr_artist_id,))
            curr_artist = cursor.fetchone()
            cursor.close()

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM portfolio WHERE artist_id=%s"""
            cursor.execute(cmd,(curr_artist_id,))
            portfolio = cursor.fetchall()
            cursor.close()

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM photograph WHERE artist_id=%s"""
            cursor.execute(cmd, (curr_artist_id,))
            photos_raw = cursor.fetchall()
            cursor.close()

            photos =list()
            for i in range(len(photos_raw)):
                photos.append(photos_raw[i][6])
                photos[i] = photos[i].tobytes()
                photos[i] = base64.b64encode(photos[i])  ##b64 encoding
                photos[i] = photos[i].decode()

            print(photos)
        return render_template("artist_page.html", name = name, artist_sess = curr_artist,artist_port = portfolio, photos_raw =photos_raw, photos =photos)



@app.route("/artist/<name>/upload", methods=["GET", "POST"])
def upload(name):
    if "flag" in session or session["flag"] == 1:
        curr_artist_id = session["occupy_id"]
    else:
        return render_template("home_page.html")

    if request.method == "POST":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT portfolio_id FROM portfolio WHERE artist_id=%s"""
            cursor.execute(cmd,(curr_artist_id,))
            portfolio_id = cursor.fetchone()[0]
            cursor.close()

        image = request.files["filename"]
        content = image.read()
        print(content)
        print(type(content))

        category = request.form["category"]
        location_info = request.form["details"]
        tec_details = request.form["location"]

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """INSERT INTO photograph(artist_id,portfolio_id,category,location_info,tec_details,image_cont) VALUES(%s,%s,%s,%s,%s,%s) RETURNING image_cont"""
            cursor.execute(cmd,(curr_artist_id,portfolio_id,category,location_info,tec_details,content))
            inserted_im = cursor.fetchone()[0]
            connection.commit()
            cursor.close()

        image_s = inserted_im.tobytes()
        encoded = base64.b64encode(image_s) ##b64 encoding
        str=  encoded.decode() ## b' atar
        #image_data = inserted_im  # byte values of the image
        #image_s = Image.open(io.BytesIO(image_data))
        #image_s.show()

        return render_template("upload.html", inserted = str, raw = content)

    if request.method == "GET":
        return render_template("upload.html", inserted ="")


@app.route("/home/user_page")
def user_page():
    return render_template("user_page.html")



@app.route("/home/deneme", methods=["GET","POST"])
def deneme():
    if request.method == "POST":
        data = request.form
        print(data)
        return render_template("home_page.html")
    else:
        return render_template("deneme.html")


if __name__ == "__main__":
    db_init.init_database()
    app.run(host="127.0.0.1", port=8080, debug=True)#host="127.0.0.1"
