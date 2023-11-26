"""Тестирование бизнес-логики приложения.

Как обрабатываются те или иные формы, разрешено ли создание объектов с
неуникальными полями, как работает специфичная логика конкретного приложения.
"""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url
):
    """Проверка POST-запросов на добавление комментариев."""
    comments_count_start = Comment.objects.count()
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    comments_count_finish = Comment.objects.count()
    assert comments_count_finish - comments_count_start == 0


def test_user_can_create_comment(
    author_client, author, form_data, detail_url, news
):
    """Проверим, что залогиненный пользователь может оставить комментарий."""
    comments_count_start = Comment.objects.count()
    author_client.post(detail_url, data=form_data)
    comments_count_finish = Comment.objects.count()
    assert comments_count_finish - comments_count_start == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url, bad_words_data):
    """Проверка блокировки стоп-слов."""
    comments_count_start = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_finish = Comment.objects.count()
    assert comments_count_finish - comments_count_start == 0


def test_author_can_delete_comment(
    author_client, detail_url, delete_url
):
    """Проверка удаления комментария автором."""
    url_to_comments = detail_url + '#comments'
    comments_count_start = Comment.objects.count()
    assert comments_count_start > 0
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count_finish = Comment.objects.count()
    assert comments_count_start - comments_count_finish == 1


def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_url
):
    """Проверка удаления комментария читателем."""
    comments_count_start = Comment.objects.count()
    assert comments_count_start > 0
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_finish = Comment.objects.count()
    assert comments_count_start - comments_count_finish == 0


def test_author_can_edit_comment(
    author_client, edit_url, detail_url, form_data, comment
):
    """Проверка редактирования комментария автором."""
    url_to_comments = detail_url + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, edit_url, form_data, comment
):
    """Проверка редактирования комментария читателем."""
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
