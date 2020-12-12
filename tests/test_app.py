''' test_app.py '''
from flask_testing import TestCase

from simple_messenger.app import create_app


class TestApp(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_generic_404(self):
        res = self.client.get('/foo/bar')

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            res.json,
            {
                'status': 'NOT_FOUND',
            }
        )

    def test_health(self):
        res = self.client.get('/health')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json,
            {
                'status': 'OK',
            }
        )
