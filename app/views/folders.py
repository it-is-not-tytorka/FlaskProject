from app import app, USERS, models  # TODO: maybe from models import User, Image etc?
from flask import request, Response
import http
import uuid
import json


@app.post("/user/<int:user_id>/folder/create")
def create_folder(user_id):
    data = request.get_json()
    folder_name = data["folder_name"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        folder_id = f"folder-{uuid.uuid4()}"
        folder = models.Folder(folder_id, folder_name, user_id)
        folder.create_folder(user)
        user.increase_folder_count()
        response = {"folder_id": folder.id}
        return Response(
            json.dumps(response),
            status=http.HTTPStatus.CREATED,
            mimetype="application/json",
        )
    return Response(response="Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/folder/change")
def change_order_of_images(user_id):
    data = request.json
    folder_id = data["folder_id"]
    first_image_id = data["first_image_id"]
    second_image_id = data["second_image_id"]
    if models.Folder.is_valid_folder_id(user_id, folder_id):
        user = USERS[user_id]
        folder = user.folders[folder_id]
        if folder.is_able_to_edit_images():
            if models.Photo.is_valid_photo_id(
                folder, first_image_id
            ) and models.Photo.is_valid_photo_id(folder, second_image_id):
                swapped_dict = models.Editior.swap_two_elements_in_dict(
                    first_image_id, second_image_id, folder.data["images"]
                )
                if not swapped_dict is None:
                    folder.data["images"] = swapped_dict.copy()
                    return Response(status=http.HTTPStatus.OK)
                return Response(
                    "There's no such images.", status=http.HTTPStatus.OK
                )  # TODO: what kind of status must be here
            return Response("Not valid images id.", status=http.HTTPStatus.BAD_REQUEST)
        return Response(
            "You don't have access to edit images.", status=http.HTTPStatus.BAD_REQUEST
        )  # TODO: what kind of status must be here
    return Response(
        "Not valid user id or folder id.", status=http.HTTPStatus.BAD_REQUEST
    )


@app.get("/user/<int:user_id>/change/folder/order")
def change_order_of_folders(user_id):
    data = request.json
    first_folder_id = data["first_folder_id"]
    second_folder_id = data["second_folder_id"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        if models.Folder.is_valid_folder_id(
            user_id, first_folder_id
        ) and models.Folder.is_valid_folder_id(user_id, second_folder_id):
            old_dict = user.folders.copy()
            new_dict = models.Editior.swap_two_elements_in_dict(
                first_folder_id, second_folder_id, old_dict
            )
            if not new_dict is None:
                user.folders = new_dict.copy()
                return Response(
                    "Two folders swapped successfully.", status=http.HTTPStatus.OK
                )
            return Response(
                "There's no such folders.", status=http.HTTPStatus.OK
            )  # TODO: what kind of status must be here
        return Response("Not valid folders id.", http.HTTPStatus.BAD_REQUEST)
    return Response("Not valid user id.", http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/delete/folder")
def delete_folder(user_id):
    data = request.json
    folder_id = data["folder_id"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        if models.Folder.is_valid_folder_id(user_id, folder_id):
            user.delete_folder(folder_id)
            user.decrease_folder_count()
            return Response(
                "Folder was deleted successfully.", status=http.HTTPStatus.OK
            )
        # TODO: find out what status code must be here
        return Response("There's no such a folder.", status=http.HTTPStatus.OK)
    return Response("Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/folder/share")
def share_folder(user_id):
    data = request.json
    user_to_send_id = user_id
    user_to_receive_id = data["user_to_receive_id"]
    shared_folder_id = data["shared_folder_id"]
    access_edit = data[
        "access_edit"
    ]  # every user can comment but only with this user can edit everything: swap, delete, comment images
    if user_to_receive_id != user_to_send_id:
        if models.User.is_valid_user_id(
            user_to_send_id
        ) and models.User.is_valid_user_id(user_to_receive_id):
            if models.Folder.is_valid_folder_id(user_to_send_id, shared_folder_id):
                user_to_send = USERS[user_to_send_id]
                user_to_receive = USERS[user_to_receive_id]
                shared_folder = user_to_send.folders[shared_folder_id]
                if not isinstance(
                    shared_folder, models.SharedFolder
                ):  # only master of folder can share
                    new_folder = models.SharedFolder(
                        shared_folder, access_edit, user_to_receive_id
                    )
                    new_folder.create_folder(user_to_receive)
                    user_to_receive.increase_folder_count()
                    return Response(
                        "Folder was shared successfully.", http.HTTPStatus.OK
                    )
                return Response(
                    "You don't have rights to share folder", http.HTTPStatus.BAD_REQUEST
                )
            return Response("Not valid folder id.", http.HTTPStatus.BAD_REQUEST)
        return Response("Not valid users id.", http.HTTPStatus.BAD_REQUEST)
    return Response(
        "Users id are the same.", http.HTTPStatus.BAD_REQUEST
    )  # TODO: change statuses here too


@app.get("/user/<int:user_id>/folder/remove/access")
def remove_access_to_folder(user_id):
    data = request.json
    master_user_id = user_id
    user_to_remove_id = data["user_to_remove_id"]
    folder_id = data["folder_id"]
    if master_user_id != user_to_remove_id:
        if models.User.is_valid_user_id(
            master_user_id
        ) and models.User.is_valid_user_id(user_to_remove_id):
            master_user = USERS[master_user_id]
            user_to_remove = USERS[user_to_remove_id]
            if models.Folder.is_valid_folder_id(
                user_to_remove_id, folder_id
            ) and models.Folder.is_valid_folder_id(master_user_id, folder_id):
                folder = master_user.folders[folder_id]
                if not isinstance(
                    folder, models.SharedFolder
                ):  # only master of folder can remove folder access
                    user_to_remove.delete_folder(folder_id)
                    user_to_remove.decrease_folder_count()
                    return Response(
                        "Folder access was removed successfully.", http.HTTPStatus.OK
                    )
                return Response("Wrong master id.", http.HTTPStatus.BAD_REQUEST)
            return Response("Not valid folder id.", http.HTTPStatus.BAD_REQUEST)
        return Response("Not valid users id.", http.HTTPStatus.BAD_REQUEST)
    return Response(
        "Users id are the same.", http.HTTPStatus.BAD_REQUEST
    )  # TODO: find out what statuses must be here
