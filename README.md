# DRF_Poll_Form
Тестовое задание, REST API для сервиса опросов на DRF.
<span style="color:orange">Данная инструкция рассчитана для Ubuntu 18.04. lts </span>

Для начала создадим виртуальное окружение с python3, а затем его запустим.
```
python3 -m venv env
source env/bin/activate
```
Теперь загрузим проект и установим.
```
git clone https://github.com/rysevpd/DRF_Poll_Form.git
cd ./DRF_Poll_Form
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```
Перед запуском самого сервера надо создать super-пользователя. Он запросит у вас логин,
почту для сброса и пароль.
```
python manage.py createsuperuser
```
Запуск сервера.
```
python manage.py runserver
```



# REST API
Возвращается json-формат.
Требуется авторизация.

------

### GET /admin/polls

Получение абсолютно всех опросов.

#####Example
```
{
    "id": 1,
    "name_test": "Первый опрос",
    "about_test": "Простой опрос об истории linux",
    "date_start": "2021-04-22",
    "date_finish": "2021-04-25"
}
```
### GET /admin/polls/<id_poll>
Получить один конкретный опрос.
### POST /admin/polls
Cоздание нового опроса.
##### Example
```
{
    "name_test": "Первый опрос",
    "about_test": "Простой опрос об истории linux",
    "date_start": "2021-04-22",
    "date_finish": "2021-04-25"
}
```
<span style="color:red">ВАЖНО: указывайте дату в формате "YYYY-MM-DD"</span>
### DELETE /admin/polls/<id_poll>
Удалить опрос.
#### PATCH /admin/polls/<id_poll>
Редактировать информацию об опросе.
### POST /admin/polls/<id_poll>/questions
Создание нового вопроса для теста. Есть три варианта вопроса: 'text', 'one_answer', 'multiple_answer'. Соответственно 
это вопрос с развернутым ответом, вопрос с выбором одного варианта и вопрос с выбором нескольких вариантов ответа.

##### Example №1
```
{
    "type": "text",
    "text": "Кто такой Линус Торвальдс?"
}
```
##### Example №2
```
{
    "type": "one_answer",
    "text": "Кто такой Линус Торвальдс?",
    "answeroptions": ["Создатель Линукс", "Бабочка", "Судья"]
}
```

### GET /admin/polls/<id_poll>/questions/<id_question>
Выведет только конкретный вопрос из теста

### DELETE /admin/polls<id_poll>/questions/<id_question>
Удалит нужный вам запрос

### PATCH /admin/polls/(id_poll/questions/<id_question>
Редактировать вопрос. Синтаксис аналогичен созданию вопроса.

#Пользователи

### GET /polls/<id_poll>
Получить определенный опрос с его вопросами.

### POST /polls/<id_poll>
Отправить решение теста от пользователя.

##### Example 
```
{
    "id_user": "1212122121",
    "answers": ["id_question":"Ответ", "id_question": "Еще ответ"]
}
```

#### GET /pollsByUser/<id_user>
Передаст все опросы вместе с вопросами и вашим ответом.


