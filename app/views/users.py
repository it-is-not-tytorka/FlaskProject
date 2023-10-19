from app import app, USERS
from app.models import User
from flask import request, Response, url_for
import json
import matplotlib.pyplot as plt
from http import HTTPStatus


@app.post("/user/create")
def user_create():
    data = request.get_json()
    user_first_name = data["first_name"]
    user_last_name = data["last_name"]
    user_phone = data["phone"]
    user_email = data["email"]
    user_id = len(USERS)

    # check if phone number and email are valid
    if User.is_valid_phone(user_phone) and User.is_valid_email(user_email):
        # chack if user's params are unique
        if User.is_unique_params(data, "phone", "email"):
            user = User(
                user_first_name, user_last_name, user_phone, user_email, user_id
            )
            user_data = user.get_info()
            USERS.append(user)
            return Response(
                response=json.dumps(user_data),
                status=HTTPStatus.CREATED,
                content_type="application/json",
            )

        response_data = {
            "error": "Data duplication conflict",
        }
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.CONFLICT,
            content_type="application/json",
        )

    response_data = {
        "error": "Invalid user phone or email",
    }
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.BAD_REQUEST,
        content_type="application/json",
    )


@app.get("/user/<int:user_id>/info")
def get_user_info(user_id):
    if User.is_valid_user_id(user_id):
        user = USERS[user_id]
        response = user.get_info()
        return Response(
            response=json.dumps(response),
            status=HTTPStatus.OK,
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


@app.get("/user/<int:user_id>/stats")
def get_users_stats(user_id):
    if User.is_valid_user_id(user_id):
        user = USERS[user_id]
        fig, ax = plt.subplots()
        column_headers = ["folders", "images", "comments"]
        column_count = [user.folder_count, user.image_count, user.comment_count]
        ax.bar(column_headers, column_count)
        ax.set_title("User's statistic")
        ax.set_ylabel("Count of created objects")
        plt.savefig("app/static/user_stats.png")
        return Response(
            response=f"""<img src="{url_for("static",filename="user_stats.png")}">""",
            status=HTTPStatus.OK,
        )

    response_data = {
        "error": "User not found",
    }
    return Response(
        response=json.dumps(response_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )
