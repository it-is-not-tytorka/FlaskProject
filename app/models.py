import re
import datetime
from app import USERS

# TODO: write docs for classes


class User:
    def __init__(self, first_name, last_name, phone, email, id):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.id = id
        self.folders = {}
        self.folder_count = 0
        self.image_count = 0
        self.comment_count = 0

    @staticmethod
    def is_valid_phone(phone_numb):
        temp = re.compile(r"^\+?(7)?(0|7)\d{9,13}$")
        return not temp.match(phone_numb) is None

    @staticmethod
    def is_valid_email(email):
        return (
            len(email) > 7
            and re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", email)
            != None
        )

    def get_inf(self):
        inf = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "id": self.id,
            "folder_count": self.folder_count,
            "image_count": self.image_count,
            "comment_count": self.comment_count,
            "folders": self.folders_data_to_json(),
        }
        return inf

    def folders_data_to_json(self):
        dict_of_folders = {}
        for folder_id in self.folders:
            folder = self.folders[folder_id]
            if not folder.is_marked_as_deleted():
                dict_of_folders[folder_id] = {}
                dict_of_folders[folder_id]["name"] = folder.data["name"]
                dict_of_folders[folder_id]["folder_users"] = folder.data["folder_users"]
                dict_of_folders[folder_id]["images"] = folder.photos_data_to_json()
            else:
                dict_of_folders[folder_id] = "The folder was deleted by it's owner."
        return dict_of_folders

    @staticmethod
    def is_valid_user_id(user_id: int):
        return isinstance(user_id, int) and user_id >= 0 and user_id < len(USERS)

    @staticmethod
    def share_folder(user_to_receive, folder):
        user_to_receive.folders[folder.id] = folder

    def delete_folder(self, folder_id):
        folder = self.folders[folder_id]
        folder.is_deleted = True
        del folder.data["folder_users"][self.id]
        del self.folders[folder_id]

    @staticmethod
    def is_unique_params(data, *args):
        try:
            return all(
                data[arg] != getattr(user, arg) for arg in args for user in USERS
            )
        except AttributeError:
            return False

    def increase_folder_count(self):
        self.folder_count += 1

    def decrease_folder_count(self):
        self.folder_count -= 1

    def increase_image_count(self):
        self.image_count += 1

    def decrease_image_count(self):
        self.image_count -= 1

    def increase_comment_count(self):
        self.comment_count += 1

    def decrease_comment_count(self):
        self.comment_count -= 1


class Folder:
    def __init__(self, id: str, name: str, owner_id: int):
        self.name = name
        self.id = id
        self.access_edit = True
        self.is_deleted = False
        self.data = {
            "name": self.name,
            "folder_users": {owner_id: "owner"},
            "images": {},
        }

    def create_folder(self, user: User):
        user.folders[self.id] = self

    @staticmethod
    def is_valid_folder_id(user_id, folder_id):
        return (
            User.is_valid_user_id(user_id)
            and isinstance(folder_id, str)
            and folder_id in USERS[user_id].folders.keys()
        )

    def photos_data_to_json(self):
        dict_of_images = {}
        for key in self.data["images"]:
            photo = self.data["images"][key]
            dict_of_images[photo.id] = photo.data
        return dict_of_images

    def create_image(self, image):
        self.data["images"][image.id] = image

    def delete_image(self, image_id):
        del self.data["images"][image_id]

    def is_able_to_edit_images(self):
        return self.access_edit

    def is_marked_as_deleted(self):
        return self.is_deleted


class SharedFolder(Folder):
    def __init__(self, folder: Folder, access_edit: bool, user_id: int):
        self.id = folder.id
        self.name = folder.name
        self.access_edit = access_edit
        self.data = folder.data
        self.main_folder = folder
        if access_edit:
            folder.data["folder_users"][user_id] = "moderator"
        else:
            folder.data["folder_users"][user_id] = "reader"

    def is_marked_as_deleted(self):
        return self.main_folder.is_deleted


class Photo:
    def __init__(self, id: str, path: str, title: str):
        self.id = id
        self.path = path
        self.title = title
        self.comments = []
        self.data = {"title": self.title, "path": self.path, "comments": self.comments}

    @staticmethod
    def is_valid_photo_id(folder: Folder, photo_id: int):
        return isinstance(photo_id, str) and photo_id in folder.data["images"]

    def add_comment(self, user: User, comment: str, comment_id: str):
        today_date = str(datetime.date.today())
        data = {
            "user_id": user.id,
            "comment": comment,
            "date": today_date,
            "comment_id": comment_id,
        }
        self.comments.append(data)

    def is_comment_present(self, comment_id: str) -> bool:
        return any(comment["comment_id"] == comment_id for comment in self.comments)

    def delete_comment(self, comment_id: str):
        for i in range(len(self.comments)):
            if self.comments[i]["comment_id"] == comment_id:
                self.comments.pop(i)


class Editior:
    @staticmethod
    def swap_two_elements_in_dict(
        first_el_id: int, second_el_id: int, old_dict: dict
    ) -> dict:
        new_dict = {}
        try:
            data_first_el = old_dict[first_el_id]
            data_second_el = old_dict[second_el_id]
            for key in old_dict:
                if key == first_el_id:
                    new_dict[second_el_id] = data_second_el
                elif key == second_el_id:
                    new_dict[first_el_id] = data_first_el
                else:
                    new_dict[key] = old_dict[key]
            return new_dict
        except IndexError:
            return None
