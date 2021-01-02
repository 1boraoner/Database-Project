from flask import Flask, render_template, request, session, url_for, redirect
import psycopg2 as dbapi2
import base64
from random import randint

import db_init
import classes as entity


url = """ user='postgres' password='bora' host='localhost' port='5432' dbname='postgres' """
app = Flask(__name__)
app.secret_key = "victoriasecret"

@app.route("/", methods=["GET","POST"])
def home_page():
    session["flag"] = 0
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

                full_name = str(new_user.name) + " "+ str(new_user.surname)
                cmd = """ INSERT INTO fav_list(user_id,list_name) VALUES(%s,%s)"""
                cursor.execute(cmd,(the_user_id,full_name))
                connection.commit()

                cursor.close()
        return render_template('home_page.html')
    return render_template('signup_page.html')


@app.route("/home/login_page", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":
        data = request.form
        if 'type' in data.keys(): #check box is ticked
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
                    session["occupy_name"]= str(sess_artist.name)+"_"+str(sess_artist.surname)


                    return redirect(url_for("artist_page", name =str(sess_artist.name)+"_"+str(sess_artist.surname)))
        else:
            with dbapi2.connect(url) as connection:
                cursor = connection.cursor()
                cursor.execute('''SELECT * FROM users''')
                table = cursor.fetchall()
                cursor.close()

            for rows in table:
                if data["name"] == rows[1] and data["surname"] == rows[2] and data["password"] == str(rows[4]):

                    sess_user = entity.user(rows[1], rows[2], rows[3], rows[4])
                    sess_user.user_id_setter(rows[0])

                    session["flag"] = 1           #logged in flag
                    session["type"] = "user"      #log in type
                    session["occupy_id"] = sess_user.userid #session variable
                    session["occupy_name"] = str(rows[1]) + " " + str(rows[2])

                    return redirect(url_for("deneme"))


    return render_template("login_page.html")


@app.route("/logout")
def logout_page():
    session.pop("flag")
    session.pop("occupy_id")
    session.pop("occupy_name")
    session.pop("type")
    session["flag"] = 0
    return render_template("home_page.html")

@app.route("/artist/<name>", methods=["GET","POST"])
def artist_page(name):
    if session["flag"] == 1:
        curr_artist_id = session["occupy_id"]
    else:
        return render_template("home_page.html")

    if request.method == "POST":

        to_delete = request.form.getlist("delete_this")
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()

            for delete_id in to_delete:

                cmd = """DELETE FROM photograph WHERE photo_id=%s"""
                cursor.execute(cmd, (delete_id,))
                connection.commit()

                cmd = """DELETE FROM exib_content WHERE photo_id=%s"""
                cursor.execute(cmd, (delete_id,))
                connection.commit()

                cmd = """DELETE FROM fav_content WHERE photo_id=%s"""
                cursor.execute(cmd, (delete_id,))
                connection.commit()

            cursor.close()

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
            photos.append(photos_raw[i][7])
            photos[i] = photos[i].tobytes()
            photos[i] = base64.b64encode(photos[i])  #b64 encoding
            photos[i] = photos[i].decode()


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

        category = request.form["category"]
        location_info = request.form["details"]
        tec_details = request.form["location"]
        photo_name = request.form["photo_name"]

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """INSERT INTO photograph(artist_id,portfolio_id,photo_name,category,location_info,tec_details,image_cont) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING image_cont"""
            cursor.execute(cmd,(curr_artist_id,portfolio_id,photo_name,category,location_info,tec_details,content))
            inserted_im = cursor.fetchone()[0]
            connection.commit()
            cursor.close()

        image_s = inserted_im.tobytes()
        encoded = base64.b64encode(image_s) #b64 encoding
        str=  encoded.decode() # b' atar

        return render_template("upload.html", name=name, inserted = str, raw = content) #raw silinebilir debugda kullanılmıştı

    if request.method == "GET":
        return render_template("upload.html", name=name, inserted ="")


@app.route("/artist/<name>/exhibition_create", methods=["GET","POST"])
def create_exhibition(name):
    if "flag" in session:
        curr_artist_id = session["occupy_id"]
    else:
        return render_template("home_page.html")


    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cmd = """SELECT * FROM photograph WHERE artist_id=%s"""
        cursor.execute(cmd, (curr_artist_id,))
        photos_raw = cursor.fetchall()
        cursor.close()


#        photo_cont = map(lambda image:base64.b64encode(image.tobytes()).decode(), photo_cont)
        photos = list()
        for i in range(len(photos_raw)):
            photos.append(photos_raw[i][7])
            photos[i] = photos[i].tobytes()
            photos[i] = base64.b64encode(photos[i])  #b64 encoding
            photos[i] = photos[i].decode()

    if request.method == "POST":

        exhb_id = randint(1,100000)
        exhb_name = request.form["exhb_name"]
        date_inf = request.form["date_inf"]
        duration = request.form["duration"]
        photo_ids = request.form.getlist("checked")

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """INSERT INTO exhibition(exhibition_id,exhibition_name,date_inf,duration,artist_id) VALUES(%s,%s,%s,%s,%s)"""
            cursor.execute(cmd,(exhb_id,exhb_name,date_inf,duration,curr_artist_id))
            connection.commit()
            cmd = """INSERT INTO exib_content(photo_id, exhibition_id,artist_id) VALUES(%s,%s,%s)"""
            for id in photo_ids:
                cursor.execute(cmd,(id,exhb_id,curr_artist_id))
                connection.commit()
            cursor.close()

        return redirect(url_for("artist_page", name = name))

    return render_template("create_exhibition.html", name=name, photo_string = photos_raw, photo_cont= photos)

@app.route("/artist/<name>/exhibition", methods=["GET","POST"])
def exhibition(name):

    if request.method == "POST":
        eid = request.form["eid"]

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()

            cmd = """DELETE FROM exib_content WHERE exhibition_id=%s"""
            cursor.execute(cmd, (eid,))
            connection.commit()

            cmd = """DELETE FROM exhibition WHERE exhibition_id=%s"""
            cursor.execute(cmd, (eid,))
            connection.commit()
            cursor.close()

        return redirect(url_for("deneme"))

    if request.method == "GET":

        current_artist = session["occupy_id"]

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()

            cmd = """SELECT * FROM exhibition WHERE artist_id=%s"""
            cursor.execute(cmd,(current_artist,))
            the_exhibition = cursor.fetchone()
            connection.commit()
            cmd = """SELECT photo_id FROM exib_content WHERE artist_id=%s """
            cursor.execute(cmd,(current_artist,))
            the_exhibition_content =cursor.fetchall()
            connection.commit()

            photos_raw = list()
            for photo_id in the_exhibition_content:
                cmd = """SELECT * FROM photograph WHERE photo_id=%s"""
                cursor.execute(cmd, (photo_id[0],))
                photos_raw.append(cursor.fetchall())

            cursor.close()

        photos =list()
        for i in range(len(photos_raw)):
            photos.append(photos_raw[i][0][7])
            photos[i] = photos[i].tobytes()
            photos[i] = base64.b64encode(photos[i])  #b64 encoding
            photos[i] = photos[i].decode()

        return render_template("exhibition.html", exhib_inf=the_exhibition, photos=photos, photos_raw = photos_raw)



@app.route("/home/user_page")
def user_page():

    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cmd = """SELECT fav_list_id,list_name FROM fav_list WHERE user_id=%s"""
        cursor.execute(cmd,(session["occupy_id"],))
        fav_inf = cursor.fetchone()
        fav_id = fav_inf[0]
        fav_list_name = fav_inf[1]
        connection.commit()

        cmd_2 = '''SELECT* FROM fav_content WHERE fav_list_id = %s'''
        cursor.execute(cmd_2,(fav_id,))
        connection.commit()
        photos_fav = cursor.fetchall()

        photos_raw = list()
        for photo_id in photos_fav:
            cmd = """SELECT * FROM photograph WHERE photo_id=%s"""
            cursor.execute(cmd, (photo_id[0],))
            photos_raw.append(cursor.fetchall())
            connection.commit()

        cmd_3 = '''SELECT* FROM users WHERE user_id = %s'''
        cursor.execute(cmd_3, (session["occupy_id"],))
        connection.commit()
        user_inf = cursor.fetchone()
        cursor.close()

        photos_raw_clean = list()
        for i in range(len(photos_raw)):
            if len(photos_raw[i]) == 0 :
                continue
            else:
                photos_raw_clean.append(photos_raw[i])
        #photo_raw = filter(lambda x:len(x) != 0, photos_raw)


        photos =list()
        for i in range(len(photos_raw_clean)):
            photos.append(photos_raw_clean[i][0][7])
            photos[i] = photos[i].tobytes()
            photos[i] = base64.b64encode(photos[i])  #b64 encoding
            photos[i] = photos[i].decode()


    return render_template("user_page.html",user_inf = user_inf, fav_inf = fav_list_name, photos=photos, photos_raw=photos_raw_clean )

@app.route("/home/deneme", methods=["GET","POST"]) #platform main page sends {exhibition_ids,exhib_name} and artist_ids, artist_name_surname
def deneme():

    if request.method == "GET":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd_1 = """SELECT artist_id,artist_name,artist_surname FROM photographer """ #get all artist
            cursor.execute(cmd_1)
            art_data = cursor.fetchall()
            connection.commit()

            cmd_2 = """SELECT exhibition_id, exhibition_name FROM exhibition """
            cursor.execute(cmd_2)
            exhb_data = cursor.fetchall()
            connection.commit()

            cursor.close()

        dict_art = dict()
        dict_exhb = dict()

        for i in range(len(art_data)):
            dict_art.update({art_data[i][0] : str(str(art_data[i][1]) +"_" + str(art_data[i][2]))})

        for j in range(len(exhb_data)):
            dict_exhb.update({exhb_data[j][0]: str(exhb_data[j][1])})

        return render_template("platform.html", artists  = dict_art, exhibs = dict_exhb)

@app.route("/platform/<name><aid>", methods=["GET","POST"]) #print artist_portfolio
def artist_res(name,aid):
    if "flag" not in session:
        return render_template("home_page.html")

    user_flag = False
    if session["type"] == "user":
        user_flag = True

    if request.method == "GET":

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM photographer WHERE artist_id=%s"""
            cursor.execute(cmd, (aid,))
            curr_artist = cursor.fetchone()
            cursor.close()

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM portfolio WHERE artist_id=%s"""
            cursor.execute(cmd, (aid,))
            portfolio = cursor.fetchall()
            cursor.close()

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT * FROM photograph WHERE artist_id=%s"""
            cursor.execute(cmd, (aid,))
            photos_raw = cursor.fetchall()
            cursor.close()

            photos = list()
            for i in range(len(photos_raw)):
                photos.append(photos_raw[i][7])
                photos[i] = photos[i].tobytes()
                photos[i] = base64.b64encode(photos[i])  #b64 encoding
                photos[i] = photos[i].decode()

        return render_template("artist_res.html", artist = curr_artist, portfolio = portfolio, photos_raw =photos_raw, photos =photos, user_flag=user_flag)

    if request.method == "POST":
        photo_ids = request.form.getlist("user_fav_add")

        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cmd = """SELECT user_id FROM fav_list WHERE user_id=%s"""
            cursor.execute(cmd, (session["occupy_id"],))
            fav_id = cursor.fetchone()
            connection.commit()

            for photo_id in photo_ids:
                cmd_2 = '''INSERT INTO fav_content(photo_id,fav_list_id) VALUES(%s,%s)'''
                cursor.execute(cmd_2, (photo_id, fav_id))
                connection.commit()

            cursor.close()
        return redirect(url_for("user_page"))

@app.route("/platform/exhibitions/<eid>",methods=["GET","POST"])
def exhib_ser(eid):
    if request.method == "GET":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()

            cmd = """SELECT * FROM exhibition WHERE exhibition_id=%s"""
            cursor.execute(cmd,(eid,))
            the_exhibition = cursor.fetchone()
            connection.commit()

            cmd = """SELECT photo_id FROM exib_content WHERE exhibition_id=%s """
            cursor.execute(cmd,(eid,))
            the_exhibition_content =cursor.fetchall()
            connection.commit()

            photos_raw = list()
            for photo_id in the_exhibition_content:
                cmd = """SELECT * FROM photograph WHERE photo_id=%s"""
                cursor.execute(cmd, (photo_id[0],))
                photos_raw.append(cursor.fetchall())

            cursor.close()

        photos =list()
        for i in range(len(photos_raw)):
            photos.append(photos_raw[i][0][7])
            photos[i] = photos[i].tobytes()
            photos[i] = base64.b64encode(photos[i])  #b64 encoding
            photos[i] = photos[i].decode()



        return render_template("exhibition_pub.html", exhib_inf = the_exhibition, photos=photos, photos_raw =photos_raw)


if __name__ == "__main__":
    #db_init.init_database()
    app.run(host="127.0.0.1", port=8080, debug=True)#host="127.0.0.1"
