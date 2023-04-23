hw05_final - Проект спринта: подписки на авторов.
Покрытие тестами проекта Yatube из спринта 6 Питон-разработчика бекенда Яндекс.Практикум. Все что нужно, это покрыть тестами проект, в учебных целях. Реализована система подписок/отписок на авторов постов.

Стек:

 - Python 3.10.5
 - Django==2.2.28
- mixer==7.1.2
- Pillow==9.0.1
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- requests==2.26.0
- six==1.16.0
- sorl-thumbnail==12.7.0

Клонируем проект:

```
git clone https://github.com/themasterid/hw05_final.git
```

Переходим в папку с проектом:

```
cd hw05_final
```

Устанавливаем виртуальное окружение:

```
python -m venv venv
```

Активируем виртуальное окружение:

```
source venv/Scripts/activate
```

Устанавливаем зависимости:

```
pip install -r requirements.txt
```

Применяем миграции:

```
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Создаем супер пользователя:

```
python yatube/manage.py createsuperuser
```

Для запуска тестов выполним:

```
pytest
```

python yatube/manage.py runserver localhost:80
После чего проект будет доступен по адресу http://localhost/

Заходим в http://localhost/admin и создаем группы и записи. После чего записи и группы появятся на главной странице.
