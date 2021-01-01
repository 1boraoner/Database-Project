import numpy as np
import psycopg2 as dbapi2
import json

class user:

    def __init__(self,name, surname, contact,password):
        self.name = name
        self.surname = surname
        self.contact = contact
        self.password =  password
        #self.fav_list_id = np.random.randint(0,high = 10000,dtype=int)
        #self.fav_list_table = fav_list(self.fav_list_id)
        self.userid = 0

    def user_id_setter(self,id):
        self.userid = id


class fav_list:

    def __init__(self,id):
        self.id = id
        self.photo_ids = list()
        self.user_id = 0
    
    def __fill_photos__(self,ph_id):
        self.photo_ids.append(ph_id)

    def update_user_id(self,userid):
        self.user_id = userid


class artist:

    def __init__(self, name, surname, nationality, contact, style,password): #exhibiton_id
        self.artist_id = None
        self.name = name
        self.surname=surname
        self.nationality = nationality
        self.contact = contact
        self.style = style
        self.password = password
        self.portfolio_id = None
        self.exhibition_id = None

    def artist_id_setter(self,id):
        self.artist_id = id

    def set_portfolio(self,pid):
        self.portfolio_id

    def create_exhibiton(self,exid):
        self.exhibition_id = exid

    def conv_json(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def deserialize_json(self):
        return
class exhibiton:

    def __init__(self,id, artist_id, photo_num, photo_ids):
        self.exhibition_id = id
        self.artist_id = artist_id
        self.photo_num = 0
        self.photo_ids = list()

    def add_photo(self,photo_id):
        self.photo_ids.append(photo_id)

class photo:

    def __init__(self,category,location_info,tec_details,image_content, owner_name,owner_surname):
        self.category = category
        self.location_info = location_info    
        self.tec_details = tec_details
        self.image_content = image_content
        self.owner_name = owner_name
        self.owner_surname = owner_surname
        self.artist_id = None 
        self.photo_id = None 

    def set_ids(self,photo_id,artist_id):
        self.photo_id = photo_id
        self.artist_id= artist_id
    
    # def get_ids(self):
    #     dsn = """ user='bora' password='bora' host='localhost' port='5432' dbname='platform' """
    #     with dbapi2.connect(dsn) as connection:
    #
    #         cursor = connection.cursor()
    #         statement_artist = """ SELECT artist_id FROM photographer """
    #         cursor.execute(statement_artist)
    #         cursor.close()
    #
    #
