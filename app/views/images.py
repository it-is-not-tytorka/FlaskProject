from app import app, USERS
from app.models import User, Folder, Photo
from flask import request, Response
from http import HTTPStatus
import uuid
import json


@app.post("/user/<int:user_id>/image/create")
def create_image(user_id):
    data = request.get_json()
    folder_id = data["folder_id"]
    path = data["path"]
    title = data["title"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if folder.is_able_to_edit_images():
                if not folder.is_marked_as_deleted():
                    photo_id = f"photo-{uuid.uuid4()}"
                    photo = Photo(photo_id, path, title, user.id)
                    folder.create_image(photo)
                    user.increase_image_count()
                    response = {"folder_id": folder.id, "image_id": photo.id}
                    return Response(
                        response=json.dumps(response),
                        status=HTTPStatus.CREATED,
                        content_type="application/json",
                    )

                response_data = {"error": "The folder was deleted by it's owner"}
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


@app.post("/user/<int:user_id>/folder/comment")
def add_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment = data["comment"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if not folder.is_marked_as_deleted():
                if Photo.is_valid_photo_id(folder, image_id):
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
                        response=json.dumps(response),
                        status=HTTPStatus.CREATED,
                        content_type="application/json",
                    )

                response_data = {"error": "Invalid image id"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.BAD_REQUEST,
                    content_type="application/json",
                )

            response_data = {"error": "The folder was deleted by it's owner"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.GONE,
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


@app.get("/user/<int:user_id>/folder/delete/image")
def delete_image(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if folder.is_able_to_edit_images():
                if Photo.is_valid_photo_id(folder, image_id):
                    image = folder.data["images"][image_id]
                    user_owner_image_id = image.data["user_id"]

                    if User.is_valid_user_id(user_owner_image_id):
                        user_owner_image = USERS[user_owner_image_id]
                        user_owner_image.decrease_image_count()

                    folder.delete_image(image_id)
                    return Response(status=HTTPStatus.NO_CONTENT)

                response_data = {"error": "Invalid image id"}
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


@app.get("/user/<int:user_id>/delete/comment")
def delete_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment_id = data["comment_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if folder.is_able_to_edit_images():
                if Photo.is_valid_photo_id(folder, image_id):
                    image = folder.data["images"][image_id]
                    comment_data = image.data["comments"][comment_id]
                    user_owner_comment_id = comment_data["user_id"]

                    if image.is_valid_comment_id(comment_id):
                        image.delete_comment(comment_id)

                        if User.is_valid_user_id(user_owner_comment_id):
                            user_owner_comment = USERS[user_owner_comment_id]
                            user_owner_comment.decrease_comment_count()

                        return Response(
                            status=HTTPStatus.NO_CONTENT,
                        )

                    response_data = {"error": "Invalid comment id"}
                    return Response(
                        response=json.dumps(response_data),
                        status=HTTPStatus.BAD_REQUEST,
                        content_type="application/json",
                    )

                response_data = {"error": "Invalid image id"}
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
