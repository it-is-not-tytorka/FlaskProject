from app import app, USERS, models  # TODO: maybe from models import User, Image etc?
from flask import request, Response
import http
import uuid
import json


@app.post("/user/<int:user_id>/image/create")
def create_image(user_id):
    data = request.get_json()
    folder_id = data["folder_id"]
    path = data["path"]
    title = data["title"]
    if models.Folder.is_valid_folder_id(user_id, folder_id):
        user = USERS[user_id]
        folder = user.folders[folder_id]
        if folder.is_able_to_edit_images():
            if not folder.is_marked_as_deleted():
                photo_id = f"photo-{uuid.uuid4()}"
                photo = models.Photo(photo_id, path, title)
                folder.create_image(photo)
                user.increase_image_count()
                response = {"folder_id": folder.id, "image_id": photo.id}
                return Response(
                    json.dumps(response),
                    status=http.HTTPStatus.OK,
                    mimetype="application/json",
                )
            return Response(
                "The folder was deleted by it's owner.",
                status=http.HTTPStatus.BAD_REQUEST,
            )
        return Response(
            "You don't have access to edit images.", status=http.HTTPStatus.BAD_REQUEST
        )  # TODO: what kind of status must be here
    return Response("Not valid folder id.", status=http.HTTPStatus.BAD_REQUEST)


@app.post("/user/<int:user_id>/folder/comment")
def add_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment = data["comment"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        if models.Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if not folder.is_marked_as_deleted():
                if models.Photo.is_valid_photo_id(folder, image_id):
                    image = folder.data["images"][image_id]
                    comment_id = f"comment-{uuid.uuid4()}"
                    image.add_comment(user, comment, comment_id)
                    user.increase_comment_count()
                    response = {
                        "folder_id": folder.id,
                        "image_id": image.id,
                        "comment_id": comment_id,
                    }
                    return Response(
                        json.dumps(response),
                        status=http.HTTPStatus.CREATED,
                        mimetype="application/json",
                    )
                return Response(
                    "The folder was deleted by it's owner.",
                    status=http.HTTPStatus.BAD_REQUEST,
                )
            return Response("Not valid image id.", status=http.HTTPStatus.BAD_REQUEST)
        return Response("Not valid folder id.", status=http.HTTPStatus.BAD_REQUEST)
    return Response("Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/folder/delete/image")
def delete_image(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        if models.Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if folder.is_able_to_edit_images():
                if models.Photo.is_valid_photo_id(folder, image_id):
                    folder.delete_image(image_id)
                    user.decrease_image_count()
                    return Response(
                        "Image was deleted successfully.", status=http.HTTPStatus.OK
                    )
                return Response(
                    "There's no such an image.", status=http.HTTPStatus.OK
                )  # TODO: find out what status code must be here
            return Response(
                "You don't have access to edit images.",
                status=http.HTTPStatus.BAD_REQUEST,
            )  # TODO: find out what status code must be here
        return Response("Not valid folder id.", status=http.HTTPStatus.BAD_REQUEST)
    return Response("Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/delete/comment")
def delete_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment_id = data["comment_id"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        if models.Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if folder.is_able_to_edit_images():
                if models.Photo.is_valid_photo_id(folder, image_id):
                    image = folder.data["images"][image_id]
                    if image.is_comment_present(comment_id):
                        image.delete_comment(comment_id)
                        user.decrease_comment_count()
                        return Response(
                            "The comment was deleted successfully.",
                            status=http.HTTPStatus.OK,
                        )
                    return Response(
                        "There's no such a comment.", status=http.HTTPStatus.BAD_REQUEST
                    )  # TODO: find out what status code must be here
                return Response(
                    "Not valid image id.", status=http.HTTPStatus.BAD_REQUEST
                )  # TODO: what kind of status
            return Response(
                "You don't have access to edit images.",
                status=http.HTTPStatus.BAD_REQUEST,
            )
        return Response("Not valid folder id.", status=http.HTTPStatus.BAD_REQUEST)
    return Response("Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)
