"""Тесты, касающиеся отображения контента.

Какие данные на каких страницах отображаются, какие при этом используются
шаблоны, как работает пагинатор.
"""

import pytest
from django.conf import settings


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count(client, home_url):
    """Тестируем количество новостей на странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_order(client, home_url):
    """Тестируем сортировку новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comment')
def test_comments_order(client, detail_url):
    """Сначала новые, затем старые комментарии."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates, reverse=False)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )

)
def test_news_detail_page_contains_form(
    parametrized_client, form_in_context, detail_url
):
    """Анонимному пользователю недоступна форма для отправки комментария на
    странице отдельной новости, а авторизованному доступна.
    """
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_in_context
