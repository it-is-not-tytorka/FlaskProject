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
            "folders":self.folders_data_to_json()
        }
        return inf
    
    def folders_data_to_json(self):
        dict_of_folders = {}
        for folder_id in self.folders:
            folder = self.folders[folder_id]
            dict_of_folders[folder_id] = folder.photos_data_to_json()
        return dict_of_folders

    @staticmethod
    def is_valid_user_id(user_id : int):
        return isinstance(user_id, int) and user_id >= 0 and user_id < len(USERS)
    

class Folder:
    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name
        self.data = {
                "name": self.name,
                "images": {}
            }
    
    def create_folder(self, user: User):
        user.folders[self.id] = self

    @staticmethod
    def is_valid_folder_id(user_id, folder_id):
        return User.is_valid_user_id(user_id) and isinstance(folder_id, int) and folder_id >= 0 and folder_id < len(USERS[user_id].folders)

    def photos_data_to_json(self):
        data = self.data
        for key in self.data["images"]:
            photo = self.data["images"][key]
            data["images"][photo.id] = photo.data
        return data


class Photo:
    def __init__(self, id : int, path : str, title : str):
        self.id = id
        self.path = path
        self.title = title
        self.data = {
            "title": self.title,
            "path": self.path
        }
    
    @staticmethod
    def is_valid_photo_id(folder, photo_id):
        return folder.is_valid_folder_id and isinstance(photo_id, int) and photo_id >= 0 and photo_id < len(folder.data["images"])