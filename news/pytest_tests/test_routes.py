"""Тесты доступности конкретных эндпоинтов, проверка редиректов.

Кодов ответа, которые возвращают страницы, тестирование доступа для
авторизованных или анонимных пользователей.
"""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, url, expected_status',
    (
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('home_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('login_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('logout_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('signup_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('detail_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('edit_url'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('delete_url'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('edit_url'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('delete_url'),
            HTTPStatus.OK
        ),
    )
)
def test_pages_availability(parametrized_client, url, expected_status):
    """Доступы до страниц."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('delete_url')),
    ),
)
def test_redirects(client, url):
    """Проверка редиректов."""
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
