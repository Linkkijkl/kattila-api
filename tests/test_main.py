import unittest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image


class TestKattilaApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self) -> None:
        with TestClient(app) as client:
            self.client = client

    def test_lifesign_endpoint_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_coffee_image_endpoint_exists(self):
        response = self.client.get("/coffee/image")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_coffee_image_endpoint_post_not_allowed(self):
        response = self.client.post("/coffee/image")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"detail": "Method Not Allowed"})

    def test_coffee_image_endpoint_put_missing_api_key_headers(self):
        response = self.client.put("/coffee/image")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_coffee_image_endpoint_put_wrong_api_key_headers(self):
        img = Image.new("RGB", (600, 800), color="white")
        headers = {"X-API-Key": "UNAUTHORIZED_KEY"}
        files = {"file": ("filename", img.tobytes(), "image/jpeg")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    def test_coffee_image_endpoint_put_correct_api_key_headers(self):
        img = Image.new("RGB", (600, 800), color="white")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", img.tobytes(), "image/jpeg")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_coffee_image_endpoint_incorrect_media_type(self):
        img = Image.new("RGB", (600, 800), color="white")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", img.tobytes(), "image/example")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
