import secrets, os
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename) # uploaded files have filename attribute. The unserscore is the filename(underscore since we won't use it)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)

    #Resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_filename


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset Request', #Subject
            sender = 'noreply@demo.com',
            recipients = [user.email]
    )

    msg.body = f'''
To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)} 

If you did not make this request then simply ignore this email and no changes will be made.
'''#external is used in order to get an absolute url not a relative url. Link in email should have full domain
    mail.send(msg)