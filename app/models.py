import re
from app import USERS

class User:
    def __init__(self, first_name, last_name, phone, email, id):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.id = id
        self.folders = {}

    @staticmethod
    def is_valid_phone(phone_numb):
        temp = re.compile(r'^\+?(7)?(0|7)\d{9,13}$')
        return not temp.match(phone_numb) is None
    
    @staticmethod
    def is_valid_email(email):
        return len(email) > 7 and re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email) != None
    
    def get_inf(self):
        inf = {
            "first_name":self.first_name,
            "last_name":self.last_name,
            "phone":self.phone,
            "email":self.email,
            "id":self.id,
            "folders":self.folders
        }
        return inf
    
    @staticmethod
    def check_user(user_id : int):
        return isinstance(user_id, int) and user_id >= 0 and user_id < len(USERS)
    @staticmethod
    def check_folder(user, folder_id : int):
        return isinstance(folder_id, int) and folder_id >= 0 and folder_id < len(user.folders)
    

class Folder:
    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name
        self.data = {
                "name": self.name,
                "images": {}
            }
    
    def create_folder(self, user: User):
        user.folders[self.id] = self.data

class Photo:
    def __init__(self, id : int, path : str, comment : str = ''):
        self.id = id
        self.path = path
        self.comment = comment
        self.data = {
            "path": self.path,
            "comment": self.comment
        }