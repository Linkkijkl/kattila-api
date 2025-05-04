import unittest
from io import BytesIO
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image, ImageChops


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
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", sent_image_bytes, "image/png")}
        response = self.client.post("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"detail": "Method Not Allowed"})

    def test_coffee_image_endpoint_put_missing_api_key_headers(self):
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        files = {"file": ("filename", sent_image_bytes, "image/png")}
        response = self.client.put("/coffee/image", files=files)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_coffee_image_endpoint_put_wrong_api_key_headers(self):
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        headers = {"X-API-Key": "UNAUTHORIZED_KEY"}
        files = {"file": ("filename", sent_image_bytes, "image/png")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    def test_coffee_image_endpoint_put_correct_api_key_headers(self):
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", sent_image_bytes, "image/png")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_coffee_image_endpoint_incorrect_media_type(self):
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", sent_image_bytes, "image/example")}
        response = self.client.put("/coffee/image", headers=headers, files=files)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_coffee_image_endpoint_image_updates(self):
        sent_image = Image.new("RGB", (600, 800), color="white")
        sent_image_bytes = BytesIO()
        sent_image.save(sent_image_bytes, "png")
        headers = {"X-API-Key": "TESTING_API_KEY"}
        files = {"file": ("filename", sent_image_bytes, "image/png")}
        self.client.put("/coffee/image", headers=headers, files=files)
        response = self.client.get("/coffee/image")
        received_image = Image.open(BytesIO(response.content))
        self.assertFalse(ImageChops.difference(sent_image, received_image).getbbox())


if __name__ == "__main__":
    unittest.main(verbosity=2)
