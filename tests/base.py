''' base.py '''
from flask_testing import TestCase

from simple_messenger.app import create_app
from simple_messenger.models import db, User


class Base(TestCase):

    def create_app(self):
        app = create_app()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self):
        user = User()
        db.session.add(user)
        db.session.commit()

        return user
