from flask import current_app
from flaskblog import db, bcrypt, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id): # loads the currend user using user id stored in session
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)


    def __repr__(self):
        return f"User({self.username}, {self.email}, {self.image_file})"

    def generate_password_hash(self, password):
        return bcrypt.generate_password_hash(password)
    
    def check_password_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec) #initialize the serializer
        return s.dumps({'user_id': self.id}).decode('utf-8') # return generated reset token
    
    @staticmethod # telling python not to expect self as an argument. This method is bound to the class not the object
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)