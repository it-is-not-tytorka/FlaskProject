from app import app, USERS
from app.models import User, Folder, SharedFolder, Photo, Editor
from flask import request, Response
from http import HTTPStatus
import uuid
import json


@app.post("/user/<int:user_id>/folder/create")
def create_folder(user_id):
    data = request.get_json()
    folder_name = data["folder_name"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]
        folder_id = f"folder-{uuid.uuid4()}"
        folder = Folder(folder_id, folder_name, user_id)
        folder.create_folder(user)
        user.increase_folder_count()
        response = {"folder_id": folder.id}
        return Response(
            response=json.dumps(response),
            status=HTTPStatus.CREATED,
            mimetype="application/json",
        )

    response_data = {
        "error": "User not found",
    }
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/folder/change/order")
def change_order_of_images(user_id):
    data = request.json
    folder_id = data["folder_id"]
    first_image_id = data["first_image_id"]
    second_image_id = data["second_image_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if folder.is_able_to_edit_images():
                if Photo.is_valid_photo_id(
                    folder, first_image_id
                ) and Photo.is_valid_photo_id(folder, second_image_id):
                    swapped_dict = Editor.swap_two_elements_in_dict(
                        first_image_id, second_image_id, folder.data["images"]
                    )

                    if not swapped_dict is None:
                        folder.data["images"] = swapped_dict.copy()
                        return Response(status=HTTPStatus.NO_CONTENT)

                    response_data = {"error": "Images not found"}
                    return Response(
                        response=json.dumps(response_data),
                        status=HTTPStatus.BAD_REQUEST,
                        content_type="application/json",
                    )

                response_data = {"error": "Invalid images ID"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.BAD_REQUEST,
                    content_type="application/json",
                )

            response_data = {"error": "Permission denied"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.FORBIDDEN,
                content_type="application/json",
            )

        response_data = {"error": "Invalid folder id"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="application/json",
        )

    response_data = {"error": "User not found"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/change/folder/order")
def change_order_of_folders(user_id):
    data = request.json
    first_folder_id = data["first_folder_id"]
    second_folder_id = data["second_folder_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(
            user_id, first_folder_id
        ) and Folder.is_valid_folder_id(user_id, second_folder_id):
            old_dict = user.folders.copy()
            new_dict = Editor.swap_two_elements_in_dict(
                first_folder_id, second_folder_id, old_dict
            )

            if not new_dict is None:
                user.folders = new_dict.copy()
                return Response(status=HTTPStatus.NO_CONTENT)

            response_data = {"error": "Folders not found"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
                content_type="application/json",
            )

        response_data = {"error": "Invalid folders id"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="applicatin/json",
        )

    response_data = {"error": "User not found"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/delete/folder")
def delete_folder(user_id):
    data = request.json
    folder_id = data["folder_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            user.delete_folder(folder_id)
            user.decrease_folder_count()
            return Response(status=HTTPStatus.NO_CONTENT)

        response_data = {"error": "Invalid folder id"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="application/json",
        )

    response_data = {"error": "User not found"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/folder/share")
def share_folder(user_id):
    data = request.json
    user_to_send_id = user_id
    user_to_receive_id = data["user_to_receive_id"]
    shared_folder_id = data["shared_folder_id"]
    # every user can comment but only with access_edit == True user can edit everything: swap, delete, comment images
    access_edit = data["access_edit"]

    if user_to_receive_id != user_to_send_id:
        if User.is_valid_user_id(user_to_send_id):
            if User.is_valid_user_id(user_to_receive_id):
                if Folder.is_valid_folder_id(user_to_send_id, shared_folder_id):
                    user_to_send = USERS[user_to_send_id]
                    user_to_receive = USERS[user_to_receive_id]
                    shared_folder = user_to_send.folders[shared_folder_id]

                    # only folder owner can share
                    if not isinstance(shared_folder, SharedFolder):
                        new_folder = SharedFolder(
                            shared_folder, access_edit, user_to_receive_id
                        )
                        new_folder.create_folder(user_to_receive)
                        return Response(status=HTTPStatus.NO_CONTENT)

                    response_data = {"error": "Permission denied"}
                    return Response(
                        response=json.dumps(response_data),
                        status=HTTPStatus.FORBIDDEN,
                        content_type="application/json",
                    )

                response_data = {"error": "Invalid folder id"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.BAD_REQUEST,
                    content_type="application/json",
                )

            response_data = {"error": "Invalid user id"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
                content_type="application/json",
            )

        response_data = {"error": "User not found"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.NOT_FOUND,
            content_type="application/json",
        )

    response_data = {"error": "Users id are the same"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.BAD_REQUEST,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/folder/remove/access")
def remove_access_to_folder(user_id):
    data = request.json
    master_user_id = user_id
    user_to_remove_id = data["user_to_remove_id"]
    folder_id = data["folder_id"]

    if master_user_id != user_to_remove_id:
        if User.is_valid_user_id(master_user_id) and User.is_valid_user_id(
            user_to_remove_id
        ):
            master_user = USERS[master_user_id]
            user_to_remove = USERS[user_to_remove_id]

            if Folder.is_valid_folder_id(
                user_to_remove_id, folder_id
            ) and Folder.is_valid_folder_id(master_user_id, folder_id):
                folder = master_user.folders[folder_id]

                if not isinstance(
                    folder, SharedFolder
                ):  # only folder owner can remove folder access
                    user_to_remove.delete_folder(folder_id)
                    user_to_remove.decrease_folder_count()
                    return Response(HTTPStatus.NO_CONTENT)

                response_data = {"error": "Permission denied"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.FORBIDDEN,
                    content_type="application/json",
                )

            response_data = {"error": "Invalid folder id"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
                content_type="application/json",
            )

        response_data = {"error": "Invalid users id"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="application/json",
        )

    response_data = {"error": "Users id are the same"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.BAD_REQUEST,
        content_type="application/json",
    )
