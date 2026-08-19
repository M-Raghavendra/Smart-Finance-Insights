import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app import app
from models import User
from flask_login import login_user

def debug_analytics():
    with app.app_context():
        with app.test_request_context('/analytics'):
            user = User.query.filter_by(email="vicky@gmail.com").first()
            login_user(user)
            client = app.test_client()
            client.post("/login", data={"email": "vicky@gmail.com", "password": "Vicky@123"})
            res = client.get("/analytics")
            print("Status code:", res.status_code)
            if res.status_code != 200:
                print("HTML Output / Error:")
                print(res.get_data(as_text=True))

if __name__ == "__main__":
    debug_analytics()
