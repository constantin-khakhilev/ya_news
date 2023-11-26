from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Создаём объект новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def all_news():
    """Создаём список новостей."""
    today = datetime.today()
    # Выражение генератора новостей.
    news_gen = (
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    News.objects.bulk_create(news_gen)
    return all_news


@pytest.fixture
def comment(author, news):
    """От имени одного пользователя создаём комментарии к новости."""
    now = timezone.now()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def id_news_for_args(news):
    return news.id,


@pytest.fixture
def id_comment_for_args(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }


@pytest.fixture
def home_url():
    """Главная страница."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Страница входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Страница выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Страница регистрации."""
    return reverse('users:signup')


@pytest.fixture
def detail_url(id_news_for_args):
    """Отображение новости."""
    return reverse('news:detail', args=id_news_for_args)


@pytest.fixture
def delete_url(id_comment_for_args):
    """Удаление комментария."""
    return reverse('news:delete', args=id_comment_for_args)


@pytest.fixture
def edit_url(id_comment_for_args):
    """Редактирование комментария."""
    return reverse('news:edit', args=id_comment_for_args)


@pytest.fixture
def bad_words_data():
    """Словарь запрещённых слов."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    return bad_words_data
