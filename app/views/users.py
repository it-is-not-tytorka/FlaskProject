from app import app, USERS, models  # TODO: maybe from models import User, Image etc?
from flask import request, Response, url_for
import json
import matplotlib.pyplot as plt
import http  # TODO: maybe from http import HTTPStatus


@app.post("/user/create")
def user_create():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    phone = data["phone"]
    email = data["email"]
    id = len(USERS)
    # check if phone number and email are valid
    if models.User.is_valid_phone(phone_numb=phone) and models.User.is_valid_email(
        email=email
    ):
        # TODO: switch on: if models.User.is_unique_params(data, "first_name","last_name","phone","email"):
        user = models.User(first_name, last_name, phone, email, id)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "email": user.email,
            "id": user.id,
            "folders": user.folders,
        }
        USERS.append(user)
        return Response(
            json.dumps(user_data),
            status=http.HTTPStatus.CREATED,
            mimetype="application/json",
        )
    # TODO: switch on: return Response("Not unique user's data.", status=http.HTTPStatus.BAD_REQUEST)
    return Response(
        response="Not valid phone number or email.", status=http.HTTPStatus.BAD_REQUEST
    )


@app.get("/user/<int:user_id>")
def get_user_inf(user_id):
    if models.User.is_valid_user_id(user_id):
        response = USERS[user_id].get_inf()
        return Response(
            json.dumps(response), status=http.HTTPStatus.OK, mimetype="application/json"
        )
    return Response(response="Not valid user id.", status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>/stats")
def get_users_stats(user_id):
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        fig, ax = plt.subplots()
        column_headers = ["folders", "images", "comments"]
        column_count = [user.folder_count, user.image_count, user.comment_count]
        ax.bar(column_headers, column_count)
        ax.set_title("User's statistic")
        ax.set_ylabel("Count of created objects")
        plt.savefig("app/static/user_stats.png")
        return Response(
            f"""<img src="{url_for("static",filename="user_stats.png")}">""",
            status=http.HTTPStatus.OK,
        )
    return Response(
        "Not valid user id.", status=http.HTTPStatus.BAD_REQUEST, mimetype="text/html"
    )
