from django.db import DatabaseError, connection
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer

@api_view(["GET"])
def getRoutes(request):
    routes = [
        {
            "Endpoint": "/api/notes/",
            "method": "GET",
            "body": None,
            "description": "Returns an array of notes",
        },
        {
            "Endpoint": "/api/notes/<id>/",
            "method": "GET",
            "body": None,
            "description": "Returns a single note object",
        },
        {
            "Endpoint": "/api/notes/create/",
            "method": "POST",
            "body": {"body": ""},
            "description": "Creates a note from request data",
        },
        {
            "Endpoint": "/api/notes/<id>/update/",
            "method": "PUT",
            "body": {"body": ""},
            "description": "Updates an existing note",
        },
        {
            "Endpoint": "/api/notes/<id>/delete/",
            "method": "DELETE",
            "body": None,
            "description": "Deletes an existing note",
        },
        {
            "Endpoint": "/api/healthz/",
            "method": "GET",
            "body": None,
            "description": "Liveness probe for Kubernetes",
        },
        {
            "Endpoint": "/api/readyz/",
            "method": "GET",
            "body": None,
            "description": "Readiness probe that checks database access",
        },
    ]
    return Response(routes)


@api_view(["GET"])
def healthz(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def readyz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return Response(
            {"status": "unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"status": "ready"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def getNotes(request):
    notes = Note.objects.all().order_by('-created')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
def updateNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    serializer = NoteSerializer(instance=note, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def deleteNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    note.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def createNote(request):
    serializer = NoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
