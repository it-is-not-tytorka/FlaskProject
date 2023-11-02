import re
from app import USERS


class User:
    def __init__(
        self, first_name: str, last_name: str, phone: str, email: str, id: int
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.id = id
        self.folders = {}
        self.image_count = 0
        self.comment_count = 0
        self.status = "created"

    def get_info(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "id": self.id,
            "folder_count": self.folder_count,
            "image_count": self.image_count,
            "comment_count": self.comment_count,
            "folders": [folder.to_dict() for folder in self.folders.values()],
        }

    @property
    def folder_count(self):
        return len(
            list(filter(lambda folder: not folder.is_deleted, self.folders.values()))
        )

    @staticmethod
    def is_valid_phone(phone_numb: str) -> bool:
        temp = re.compile(r"^\+?(7)?(0|7)\d{9,13}$")
        return not temp.match(phone_numb) is None

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return (
            len(email) > 7
            and re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", email)
            is not None
        )

    @staticmethod
    def is_unique_params(data: dict, *args) -> bool:
        try:
            is_unique = True
            for user in USERS.values():
                if user.status != "deleted":
                    if any(getattr(user, arg) == data[arg] for arg in args):
                        is_unique = False
            return is_unique
        except AttributeError:
            return False

    @staticmethod
    def is_valid_user_id(user_id: int) -> bool:
        return isinstance(user_id, int) and user_id in USERS and USERS[user_id].status != "deleted"

    @staticmethod
    def share_folder(user_to_receive, folder) -> None:
        user_to_receive.folders[folder.id] = folder

    def delete_folder(self, folder_id) -> None:
        folder = self.folders[folder_id]
        if not isinstance(folder, SharedFolder):
            folder.is_deleted = True
        del folder.users[self.id]
        del self.folders[folder_id]


class Folder:
    def __init__(self, id: str, name: str, owner_id: int) -> None:
        self.name = name
        self.id = id
        self.access_edit = True
        self.is_deleted = False
        self.images = {}
        self.users = {owner_id: "owner"}

    def create_folder(self, user: User) -> None:
        user.folders[self.id] = self

    @staticmethod
    def is_valid_folder_id(user_id: int, folder_id: str) -> bool:
        return (
            User.is_valid_user_id(user_id)
            and isinstance(folder_id, str)
            and folder_id in USERS[user_id].folders.keys()
        )

    def to_dict(self) -> dict:
        if not self.is_deleted:
            return {
                "folder_id": self.id,
                "name": self.name,
                "folder_users": self.users,
                "images": [self.images[image_id].to_dict() for image_id in self.images],
            }
        return {"folder_id": self.id, "error": "The folder was deleted by it's owner."}

    def create_image(self, image) -> None:
        self.images[image.id] = image

    def delete_image(self, image) -> None:
        del self.images[image.id]

    def is_able_to_edit_images(self) -> bool:
        return self.access_edit


class SharedFolder(Folder):
    def __init__(self, folder: Folder, access_edit: bool, user_id: int) -> None:
        self.id = folder.id
        self.name = folder.name
        self.access_edit = access_edit
        self.users = folder.users
        self.images = folder.images
        self.main_folder = folder
        if access_edit:
            folder.users[user_id] = "moderator"
        else:
            folder.users[user_id] = "reader"

    @property
    def is_deleted(self):
        return self.main_folder.is_deleted
    
    def create_image(self, image) -> None:
        self.main_folder.images[image.id] = image


class Image:
    def __init__(self, id: str, path: str, title: str, user_id: int) -> None:
        self.id = id
        self.path = path
        self.title = title
        self.comments = {}
        self.user_id = user_id

    @staticmethod
    def is_valid_image_id(folder: Folder, image_id: int) -> bool:
        return isinstance(image_id, str) and image_id in folder.images

    def add_comment(self, comment) -> None:
        self.comments[comment.id] = comment

    def delete_comment(self, comment_id: str) -> None:
        del self.comments[comment_id]

    def to_dict(self) -> dict:
        return {
            "image_id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "path": self.path,
            "comments": [
                self.comments[comment_id].to_dict() for comment_id in self.comments
            ],
        }


class Comment:
    def __init__(self, text: str, id: str, user_id: int, date: str) -> None:
        self.text = text
        self.id = id
        self.user_id = user_id
        self.date = date

    @staticmethod
    def is_valid_comment_id(image: Image, comment_id: str) -> bool:
        return isinstance(comment_id, str) and comment_id in image.comments

    def to_dict(self) -> dict:
        return {
            "comment_id": self.id,
            "comment_text": self.text,
            "user_id": self.user_id,
            "date": self.date,
        }


class Editor:
    @staticmethod
    def swap_elements(first_el_id: int, second_el_id: int, old_dict: dict) -> dict:
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

    @staticmethod
    def recalculate_counts_folder(folder: Folder) -> None:
        for image in folder.images.values():
            Editor.recalculate_counts_image(image)

    @staticmethod
    def recalculate_counts_image(image: Image) -> None:
        user_id = image.user_id
        if User.is_valid_user_id(user_id):
            user = USERS[user_id]
            Editor.decrease_image_count(user)
        for comment in image.comments.values():
            Editor.recalculate_counts_comment(comment)

    @staticmethod
    def recalculate_counts_comment(comment: Comment) -> None:
        user_id = comment.user_id
        if User.is_valid_user_id(user_id):
            user = USERS[user_id]
            Editor.decrease_comment_count(user)

    @staticmethod
    def increase_image_count(user) -> None:
        user.image_count += 1

    @staticmethod
    def decrease_image_count(user) -> None:
        user.image_count -= 1

    @staticmethod
    def increase_comment_count(user) -> None:
        user.comment_count += 1

    @staticmethod
    def decrease_comment_count(user) -> None:
        user.comment_count -= 1
