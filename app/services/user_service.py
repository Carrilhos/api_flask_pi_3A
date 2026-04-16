from app.models.user_model import User

def get_all_users():
    users = [
        User(1, "Gabriel"),
        User(2, "Maria")
    ]

    return [user.to_dict() for user in users]