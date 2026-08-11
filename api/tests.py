from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note


class NoteAPITestCase(TestCase):
    """Functional tests for the Notes REST API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.note_data = {"title": "Test Note", "body": "This is a test note body."}
        self.note = Note.objects.create(title="Existing Note", body="Existing body.")

    def test_get_all_notes(self):
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_note(self):
        response = self.client.get(f"/api/notes/{self.note.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Existing Note")

    def test_create_note(self):
        response = self.client.post("/api/notes/create/", self.note_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Note.objects.count(), 2)

    def test_update_note(self):
        updated = {"title": "Updated Title", "body": "Updated body content."}
        response = self.client.put(
            f"/api/notes/{self.note.id}/update/", updated, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated Title")

    def test_delete_note(self):
        response = self.client.delete(f"/api/notes/{self.note.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Note.objects.count(), 0)

    def test_get_api_routes(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
