# Django
from rest_framework import status

# Standard Library
import json

# Third Party
import pytest

# DocumentCloud
from documentcloud.documents.tests.factories import DocumentFactory
from documentcloud.organizations.tests.factories import OrganizationFactory
from documentcloud.projects.models import Collaboration, Project, ProjectMembership
from documentcloud.projects.serializers import (
    CollaborationSerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
)
from documentcloud.projects.tests.factories import ProjectFactory
from documentcloud.users.tests.factories import UserFactory


@pytest.mark.django_db()
class TestProjectAPI:
    def test_list(self, client):
        """List projects"""
        size = 10
        ProjectFactory.create_batch(size)
        response = client.get(f"/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_create(self, client, user):
        """Create a new project"""
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/projects/",
            {"title": "Test", "description": "This is a test project"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_json = json.loads(response.content)
        project = Project.objects.filter(pk=response_json["id"]).first()
        assert project is not None
        assert project.user == user
        assert project.collaborators.filter(pk=user.pk).exists()

    def test_retrieve(self, client, project):
        """Test retrieving a project"""
        response = client.get(f"/api/projects/{project.pk}/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        serializer = ProjectSerializer(project)
        assert response_json == serializer.data

    def test_update(self, client, project):
        """Test updating a project"""
        client.force_authenticate(user=project.user)
        title = "New Title"
        response = client.patch(f"/api/projects/{project.pk}/", {"title": title})
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.title == title

    def test_destroy(self, client, project):
        """Test destroying a project"""
        client.force_authenticate(user=project.user)
        response = client.delete(f"/api/projects/{project.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db()
class TestProjectMembershipAPI:
    def test_list(self, client):
        """List documents in a project"""
        size = 10
        project = ProjectFactory(documents=DocumentFactory.create_batch(size))
        response = client.get(f"/api/projects/{project.pk}/documents/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_create(self, client, project, document):
        """Add a document to a project"""
        client.force_authenticate(user=project.user)
        response = client.post(
            f"/api/projects/{project.pk}/documents/", {"document": document.pk}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert project.documents.filter(pk=document.pk).exists()

    def test_create_bad_edit_access(self, client, project, document):
        """You may not enable edit access in a project if you do not have edit access"""
        client.force_authenticate(user=project.user)
        response = client.post(
            f"/api/projects/{project.pk}/documents/",
            {"document": document.pk, "edit_access": True},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_bad_collaborator(self, client, user, project, document):
        """You may not add a document to a project you are not a collaborator on"""
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/projects/{project.pk}/documents/", {"document": document.pk}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve(self, client, document):
        """Test retrieving a document from project"""
        project = ProjectFactory(documents=[document])
        response = client.get(f"/api/projects/{project.pk}/documents/{document.pk}/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        projectmembership = project.projectmembership_set.get(document=document)
        serializer = ProjectMembershipSerializer(projectmembership)
        assert response_json == serializer.data

    def test_update(self, client, document):
        """Test updating a document in a project"""
        project = ProjectFactory(user=document.user, documents=[document])
        projectmembership = project.projectmembership_set.get(document=document)
        client.force_authenticate(user=project.user)
        response = client.patch(
            f"/api/projects/{project.pk}/documents/{document.pk}/",
            {"edit_access": True},
        )
        assert response.status_code == status.HTTP_200_OK
        projectmembership.refresh_from_db()
        assert projectmembership.edit_access

    def test_update_bad_document(self, client):
        """You may not try to change the document ID"""
        documents = DocumentFactory.create_batch(2)
        project = ProjectFactory(user=documents[0].user, documents=[documents[0]])
        client.force_authenticate(user=project.user)
        response = client.patch(
            f"/api/projects/{project.pk}/documents/{documents[0].pk}/",
            {"document": documents[1].pk},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_bad_edit_access(self, client, user, document):
        """You may not enable edit access in a project if you do not have edit access"""
        project = ProjectFactory(user=user, documents=[document])
        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/projects/{project.pk}/documents/{document.pk}/",
            {"edit_access": True},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_destroy(self, client, document):
        """Test removing a document from a project"""
        project = ProjectFactory(user=document.user, documents=[document])
        client.force_authenticate(user=project.user)
        response = client.delete(f"/api/projects/{project.pk}/documents/{document.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not project.documents.filter(pk=document.pk).exists()

    def test_destroy_bad_collaborator(self, client, user, document):
        """You cannot remove a document from a project you are not a collaborator on"""
        project = ProjectFactory(user=document.user, documents=[document])
        client.force_authenticate(user=user)
        response = client.delete(f"/api/projects/{project.pk}/documents/{document.pk}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
class TestCollaborationAPI:
    def test_list(self, client):
        """List users in a project"""
        size = 10
        project = ProjectFactory(collaborators=UserFactory.create_batch(size))
        response = client.get(f"/api/projects/{project.pk}/users/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        # add one for the projects owner
        assert len(response_json["results"]) == size + 1

    def test_create(self, client, project, user):
        """Add a user to a project"""
        # Add both users to an organization so they have view access to each other
        OrganizationFactory(members=[project.user, user])
        client.force_authenticate(user=project.user)
        response = client.post(f"/api/projects/{project.pk}/users/", {"user": user.pk})
        assert response.status_code == status.HTTP_201_CREATED
        assert project.collaborators.filter(pk=user.pk).exists()

    def test_create_bad_collaborator(self, client, project, user):
        """You may not add a collaborator to a project you are not a collaborator on"""
        OrganizationFactory(members=[project.user, user])
        client.force_authenticate(user=user)
        response = client.post(f"/api/projects/{project.pk}/users/", {"user": user.pk})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve(self, client, user):
        """Test retrieving a user from project"""
        project = ProjectFactory(collaborators=[user])
        response = client.get(f"/api/projects/{project.pk}/users/{user.pk}/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        collaboration = project.collaboration_set.get(user=user)
        serializer = CollaborationSerializer(collaboration)
        assert response_json == serializer.data

    def test_destroy(self, client, user):
        """Test removing a user from a project"""
        project = ProjectFactory(collaborators=[user])
        client.force_authenticate(user=project.user)
        response = client.delete(f"/api/projects/{project.pk}/users/{user.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not project.collaborators.filter(pk=user.pk).exists()

    def test_destroy_bad_collaborator(self, client, user, project):
        """You cannot remove a user from a project you are not a collaborator on"""
        client.force_authenticate(user=user)
        response = client.delete(f"/api/projects/{project.pk}/users/{project.user.pk}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN