from app import app, USERS
from app.models import User, Folder, Image, Editor
from flask import request, Response
from http import HTTPStatus
import uuid
import json


@app.post("/user/<int:user_id>/images/create")
def create_image(user_id):
    data = request.get_json()
    folder_id = data["folder_id"]
    path = data["path"]
    title = data["title"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if not folder.is_deleted:
                if folder.is_able_to_edit_images():
                    if isinstance(title, str):
                        if isinstance(path, str):
                            image_id = f"image-{uuid.uuid4()}"
                            image = Image(image_id, path, title, user.id)
                            folder.create_image(image)
                            Editor.increase_image_count(user)
                            response = {"folder_id": folder.id, "image_id": image.id}
                            return Response(
                                response=json.dumps(response),
                                status=HTTPStatus.CREATED,
                                content_type="application/json",
                            )

                        response_data = {"error": "Image path must be a string."}
                        return Response(
                            response=json.dumps(response_data),
                            status=HTTPStatus.BAD_REQUEST,
                            content_type="application/json",
                        )

                    response_data = {"error": "Image title must be a string"}
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

            response_data = {"error": "The folder was deleted by it's owner."}
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

    response_data = {"error": "User not found"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/images/swap")
def swap_images(user_id):
    data = request.json
    folder_id = data["folder_id"]
    first_image_id = data["first_image_id"]
    second_image_id = data["second_image_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if not folder.is_deleted:
                # Every user can swap images in folder because it doesn't change order for other users who
                # have access to this folder.
                if Image.is_valid_image_id(
                    folder, first_image_id
                ) and Image.is_valid_image_id(folder, second_image_id):
                    swapped_dict = Editor.swap_elements(
                        first_image_id, second_image_id, folder.images
                    )

                    if swapped_dict is not None:
                        folder.images = swapped_dict.copy()
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

            response_data = {"error": "The folder was deleted by it's owner."}
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

    response_data = {"error": "User not found"}
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )


@app.delete("/user/<int:user_id>/images/delete")
def delete_image(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]

            if folder.is_able_to_edit_images():
                if not folder.is_deleted:
                    if Image.is_valid_image_id(folder, image_id):
                        image = folder.images[image_id]
                        Editor.recalculate_counts_image(image)
                        folder.delete_image(image)

                        return Response(status=HTTPStatus.NO_CONTENT)

                    response_data = {"error": "Invalid image ID"}
                    return Response(
                        response=json.dumps(response_data),
                        status=HTTPStatus.BAD_REQUEST,
                        content_type="application/json",
                    )

                response_data = {"error": "The folder was delete by it's owner"}
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
