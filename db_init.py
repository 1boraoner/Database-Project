import os
import sys
import psycopg2 as dbapi2

INIT_DB = [
    """CREATE TABLE IF NOT EXISTS photographer(
        artist_id INT GENERATED BY DEFAULT AS IDENTITY NOT NULL,
        artist_name VARCHAR(50) NOT NULL,
        artist_surname VARCHAR(50) NULL,
        nationality VARCHAR(50) NULL,
        contact_add VARCHAR(100) NULL,
        artist_style   VARCHAR(50) NULL,
        password VARCHAR(50) NOT NULL,
        PRIMARY KEY(artist_id)
    )""",

    """CREATE TABLE IF NOT EXISTS exhibition(
        exhibition_id INT NOT NULL,
        date_inf VARCHAR(50) NULL,
        duration INT NULL,
        visitor_count INT NULL,
        PRIMARY KEY(exhibition_id)
    )""",

    """CREATE TABLE IF NOT EXISTS portfolio(
        portfolio_id SERIAL,
        artist_id INT NOT NULL,
        photo_num INT DEFAULT 0,
        create_date DATE NOT NULL DEFAULT CURRENT_DATE,
        summary VARCHAR(200) NULL,
        FOREIGN KEY(artist_id) REFERENCES photographer(artist_id),
        PRIMARY KEY(portfolio_id)
    )""",

    """CREATE TABLE IF NOT EXISTS photograph(
        photo_id SERIAL,
        artist_id INT NOT NULL,
        portfolio_id INT NOT NULL,
        category VARCHAR(50) NULL,
        location_info VARCHAR(150) NULL, 
        tec_details VARCHAR(200) NULL,
        image_cont BYTEA NOT NULL,
        FOREIGN KEY(artist_id) REFERENCES photographer(artist_id),
        FOREIGN KEY(portfolio_id) REFERENCES portfolio(portfolio_id),
        PRIMARY KEY(photo_id)
    )""",

    """CREATE TABLE IF NOT EXISTS users(
        user_id INT GENERATED BY DEFAULT AS IDENTITY NOT NULL,
        user_name VARCHAR(50) NOT NULL,
        surname VARCHAR(50) NOT NULL,
        contact VARCHAR(50) NULL,
        password INT NOT NULL,
        PRIMARY KEY(user_id)
    )""",

    """CREATE TABLE IF NOT EXISTS fav_list(
        fav_list_id SERIAL NOT NULL,
        user_id INT NOT NULL,
        photo_ids INT NULL,
        PRIMARY KEY(fav_list_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)  
    )"""
]
url = """ user='postgres' password='bora' host='localhost' port='5432' dbname='postgres' """
DB_HOST ="localhost"
DB_NAME ="postgres"
DB_USER ="postgers"
DB_PASS ="bora"


def init_database():
    print("CONNECTING TO DB")
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for create_tables in INIT_DB:
            cursor.execute(create_tables)
            connection.commit()
        cursor.close()


# if __name__ == "__main__":
#     print("DATABASE CREATED")
#     init_database()

