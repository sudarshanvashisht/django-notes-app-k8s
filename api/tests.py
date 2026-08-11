from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class NoteApiTests(APITestCase):
    def test_health_endpoints(self):
        self.assertEqual(self.client.get(reverse("healthz")).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse("readyz")).status_code, status.HTTP_200_OK)

    def test_crud_flow(self):
        create_response = self.client.post(
            reverse("create-note"),
            {"body": "First note"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["body"], "First note")

        note_id = create_response.data["id"]

        list_response = self.client.get(reverse("notes"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        detail_response = self.client.get(reverse("note", args=[note_id]))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["body"], "First note")

        update_response = self.client.put(
            reverse("update-note", args=[note_id]),
            {"body": "Updated note"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["body"], "Updated note")

        delete_response = self.client.delete(reverse("delete-note", args=[note_id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(reverse("notes")).data, [])
