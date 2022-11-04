# Работа находится прямо в этом репозитории (я один в команде). https://github.com/supercruisertraining/Auth_sprint_1

# В данном репозитории находится сервис авторизации.

## Про доступ к ресурсам:
*В данной системе понятие роль означает подписку пользователя. Например, подписка премиум может позволять 
пользователю иметь доступ ко всем фильмам, включая новинки. А подписка медиум, может не давать пользователю
доступа к новинкам.*
*Пользователь может купить себе определенный уровень подписку (для этого есть API метод ```/api/v1/assign_role```,
который в будущем предполагает проверку оплаты)*

## Про базу данных
*Предполагается, что прод БД с данными крутится на другом сервере, как в большинстве реальных проектов. Запускать её в
docker-compose рядом с приложением считаю нецелесообразным.*
*Миграции alembic планируется также применять вручную, а не писать команды в docker-compose.*

## Про администраторов
*Методы, предназначенные только для администратора всегда начинаются с /admin/. Это сделано для того, чтобы
можно было ограничить к ним доступ с помощью ACL. К тому же, администратор имеет возможность поддерживать
только одну логин-сессию: при входе в аккаунт все его существующие refresh-токены удаляются.*


## Основные разделы:
- ### /src - Основной код
- ### /tests - Тесты на каждый API метод

## API методы:
 - ### ```/api/v1/create_user``` - Создание пользователя

 - ### ```/api/v1/update_user``` - Обновление данных пользователя

 - ### ```/api/v1/login``` - Вход в систему: генерация пары JWT-токенов

 - ### ```/api/v1/get_login_stat``` - Получить историю входов в аккаунт

 - ### ```/api/v1/get_roles``` - Получить список всех ролей (=возможных подписок)

 - ### ```/api/v1/refresh``` - Обновление пары токенов.

 - ### ```/api/v1/logout``` - Выход из аккаунта на текущем устройстве.

 - ### ```/api/v1/logout_hard``` - Выход из всех.

 - ### ```/api/v1/assign_role``` - Назначить роль пользователю.

 - ### ```/admin/api/v1/create_role``` - Создать роль.

 - ### ```/admin/api/v1/delete_role``` - Удалить роль.

 - ### ```/admin/api/v1/login``` - Вход администратора в систему.
 
 - ### ```/admin/api/v1/logout``` - Выход администратора из системы.

 - ### ```/admin/api/v1/refresh``` - Обновление токенов администратора.


## Про аутентификацию:
#### Используется JWT. Refresh-токены хранятся в Redis, чтобы можно было реализовать выход со всех устройств.
#### Когда пользователю нужно выйти из аккаунта со всех устройств, нужно удалить все refresh-токены на данного пользователя. Но поиск всех токенов данного клиента был бы затруднителен, так как структура данных в Redis следующая <token>: {<user_id>: user_id, <exp_utc>: exp_utc}. 
#### Поэтому, по мере добавления refresh токенов в Redis (при входе пользователя в систему) мы дублируем информацию в другую Бд redis со следующей структурой: <user_id::token>: {<user_id>: user_id, <exp_utc>: exp_utc, <token>: token}. С таким форматом ключей искать токены для конкретного user_id гораздо проще.

## Запуск приложения:

### Сборка образа
 ```shell
 docker build -t auth .
 ```

### Запуск docker-compose 
```shell
docker-compose up -d
```

## Запуск тестов

### Сборка образа (если до этого не производилась)
```shell
 docker build -t auth .
```

### Переходим в нужную директорию
```shell
cd tests
```
### Запуск docker-compose
```shell
docker-compose up -d
```

### Просмотр результатов тестов
```shell
docker-compose logs test
```