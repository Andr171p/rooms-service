from collections import UserString

import pytest
from pydantic import BaseModel, ValidationError

from rooms_service.domain.constants import MAX_ROLE_PRIORITY, MIN_ROLE_PRIORITY
from rooms_service.domain.value_objects import PermissionCode, RolePriority


class TestRolePriority:
    """Тестовые кейсы для приоритета роли"""
    @pytest.mark.parametrize(
        "valid_role_priority",
        [
            MIN_ROLE_PRIORITY,
            MAX_ROLE_PRIORITY,
            (MIN_ROLE_PRIORITY + MAX_ROLE_PRIORITY) // 2,
            1,
            100
        ]
    )
    def test_valid_role_priority(self, valid_role_priority: int) -> None:  # noqa: PLR6301
        """Тест валидных значений для приоритета роли"""
        role_priority = RolePriority(valid_role_priority)
        assert role_priority == valid_role_priority
        assert isinstance(role_priority, int)

    @pytest.mark.parametrize(
        "invalid_role_priority",
        [
            MIN_ROLE_PRIORITY - 1,
            MAX_ROLE_PRIORITY + 1,
            -1,
            1000,
            -100,
        ]
    )
    def test_invalid_role_priority(self, invalid_role_priority: int) -> None:  # noqa: PLR6301
        """Тест невалидных значений для приоритета роли"""
        with pytest.raises(ValueError, match="Priority must be between"):
            RolePriority(invalid_role_priority)

    def test_role_priority_in_pydantic_model(self) -> None:  # noqa: PLR6301
        """Тест примитива внутри pydantic модели"""

        class TestModel(BaseModel):
            priority: RolePriority

        model = TestModel(priority=50)
        assert model.priority == 50  # noqa: PLR2004
        assert isinstance(model.priority, int)

        with pytest.raises(ValidationError):
            TestModel(priority=MAX_ROLE_PRIORITY + 1)


class TestPermissionCode:
    """Тестовые кейсы для примитива PermissionCode"""

    @pytest.mark.parametrize(
        "valid_permission_code",
        [
            "message:send",
            "room:create",
            "member:delete:admin",
            "a:b:c:d:e",
        ]
    )
    def test_valid_permission_code(self, valid_permission_code: str) -> None:  # noqa: PLR6301
        """Тест валидного кода привилегий"""
        permission_code = PermissionCode(valid_permission_code)
        assert permission_code == valid_permission_code
        assert isinstance(permission_code, UserString)

    @pytest.mark.parametrize(
        "without_colon_permission_code",
        ["message", "", "send"]
    )
    def test_without_colon_permission_code(self, without_colon_permission_code: str) -> None:  # noqa: PLR6301
        """Тест permission code не содержащего ':'"""
        with pytest.raises(ValueError, match="Permission code must contain"):
            PermissionCode(without_colon_permission_code)

    @pytest.mark.parametrize(
        "invalid_permission_code",
        ["message:", ":", ":send"]
    )
    def test_invalid_permission_code(self, invalid_permission_code: str) -> None:  # noqa: PLR6301
        """Тест невалидного permission code"""
        with pytest.raises(ValueError, match="Invalid permission code!"):
            PermissionCode(invalid_permission_code)

    def test_permission_code_in_pydantic_model(self) -> None:  # noqa: PLR6301
        """Тест permission code внутри pydantic модели"""
        valid_permission_code = "message:send"
        invalid_permission_code = "message_send"

        class TestModel(BaseModel):
            code: PermissionCode

        model = TestModel(code=valid_permission_code)
        assert model.code == valid_permission_code
        assert isinstance(model.code, str)

        with pytest.raises(ValidationError):
            TestModel(code=invalid_permission_code)
