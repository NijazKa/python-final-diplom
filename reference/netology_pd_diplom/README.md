# Реализация дипломной работы API-сервиса для магазина


## Этап 6. Реализация API views админки склада

Добавление эндпоинтов для работы с админкой:

    - /admin/users/ - отображает список всех пользователей
    - /admin/orders/ - реализует работу с заказами (поддерживаются методы GET, PATCH, DELETE)
    - /admin/products/ - реализует работу с товарами (поддерживаются методы GET, PATCH, DELETE)

Данные методы актуальны только для суперпользователей с параметром is_staff=True, авторизация через Токен


## **Проверить работу модулей**
    
    
    python3 manage.py runserver 0.0.0.0:8000


## **Установить СУБД (опционально)**

    sudo nano  /etc/apt/sources.list.d/pgdg.list
    
    ----->
    deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main
    <<----
    
    
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    sudo apt-get update
    
    sudo apt-get install postgresql-11 postgresql-server-dev-11
    
    sudo -u postgres psql postgres
    
    create user diplom_user with password 'password';
    
    alter role diplom_user set client_encoding to 'utf8';
    
    alter role diplom_user set default_transaction_isolation to 'read committed';
    
    alter role diplom_user set timezone to 'Europe/Moscow';
    
    create database diplom_db owner mploy;
    alter user mploy createdb;

    
   
