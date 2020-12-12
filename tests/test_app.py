''' test_app.py '''
from tests.base import Base


class TestApp(Base):

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
