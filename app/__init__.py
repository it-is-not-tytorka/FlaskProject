from flask import Flask

app = Flask(__name__)

USERS = {}

from app import views
from app import models
from app import tests
