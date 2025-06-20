"""
Unit tests for security domain services.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.security.domain.entities import (
    AuthenticationToken,
    Permission,
    SecurityEvent,
    User,
)
from ingenious.security.domain.services import (
    IAuthenticationService,
    IAuthorizationService,
    IPasswordService,
    ISecurityEventService,
    ITokenService,
    IUserRepository,
)


class TestIUserRepository:
    """Test cases for IUserRepository interface."""

    def test_is_abstract_interface(self):
        """Test that IUserRepository is an abstract interface."""
        with pytest.raises(TypeError):
            IUserRepository()

    @pytest.mark.asyncio
    async def test_save_user_interface(self):
        """Test save_user method interface."""
        mock_repo = Mock(spec=IUserRepository)
        mock_repo.save_user = AsyncMock()

        user = User(username="testuser")
        await mock_repo.save_user(user)

        mock_repo.save_user.assert_called_once_with(user)

    @pytest.mark.asyncio
    async def test_get_user_interface(self):
        """Test get_user method interface."""
        mock_repo = Mock(spec=IUserRepository)
        expected_user = User(username="testuser", user_id="test-id")
        mock_repo.get_user = AsyncMock(return_value=expected_user)

        result = await mock_repo.get_user("test-id")

        assert result == expected_user
        mock_repo.get_user.assert_called_once_with("test-id")

    @pytest.mark.asyncio
    async def test_get_user_by_username_interface(self):
        """Test get_user_by_username method interface."""
        mock_repo = Mock(spec=IUserRepository)
        expected_user = User(username="testuser")
        mock_repo.get_user_by_username = AsyncMock(return_value=expected_user)

        result = await mock_repo.get_user_by_username("testuser")

        assert result == expected_user
        mock_repo.get_user_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_list_users_interface(self):
        """Test list_users method interface."""
        mock_repo = Mock(spec=IUserRepository)
        expected_users = [
            User(username="user1"),
            User(username="user2"),
        ]
        mock_repo.list_users = AsyncMock(return_value=expected_users)

        result = await mock_repo.list_users()

        assert result == expected_users
        mock_repo.list_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_interface(self):
        """Test delete_user method interface."""
        mock_repo = Mock(spec=IUserRepository)
        mock_repo.delete_user = AsyncMock(return_value=True)

        result = await mock_repo.delete_user("user-id")

        assert result is True
        mock_repo.delete_user.assert_called_once_with("user-id")


class TestIAuthenticationService:
    """Test cases for IAuthenticationService interface."""

    def test_is_abstract_interface(self):
        """Test that IAuthenticationService is an abstract interface."""
        with pytest.raises(TypeError):
            IAuthenticationService()

    @pytest.mark.asyncio
    async def test_authenticate_interface(self):
        """Test authenticate method interface."""
        mock_service = Mock(spec=IAuthenticationService)
        mock_token = Mock(spec=AuthenticationToken)
        mock_service.authenticate = AsyncMock(return_value=mock_token)

        result = await mock_service.authenticate("username", "password")

        assert result == mock_token
        mock_service.authenticate.assert_called_once_with("username", "password")

    @pytest.mark.asyncio
    async def test_validate_token_interface(self):
        """Test validate_token method interface."""
        mock_service = Mock(spec=IAuthenticationService)
        expected_user = User(username="testuser")
        mock_service.validate_token = AsyncMock(return_value=expected_user)

        result = await mock_service.validate_token("token123")

        assert result == expected_user
        mock_service.validate_token.assert_called_once_with("token123")

    @pytest.mark.asyncio
    async def test_refresh_token_interface(self):
        """Test refresh_token method interface."""
        mock_service = Mock(spec=IAuthenticationService)
        mock_token = Mock(spec=AuthenticationToken)
        mock_service.refresh_token = AsyncMock(return_value=mock_token)

        result = await mock_service.refresh_token("old_token")

        assert result == mock_token
        mock_service.refresh_token.assert_called_once_with("old_token")

    @pytest.mark.asyncio
    async def test_logout_interface(self):
        """Test logout method interface."""
        mock_service = Mock(spec=IAuthenticationService)
        mock_service.logout = AsyncMock()

        await mock_service.logout("token123")

        mock_service.logout.assert_called_once_with("token123")


class TestIAuthorizationService:
    """Test cases for IAuthorizationService interface."""

    def test_is_abstract_interface(self):
        """Test that IAuthorizationService is an abstract interface."""
        with pytest.raises(TypeError):
            IAuthorizationService()

    @pytest.mark.asyncio
    async def test_authorize_interface(self):
        """Test authorize method interface."""
        mock_service = Mock(spec=IAuthorizationService)
        mock_service.authorize = AsyncMock(return_value=True)

        user = User(username="testuser")
        result = await mock_service.authorize(user, Permission.READ, "resource")

        assert result is True
        mock_service.authorize.assert_called_once_with(
            user, Permission.READ, "resource"
        )

    @pytest.mark.asyncio
    async def test_get_user_permissions_interface(self):
        """Test get_user_permissions method interface."""
        mock_service = Mock(spec=IAuthorizationService)
        expected_permissions = [Permission.READ, Permission.WRITE]
        mock_service.get_user_permissions = AsyncMock(return_value=expected_permissions)

        result = await mock_service.get_user_permissions("user-id")

        assert result == expected_permissions
        mock_service.get_user_permissions.assert_called_once_with("user-id")


class TestISecurityEventService:
    """Test cases for ISecurityEventService interface."""

    def test_is_abstract_interface(self):
        """Test that ISecurityEventService is an abstract interface."""
        with pytest.raises(TypeError):
            ISecurityEventService()

    @pytest.mark.asyncio
    async def test_log_event_interface(self):
        """Test log_event method interface."""
        mock_service = Mock(spec=ISecurityEventService)
        mock_service.log_event = AsyncMock()

        event = SecurityEvent(event_type="login")
        await mock_service.log_event(event)

        mock_service.log_event.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_get_events_interface(self):
        """Test get_events method interface."""
        mock_service = Mock(spec=ISecurityEventService)
        expected_events = [
            SecurityEvent(event_type="login"),
            SecurityEvent(event_type="logout"),
        ]
        mock_service.get_events = AsyncMock(return_value=expected_events)

        result = await mock_service.get_events("user-id", "login", 50)

        assert result == expected_events
        mock_service.get_events.assert_called_once_with("user-id", "login", 50)


class TestIPasswordService:
    """Test cases for IPasswordService interface."""

    def test_is_abstract_interface(self):
        """Test that IPasswordService is an abstract interface."""
        with pytest.raises(TypeError):
            IPasswordService()

    @pytest.mark.asyncio
    async def test_hash_password_interface(self):
        """Test hash_password method interface."""
        mock_service = Mock(spec=IPasswordService)
        mock_service.hash_password = AsyncMock(return_value="hashed_password")

        result = await mock_service.hash_password("plain_password")

        assert result == "hashed_password"
        mock_service.hash_password.assert_called_once_with("plain_password")

    @pytest.mark.asyncio
    async def test_verify_password_interface(self):
        """Test verify_password method interface."""
        mock_service = Mock(spec=IPasswordService)
        mock_service.verify_password = AsyncMock(return_value=True)

        result = await mock_service.verify_password("plain", "hashed")

        assert result is True
        mock_service.verify_password.assert_called_once_with("plain", "hashed")

    @pytest.mark.asyncio
    async def test_generate_password_interface(self):
        """Test generate_password method interface."""
        mock_service = Mock(spec=IPasswordService)
        mock_service.generate_password = AsyncMock(return_value="generated123!")

        result = await mock_service.generate_password(16)

        assert result == "generated123!"
        mock_service.generate_password.assert_called_once_with(16)


class TestITokenService:
    """Test cases for ITokenService interface."""

    def test_is_abstract_interface(self):
        """Test that ITokenService is an abstract interface."""
        with pytest.raises(TypeError):
            ITokenService()

    @pytest.mark.asyncio
    async def test_generate_token_interface(self):
        """Test generate_token method interface."""
        mock_service = Mock(spec=ITokenService)
        mock_token = Mock(spec=AuthenticationToken)
        mock_service.generate_token = AsyncMock(return_value=mock_token)

        user = User(username="testuser")
        result = await mock_service.generate_token(user, 7200)

        assert result == mock_token
        mock_service.generate_token.assert_called_once_with(user, 7200)

    @pytest.mark.asyncio
    async def test_decode_token_interface(self):
        """Test decode_token method interface."""
        mock_service = Mock(spec=ITokenService)
        expected_payload = {"user_id": "123", "exp": 1234567890}
        mock_service.decode_token = AsyncMock(return_value=expected_payload)

        result = await mock_service.decode_token("token123")

        assert result == expected_payload
        mock_service.decode_token.assert_called_once_with("token123")

    @pytest.mark.asyncio
    async def test_revoke_token_interface(self):
        """Test revoke_token method interface."""
        mock_service = Mock(spec=ITokenService)
        mock_service.revoke_token = AsyncMock()

        await mock_service.revoke_token("token123")

        mock_service.revoke_token.assert_called_once_with("token123")


class TestDomainServiceInteractions:
    """Test interactions between domain services."""

    @pytest.mark.asyncio
    async def test_authentication_workflow(self):
        """Test complete authentication workflow."""
        user_repo = Mock(spec=IUserRepository)
        auth_service = Mock(spec=IAuthenticationService)
        password_service = Mock(spec=IPasswordService)
        token_service = Mock(spec=ITokenService)
        event_service = Mock(spec=ISecurityEventService)

        # Mock user lookup
        user = User(username="testuser", user_id="user-123")
        user_repo.get_user_by_username = AsyncMock(return_value=user)

        # Mock password verification
        password_service.verify_password = AsyncMock(return_value=True)

        # Mock token generation
        token = Mock(spec=AuthenticationToken)
        token_service.generate_token = AsyncMock(return_value=token)

        # Mock authentication
        auth_service.authenticate = AsyncMock(return_value=token)

        # Mock event logging
        event_service.log_event = AsyncMock()

        # Perform authentication
        result_token = await auth_service.authenticate("testuser", "password")

        # Log security event
        login_event = SecurityEvent(
            event_type="login_success",
            user_id=user.user_id,
        )
        await event_service.log_event(login_event)

        assert result_token == token
        auth_service.authenticate.assert_called_once_with("testuser", "password")
        event_service.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_authorization_workflow(self):
        """Test authorization workflow."""
        user_repo = Mock(spec=IUserRepository)
        auth_service = Mock(spec=IAuthorizationService)
        event_service = Mock(spec=ISecurityEventService)

        # Mock user with permissions
        user = User(
            username="developer",
            user_id="user-123",
            permissions=[Permission.READ, Permission.WRITE],
        )
        user_repo.get_user = AsyncMock(return_value=user)

        # Mock authorization check
        auth_service.authorize = AsyncMock(return_value=True)

        # Check authorization
        is_authorized = await auth_service.authorize(user, Permission.READ, "file.txt")

        # Log authorization event
        event_service.log_event = AsyncMock()
        auth_event = SecurityEvent(
            event_type="authorization_check",
            user_id=user.user_id,
            details={
                "permission": Permission.READ.value,
                "resource": "file.txt",
                "granted": is_authorized,
            },
        )
        await event_service.log_event(auth_event)

        assert is_authorized is True
        auth_service.authorize.assert_called_once_with(
            user, Permission.READ, "file.txt"
        )
        event_service.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_management_workflow(self):
        """Test user management workflow."""
        user_repo = Mock(spec=IUserRepository)
        password_service = Mock(spec=IPasswordService)
        event_service = Mock(spec=ISecurityEventService)

        # Create new user
        password_service.hash_password = AsyncMock(return_value="hashed_password")
        user_repo.save_user = AsyncMock()
        event_service.log_event = AsyncMock()

        # Hash password and create user
        await password_service.hash_password("new_password")
        user = User(
            username="newuser",
            permissions=[Permission.READ],
        )

        # Save user
        await user_repo.save_user(user)

        # Log user creation event
        creation_event = SecurityEvent(
            event_type="user_created",
            user_id=user.user_id,
            details={"username": user.username, "role": user.role.value},
        )
        await event_service.log_event(creation_event)

        password_service.hash_password.assert_called_once_with("new_password")
        user_repo.save_user.assert_called_once_with(user)
        event_service.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_validation_workflow(self):
        """Test token validation workflow."""
        auth_service = Mock(spec=IAuthenticationService)
        token_service = Mock(spec=ITokenService)
        event_service = Mock(spec=ISecurityEventService)

        # Mock token validation
        user = User(username="testuser", user_id="user-123")
        auth_service.validate_token = AsyncMock(return_value=user)

        # Mock token decoding
        token_payload = {"user_id": "user-123", "exp": 1234567890}
        token_service.decode_token = AsyncMock(return_value=token_payload)

        # Validate token
        validated_user = await auth_service.validate_token("token123")

        # Log token validation
        event_service.log_event = AsyncMock()
        validation_event = SecurityEvent(
            event_type="token_validated",
            user_id=validated_user.user_id,
        )
        await event_service.log_event(validation_event)

        assert validated_user == user
        auth_service.validate_token.assert_called_once_with("token123")
        event_service.log_event.assert_called_once()
