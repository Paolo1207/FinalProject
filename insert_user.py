from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create a new user
    username = 'admin' #edit if youre different user
    email = 'pamaui1207@gmail.com'
    password = 'admin123'

    # Check if user already exists
    user = User.query.filter((User.username == username) | (User.email == email)).first()
    if user:
        print(f"User {username} or {email} already exists.")
    else:
        new_user = User(username=username, email=email)
        new_user.password_hash = generate_password_hash(password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} added successfully.")
