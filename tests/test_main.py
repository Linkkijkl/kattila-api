import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestKattilaApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass


    def setUp(self) -> None:
        with TestClient(app) as client:
            self.client = client


    def test_coffee_image_endpoint_exists(self):
        response = self.client.get("/coffee/image")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)