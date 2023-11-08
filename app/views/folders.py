from app import app, USERS
from app.models import User, Folder, SharedFolder, Editor
from flask import request, Response
from http import HTTPStatus
import uuid
import json


@app.post("/user/<int:user_id>/folders/create")
def create_folder(user_id):
    data = request.get_json()
    folder_name = data["folder_name"]

    if User.is_valid_user_id(user_id):
        if isinstance(folder_name, str):
            user = USERS[user_id]
            folder_id = f"folder-{uuid.uuid4()}"
            folder = Folder(folder_id, folder_name, user_id)
            folder.create_folder(user)
            response = {"folder_id": folder.id}
            return Response(
                response=json.dumps(response),
                status=HTTPStatus.CREATED,
                mimetype="application/json",
            )

        response_data = {
            "error": "Folder name must be a string.",
        }
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="application/json",
        )

    response_data = {
        "error": "User not found",
    }
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/folders/swap")
def swap_folders(user_id):
    data = request.json
    first_folder_id = data["first_folder_id"]
    second_folder_id = data["second_folder_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(
            user_id, first_folder_id
        ) and Folder.is_valid_folder_id(user_id, second_folder_id):
            old_dict = user.folders.copy()
            new_dict = Editor.swap_elements(first_folder_id, second_folder_id, old_dict)

            # if there wasn't a mistake in Editor.swap_elements()
            if not new_dict is None:
                user.folders = new_dict.copy()
                return Response(status=HTTPStatus.NO_CONTENT)

            response_data = {"error": "Folders not found"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
                content_type="application/json",
            )

        response_data = {"error": "Invalid folders ID"}
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


@app.delete("/user/<int:user_id>/folders/delete") # todo: method was changed to DELETE. redo README
def delete_folder(user_id):
    data = request.json
    folder_id = data["folder_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            # If user is not an owner of a folder
            # all images and comments remain in owner's folder
            # after user deleted a folder.
            # Because of this we don't call Editor.recalculate_counts_folder() to decrease images and comments counters.
            # This operator run only if folder's class is Folder and not SharedFolder (user is an owner of a folder)
            if not isinstance(folder, SharedFolder):
                Editor.recalculate_counts_folder(folder)
            user.delete_folder(folder_id)
            return Response(status=HTTPStatus.NO_CONTENT)

        response_data = {"error": "Invalid folder ID"}
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


@app.get("/user/<int:user_id>/folders/share")
def share_folder(user_id):
    data = request.json
    user_to_send_id = user_id
    user_to_receive_id = data["user_to_receive_id"]
    shared_folder_id = data["shared_folder_id"]
    # Every user can comment and watch images.
    # But only users with access_edit == True have more options.
    access_edit = data["access_edit"]

    if user_to_receive_id != user_to_send_id:
        if User.is_valid_user_id(user_to_send_id):
            if User.is_valid_user_id(user_to_receive_id):
                user_to_send = USERS[user_to_send_id]
                user_to_receive = USERS[user_to_receive_id]

                if Folder.is_valid_folder_id(user_to_send_id, shared_folder_id):
                    shared_folder = user_to_send.folders[shared_folder_id]
                    # Only owner of a folder can share folder.
                    # And this operator check if a user is an owner.
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

                response_data = {"error": "Invalid folder ID"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.BAD_REQUEST,
                    content_type="application/json",
                )

            response_data = {"error": "Invalid user ID"}
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

    response_data = {"error": "Users ID are the same"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.BAD_REQUEST,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/folders/unshare")
def unshare_folder(user_id):
    data = request.json
    user_owner_id = user_id
    user_to_unshare_id = data["user_to_unshare_id"]
    folder_id = data["folder_id"]

    if user_owner_id != user_to_unshare_id:
        if User.is_valid_user_id(user_owner_id) and User.is_valid_user_id(
            user_to_unshare_id
        ):
            user_owner = USERS[user_owner_id]
            user_to_remove = USERS[user_to_unshare_id]

            if Folder.is_valid_folder_id(
                user_to_unshare_id, folder_id
            ) and Folder.is_valid_folder_id(user_owner_id, folder_id):
                folder = user_owner.folders[folder_id]

                # Only owner of a folder can remove folder access.
                if not isinstance(folder, SharedFolder):
                    user_to_remove.delete_folder(folder_id)
                    return Response(status=HTTPStatus.NO_CONTENT)

                response_data = {"error": "Permission denied"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.FORBIDDEN,
                    content_type="application/json",
                )

            response_data = {"error": "Invalid folder ID"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
                content_type="application/json",
            )

        response_data = {"error": "Invalid users ID"}
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.BAD_REQUEST,
            content_type="application/json",
        )

    response_data = {"error": "Users ID are the same"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.BAD_REQUEST,
        content_type="application/json",
    )
