# Django
from rest_framework import status

# Standard Library
import json

# Third Party
import pytest

# DocumentCloud
from documentcloud.organizations.tests.factories import OrganizationFactory
from documentcloud.users.serializers import UserSerializer
from documentcloud.users.tests.factories import UserFactory


@pytest.mark.django_db()
class TestUserAPI:
    def test_list(self, client):
        """List users"""
        size = 10
        users = UserFactory.create_batch(size)
        OrganizationFactory(members=users)
        client.force_authenticate(user=users[0])
        response = client.get(f"/api/users/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        assert len(response_json["results"]) == size

    def test_retrieve(self, client):
        """Test retrieving a user"""
        users = UserFactory.create_batch(2)
        OrganizationFactory(members=users)
        client.force_authenticate(user=users[0])
        response = client.get(f"/api/users/{users[1].pk}/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        serializer = UserSerializer(users[1])
        assert response_json == serializer.data

    def test_retrieve_me(self, client, user):
        """Test retrieving the currently logged in user"""
        client.force_authenticate(user=user)
        response = client.get(f"/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        response_json = json.loads(response.content)
        serializer = UserSerializer(user)
        assert response_json == serializer.data

    def test_retrieve_me_anonymous(self, client):
        """me endpoint doesn't work for logged out users"""
        response = client.get(f"/api/users/me/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update(self, client, user):
        """Test setting a users active org"""
        organization = OrganizationFactory(members=[user])
        assert user.organization != organization
        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/users/{user.pk}/", {"organization": organization.pk}
        )
        assert response.status_code == status.HTTP_200_OK
        assert user.organization == organization

    def test_update_bad_member(self, client, user, organization):
        """Cannot set active organization to an organization you do not belong to"""
        assert user.organization != organization
        client.force_authenticate(user=user)
        response = client.patch(
            f"/api/users/{user.pk}/", {"organization": organization.pk}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_bad_exists(self, client, user):
        """Cannot set active organization to an organization that doesn't exist"""
        client.force_authenticate(user=user)
        response = client.patch(f"/api/users/{user.pk}/", {"organization": 999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST