from app import app, USERS, models
from flask import request, Response
import json
import http


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
        user = models.User(first_name, last_name, phone, email, id)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "email": user.email,
            "id": user.id,
            "folders": user.folders
        }
        USERS.append(user)
        return Response(
            json.dumps(user_data),
            status=http.HTTPStatus.OK,
            mimetype="application/json",
        )

    else:
        return Response(status=http.HTTPStatus.BAD_REQUEST)


@app.get("/user/<int:user_id>")
def get_user_inf(user_id):
    if models.User.is_valid_user_id(user_id):
        response = USERS[user_id].get_inf()
        return Response(
            json.dumps(response), status=http.HTTPStatus.OK, mimetype="application/json"
        )
    return Response(status=http.HTTPStatus.BAD_REQUEST)


@app.post("/user/<int:user_id>/folder/create")
def create_folder(user_id):
    data = request.get_json()
    folder_name = data["folder_name"]
    if models.User.is_valid_user_id(user_id):
        user = USERS[user_id]
        folder_id = len(user.folders)
        folder = models.Folder(folder_id, folder_name)
        folder.create_folder(user)
        return Response(status=http.HTTPStatus.OK)
    return Response(http.HTTPStatus.BAD_REQUEST) 

@app.post("/user/<int:user_id>/folder/<int:folder_id>/append")
def append_photo_to_the_folder(user_id, folder_id):
    data = request.get_json()
    path = data["path"]
    title = data["title"]
    if models.Folder.is_valid_folder_id(user_id,folder_id):
        user = USERS[user_id] 
        folder = user.folders[folder_id]
        photo_id = len(folder.data["images"])
        photo = models.Photo(photo_id, path, title)
        folder.data["images"][photo_id] = photo
        return Response(status=http.HTTPStatus.OK)
    return Response(status=http.HTTPStatus.BAD_REQUEST)
