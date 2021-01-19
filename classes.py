import psycopg2 as dbapi2

class user:

    def __init__(self,name, surname, contact,password):
        self.name = name
        self.surname = surname
        self.contact = contact
        self.password =  password
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


class exhibiton:

    def __init__(self,id=0, name=0, ename=0,date=0,):
        self.exhibition_id = id
        self.artist_name = name
        self.exhb_name = ename
        self.date = date


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
    
