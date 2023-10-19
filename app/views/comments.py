from app import app, USERS
from app.models import User, Folder, Image, Comment, Editor
from flask import request, Response
from http import HTTPStatus
from datetime import date
import uuid
import json


@app.post("/user/<int:user_id>/comments/add")
def add_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment_text = data["comment_text"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if not folder.is_deleted:
                if Image.is_valid_image_id(folder, image_id):
                    if isinstance(comment_text, str): 
                        image = folder.images[image_id]
                        comment_id = f"comment-{uuid.uuid4()}"
                        comment_date = str(date.today())
                        comment = Comment(comment_text, comment_id, user_id, comment_date)
                        image.add_comment(comment)
                        Editor.increase_comment_count(user)
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
                    
                    response_data = {"error": "Comment text must be a string."}
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

            response_data = {"error": "The folder was deleted by it's owner"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
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


@app.get("/user/<int:user_id>/comments/delete")
def delete_comment(user_id):
    data = request.json
    folder_id = data["folder_id"]
    image_id = data["image_id"]
    comment_id = data["comment_id"]

    if User.is_valid_user_id(user_id):
        user = USERS[user_id]

        if Folder.is_valid_folder_id(user_id, folder_id):
            folder = user.folders[folder_id]
            if not folder.is_deleted:
                if Image.is_valid_image_id(folder, image_id):
                    image = folder.images[image_id]
                    comment = image.comments[comment_id]
                    user_owner_comment_id = comment.user_id

                    # Only owner of a folder, moderators and user who created the comment have access to delete the comment.
                    if (
                        folder.is_able_to_edit_images()
                        or user.id == user_owner_comment_id
                    ):
                        if Comment.is_valid_comment_id(image, comment_id):
                            image.delete_comment(comment_id)
                            Editor.recalculate_counts_comment(comment)
                            return Response(
                                status=HTTPStatus.NO_CONTENT,
                            )

                        response_data = {"error": "Invalid comment ID"}
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

                response_data = {"error": "Invalid image ID"}
                return Response(
                    response=json.dumps(response_data),
                    status=HTTPStatus.BAD_REQUEST,
                    content_type="application/json",
                )

            response_data = {"error": "The folder was deleted by it's owner"}
            return Response(
                response=json.dumps(response_data),
                status=HTTPStatus.BAD_REQUEST,
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
