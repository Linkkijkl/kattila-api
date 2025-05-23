import unittest
from unittest import mock
from io import BytesIO
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app, redis_connection
from app.seuranta import SeurantaUser, SeurantaUsers
from PIL import Image, ImageChops
from fakeredis import FakeAsyncRedis


async def fakeredis_connection():
    async with FakeAsyncRedis() as connection:
        yield connection


class TestKattilaLifesignApi(unittest.TestCase):
    def setUp(self) -> None:
        with TestClient(app) as client:
            self.client = client

    def test_lifesign_endpoint_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestKattilaSeurantaApi(unittest.TestCase):
    def setUp(self) -> None:
        with TestClient(app) as client:
            self.client = client
            self.testing_headers = {"X-API-Key": "TESTING_API_KEY"}
            self.testing_seuranta_users: SeurantaUsers = SeurantaUsers(
                users=[
                    SeurantaUser(
                        username="KariLink",
                        memberships=["linkki"],
                        board_memberships=["linkki"],
                    ),
                    SeurantaUser(
                        username="LaineAlgo",
                        memberships=["algo"],
                        board_memberships=["algo"],
                    ),
                    SeurantaUser(
                        username="hybridi",
                        memberships=["algo", "linkki"],
                        board_memberships=["algo", "linkki"],
                    ),
                    SeurantaUser(
                        username="basic", memberships=[], board_memberships=[]
                    ),
                    SeurantaUser(username="empty"),
                    SeurantaUser(
                        username="howlmao", board_memberships=["algo", "linkki"]
                    ),
                ]
            )

    def test_seuranta_endpoint_exists(self):
        response = self.client.get("/seuranta/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seuranta_endpoint_post_not_allowed(self):
        response = self.client.post(
            "/seuranta/users",
            content=self.testing_seuranta_users.model_dump_json(),
            headers=self.testing_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"detail": "Method Not Allowed"})

    def test_seuranta_endpoint_put_missing_api_key_headers(self):
        response = self.client.put(
            "/seuranta/users", content=self.testing_seuranta_users.model_dump_json()
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_seuranta_endpoint_put_wrong_api_key_headers(self):
        incorrect_headers = {"X-API-Key": "UNAUTHORIZED_KEY"}
        response = self.client.put(
            "/seuranta/users",
            content=self.testing_seuranta_users.model_dump_json(),
            headers=incorrect_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    def test_seuranta_endpoint_put_correct_api_key_headers(self):
        response = self.client.put(
            "/seuranta/users",
            content=self.testing_seuranta_users.model_dump_json(),
            headers=self.testing_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seuranta_endpoint_users_updates(self):
        self.client.put(
            "/seuranta/users",
            json={"users": []},
            headers=self.testing_headers,
        )
        initial_response = self.client.get("/seuranta/users")
        put_response = self.client.put(
            "/seuranta/users",
            content=self.testing_seuranta_users.model_dump_json(),
            headers=self.testing_headers,
        )
        self.assertNotEqual(initial_response.json(), put_response.json())
        final_response = self.client.get("/seuranta/users")
        self.assertEqual(put_response.json(), final_response.json())


class TestKattilaCoffeeImageApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self) -> None:
        with TestClient(app) as client:
            self.client = client
            self.testing_headers = {"X-API-Key": "TESTING_API_KEY"}
            self.test_white_image = Image.new("RGB", (600, 800), color="white")
            self.test_white_image_bytes_png = BytesIO()
            self.test_white_image.save(self.test_white_image_bytes_png, "png")
            self.test_white_image_file = {
                "file": ("filename", self.test_white_image_bytes_png, "image/png")
            }

    def test_coffee_image_endpoint_exists(self):
        response = self.client.get("/coffee/image")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_coffee_image_endpoint_post_not_allowed(self):
        response = self.client.post(
            "/coffee/image",
            headers=self.testing_headers,
            files=self.test_white_image_file,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"detail": "Method Not Allowed"})

    def test_coffee_image_endpoint_put_missing_api_key_headers(self):
        response = self.client.put("/coffee/image", files=self.test_white_image_file)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_coffee_image_endpoint_put_wrong_api_key_headers(self):
        incorrect_headers = {"X-API-Key": "UNAUTHORIZED_KEY"}
        response = self.client.put(
            "/coffee/image", headers=incorrect_headers, files=self.test_white_image_file
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": "Unauthorized"})

    def test_coffee_image_endpoint_put_correct_api_key_headers(self):
        response = self.client.put(
            "/coffee/image",
            headers=self.testing_headers,
            files=self.test_white_image_file,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_coffee_image_endpoint_incorrect_media_type(self):
        files = {"file": ("filename", self.test_white_image_bytes_png, "image/example")}
        response = self.client.put(
            "/coffee/image", headers=self.testing_headers, files=files
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_coffee_image_endpoint_image_updates(self):
        self.client.put(
            "/coffee/image",
            headers=self.testing_headers,
            files=self.test_white_image_file,
        )
        response = self.client.get("/coffee/image")
        received_image = Image.open(BytesIO(response.content))
        images_same = (
            ImageChops.difference(self.test_white_image, received_image).getbbox() == None
        )
        self.assertTrue(images_same)


class TestKattilaAnnouncerApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self) -> None:
        with TestClient(app) as client1, TestClient(app) as client2:
            mock.patch.dict(app.dependency_overrides, {redis_connection: fakeredis_connection})
            self.client1 = client1
            self.client2 = client2

    def test_publish_subscribe(self):
        with self.client1.websocket_connect("/announcer/listen") as websocket:
            for test_message in ["test-message :-D", "another one", "keep on testing"]:
                self.client2.get("/announcer/new", params={"msg": test_message})
                received_message = websocket.receive_text()
                assert received_message == test_message


if __name__ == "__main__":
    unittest.main(verbosity=2)
