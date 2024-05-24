
# Web-приложение "Расписание групп"

Приложение на Streamlit "Расписание групп" с PostgreSQL

## Папка "бд"

Данная папка содержит следующие файлы:

`value.txt` - начальные данные для заполнения сущностей

`мой итог.pgerd` - файл БД PostgreSQL

`таблицы` - содержит файлы создания сущностей и темпоральных таблиц

`триггеры` - содержит необходимые функции откатов для работы БД

## Запуск приложения

Откройте терминал и запустите следующую команду

```bash
  streamlit run main.py
```

## Даталогическая таблица

![App Screenshot](images/dt.jpg)

## ER-диаграмма

![App Screenshot](images/er.jpg)

## Пример работы клиентского интерфейса

При запуске программы открывается окно входа, в котором пользователю необходимо ввести логин и пароль для авторизации, если он является сотрудником (рисунок 1). Если же программой воспользоваться хочет студент, то для него предусмотрена опция «Расписание групп». Нажав на неё, перед ним откроется поле ввода названия группы, в котором он может только просматривать расписание интересующей группы (рисунок 2). 

![App Screenshot](images/1.jpg)

![App Screenshot](images/2.jpg)

Пользователь может посмотреть расписание с выбором интересующей недели (рисунок 3).

![App Screenshot](images/3.jpg)

Если зайти под учётной записью преподавателя, то в интерфейсе появится меню выбора просмотра личного расписания, либо расписания групп (рисунок 4).

![App Screenshot](images/4.jpg)

При выборе поля «Мое расписание» и типа недели, нам выводится таблица с полями дня недели, времени, аудитории, группы и предмета (рисунок 5).

![App Screenshot](images/5.jpg)

При входе под учетной записью администратора в поле навигации появляются следующий доступный функционал: «Расписание групп», «Добавление», «Обновление», «Удаление», «Направление», «Учебный план», «Откат», «Выйти» (рисунок 6).

![App Screenshot](images/6.jpg)

При выборе просмотра «Расписание групп», нам доступно просмотреть расписание группы за интересующий нас семестр и интересующий тип недели (рисунок 7).

![App Screenshot](images/7.jpg)

При выборе поля «Добавление», нам доступен выбор, куда добавить необходимую информацию (рисунок 8).

![App Screenshot](images/8.jpg)

При выборе поля «Обновление», нам доступен выбор, где мы можем обновить необходимую информацию (рисунок 9).

![App Screenshot](images/9.jpg)

При выборе поля «Удаление», нам доступен выбор, где мы можем удалить необходимую информацию (рисунок 10).

![App Screenshot](images/10.jpg)

При выборе поля «Направление», нам доступен выбор, по добавлению, обновлению, удалению направления (рисунок 11).

![App Screenshot](images/11.jpg)

При выборе поля «Учебный план», нам доступна работа с данными учебных планов каждого направления (рисунок 12).

![App Screenshot](images/12.jpg)

При выборе поля «Откат», нам доступен функционал для отката нежелательных значений по времени (рисунок 13).

![App Screenshot](images/13.jpg)

