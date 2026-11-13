# Pet_Parsing_AI --- AUTO.RIA Analyzer

Десктопное приложение для поиска автомобилей на AUTO.RIA, сбора
объявлений и анализа рыночной стоимости с помощью OpenAI.

> **Текущая архитектура:** интерфейс работает как отдельное
> Windows-приложение, а поиск, работа с AUTO.RIA API, AI-анализ и
> хранение истории выполняются на FastAPI backend. Backend и PostgreSQL
> запускаются через Docker Compose.

## Содержание

-   [1. Как устроен запуск](#1-как-устроен-запуск)
-   [2. Что нужно установить](#2-что-нужно-установить)
-   [3. Настройка переменных
    окружения](#3-настройка-переменных-окружения)
-   [4. Локальный запуск на одном
    компьютере](#4-локальный-запуск-на-одном-компьютере)
-   [5. Первый запуск и создание таблиц
    БД](#5-первый-запуск-и-создание-таблиц-бд)
-   [6. Проверка backend](#6-проверка-backend)
-   [7. Запуск desktop-приложения](#7-запуск-desktop-приложения)
-   [8. Развёртывание backend на
    VPS/хостинге](#8-развёртывание-backend-на-vpsхостинге)
-   [9. Подключение desktop-приложения к удалённому
    серверу](#9-подключение-desktop-приложения-к-удалённому-серверу)
-   [10. Сборка Windows EXE](#10-сборка-windows-exe)
-   [11. Структура проекта](#11-структура-проекта)
-   [12. Полезные команды Docker](#12-полезные-команды-docker)
-   [13. Устранение неполадок](#13-устранение-неполадок)
-   [14. Важные ограничения текущей
    версии](#14-важные-ограничения-текущей-версии)

------------------------------------------------------------------------

## 1. Как устроен запуск

Проект состоит из трёх основных частей:

1.  **Desktop-клиент** --- графическое приложение на PySide6.
    Запускается на Windows-компьютере пользователя.
2.  **Backend API** --- приложение FastAPI. Получает запросы от
    desktop-клиента, обращается к AUTO.RIA API и OpenAI, сохраняет
    историю.
3.  **PostgreSQL** --- база данных, в которой хранятся поисковые
    запросы, найденные автомобили и AI-анализ.

Общая схема:

``` text
┌─────────────────────────────┐
│ Windows Desktop Application │
│ PySide6 + PyQt-Fluent-Widgets│
└──────────────┬──────────────┘
               │ HTTP(S) + Bearer token
               ▼
┌─────────────────────────────┐
│ FastAPI Backend             │
│ Docker container            │
└───────┬───────────┬─────────┘
        │           │
        ▼           ▼
┌──────────────┐  ┌────────────────┐
│ PostgreSQL   │  │ External APIs  │
│ Docker       │  │ AUTO.RIA       │
│ volume       │  │ OpenAI         │
└──────────────┘  └────────────────┘
```

### Что размещается на хостинге

На VPS/сервере размещаются:

-   backend из папки `backend/`;
-   `Dockerfile_backend`;
-   `docker-compose.yml`;
-   `requirements-backend.txt`;
-   серверный `.env`, созданный непосредственно на сервере;
-   Docker volume PostgreSQL.

На компьютере пользователя остаётся:

-   исходный desktop-клиент или собранная папка `dist/Pet_Parsing_AI/`;
-   клиентский `.env` с адресом backend и токеном;
-   Windows и необходимые системные компоненты.

**Загружать графический интерфейс на обычный веб-хостинг не нужно.** Это
не браузерное приложение. На сервере работает API, а графический
интерфейс запускается локально на Windows.

------------------------------------------------------------------------

## 2. Что нужно установить

### Для локальной разработки на Windows

-   Windows 10/11;
-   Python 3.14.x --- Dockerfile backend использует `python:3.14-slim`;
-   Git;
-   Docker Desktop с Docker Compose;
-   доступ к AUTO.RIA API;
-   API-ключ OpenAI для AI-анализа.

Проверка установленных инструментов:

``` powershell
python --version
git --version
docker --version
docker compose version
```

Docker Desktop должен быть запущен до запуска backend.

### Для удалённого сервера

Для VPS рекомендуется Linux-сервер с:

-   Docker Engine;
-   Docker Compose plugin;
-   доступом к интернету для обращений к AUTO.RIA и OpenAI;
-   доменом для API;
-   HTTPS-сертификатом и reverse proxy (например, Nginx или Caddy).

Конкретный VPS-провайдер проектом не задан. Подойдёт сервер, на котором
разрешено запускать Docker-контейнеры.

------------------------------------------------------------------------

## 3. Настройка переменных окружения

В корне проекта находится `.env.example`. На его основе нужно создать
настоящий `.env`.

### 3.1. Создание `.env` в PowerShell

Из корневой папки проекта:

``` powershell
Copy-Item .env.example .env
```

Открой `.env` и заполни его. Для локального запуска на одном компьютере
используется следующий набор:

``` dotenv
# AUTO.RIA API
AUTO_RIA_API=your_auto_ria_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-6.1-terra

# Backend authentication
BACKEND_API_TOKEN=replace_with_a_long_random_secret

# Desktop client -> backend URL
BACKEND_BASE_URL=http://127.0.0.1:8000

# PostgreSQL
POSTGRES_PASSWORD=replace_with_a_strong_database_password
POSTGRES_USER=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=pet_parsing_ai
```

**Важно:** в архиве `.env.example` содержит настройки AUTO.RIA, OpenAI и
PostgreSQL, но не содержит `BACKEND_API_TOKEN` и `BACKEND_BASE_URL`. Эти
две строки нужно добавить вручную. Без `BACKEND_API_TOKEN` backend
отклоняет запросы, а клиент не сможет авторизоваться.

### 3.2. Генерация токена backend

В PowerShell можно создать случайный токен командой:

``` powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Скопируй полученное значение в `BACKEND_API_TOKEN`.

Один и тот же токен должен быть указан:

-   в `.env` backend;
-   в клиентском `.env`, который использует desktop-приложение.

Не используй короткий или легко угадываемый токен.

### 3.3. Назначение переменных

  -----------------------------------------------------------------------
  Переменная              Где используется        Назначение
  ----------------------- ----------------------- -----------------------
  `AUTO_RIA_API`          Backend                 Ключ доступа к AUTO.RIA
                                                  API

  `OPENAI_API_KEY`        Backend                 Ключ доступа к OpenAI
                                                  API

  `OPENAI_MODEL`          Backend                 Идентификатор модели
                                                  для AI-анализа

  `BACKEND_API_TOKEN`     Backend и               Общий Bearer-токен для
                          desktop-клиент          доступа к API

  `BACKEND_BASE_URL`      Desktop-клиент          Адрес FastAPI backend

  `POSTGRES_PASSWORD`     Backend и Docker        Пароль PostgreSQL
                          Compose                 

  `POSTGRES_USER`         Backend / PostgreSQL    Пользователь базы
                                                  данных

  `POSTGRES_HOST`         Backend                 В Docker Compose
                                                  используется `db`

  `POSTGRES_PORT`         Backend                 Внутренний порт
                                                  PostgreSQL, обычно
                                                  `5432`

  `POSTGRES_DB`           Backend / PostgreSQL    Имя базы данных
  -----------------------------------------------------------------------

В текущем `docker-compose.yml` имя сервиса PostgreSQL --- `db`. Поэтому
backend внутри Docker обращается к базе по адресу `db:5432`. Порт
PostgreSQL наружу не опубликован.

### 3.4. Безопасность `.env`

-   Не отправляй `.env` в GitHub.
-   Не вставляй реальные ключи в README, исходный код или скриншоты.
-   На сервере создавай `.env` непосредственно в папке проекта.
-   Перед публикацией проверь `git status` и убедись, что `.env` не
    отслеживается Git.

------------------------------------------------------------------------

## 4. Локальный запуск на одном компьютере

Этот вариант подходит для разработки и проверки, когда
desktop-приложение, backend и PostgreSQL работают на одном компьютере.

### Шаг 1. Получить проект

Если репозиторий находится на GitHub и нужная версия находится в ветке
`client-server`:

``` powershell
git clone -b client-server <URL_РЕПОЗИТОРИЯ> Pet_Parsing_AI
cd Pet_Parsing_AI
```

Если репозиторий уже скачан, перейди в его корневую папку:

``` powershell
cd E:\Pet_Parsing_AI
```

### Шаг 2. Создать и заполнить `.env`

Выполни инструкции из раздела [3. Настройка переменных
окружения](#3-настройка-переменных-окружения).

До запуска Docker должны быть заполнены как минимум:

-   `AUTO_RIA_API`;
-   `OPENAI_API_KEY`;
-   `BACKEND_API_TOKEN`;
-   `POSTGRES_PASSWORD`.

### Шаг 3. Запустить Docker Desktop

Открой Docker Desktop и дождись состояния, при котором Docker Engine
запущен.

### Шаг 4. Собрать и запустить backend и PostgreSQL

Из корня проекта:

``` powershell
docker compose up -d --build
```

Команда:

-   собирает Docker-образ backend по `Dockerfile_backend`;
-   запускает контейнер PostgreSQL `pet_parsing_ai_db`;
-   запускает контейнер backend `pet_parsing_ai_backend`;
-   создаёт Docker volume `postgres_data` для хранения данных
    PostgreSQL.

Проверить контейнеры:

``` powershell
docker compose ps
```

Посмотреть логи backend:

``` powershell
docker compose logs -f backend
```

Посмотреть логи PostgreSQL:

``` powershell
docker compose logs -f db
```

Остановить просмотр логов можно сочетанием `Ctrl+C`. Это не
останавливает контейнеры.

------------------------------------------------------------------------

## 5. Первый запуск и создание таблиц БД

**Важный шаг для чистой базы данных.**

В текущем архиве нет Alembic-миграций и нет автоматического вызова
`Base.metadata.create_all()` при старте FastAPI. Поэтому на новом Docker
volume PostgreSQL база создаётся, но таблицы приложения автоматически не
появляются.

После запуска контейнеров один раз выполни:

``` powershell
docker compose exec backend python -c "import backend.models; from backend.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

Команда импортирует модели `Search` и `SearchCar`, а затем создаёт
отсутствующие таблицы:

-   `searches`;
-   `search_cars`.

Повторный запуск команды не удаляет существующие таблицы и записи.

> Сейчас это способ первоначальной инициализации схемы. Для дальнейшего
> развития проекта рекомендуется добавить Alembic и хранить изменения
> структуры БД в миграциях.

### Важно о сохранности базы

В `docker-compose.yml` настроен именованный volume `postgres_data`. Он
сохраняет данные PostgreSQL между обычными перезапусками контейнеров.

Не выполняй:

``` powershell
docker compose down -v
```

если нужно сохранить базу. Флаг `-v` удаляет volumes, включая
`postgres_data`.

Обычная остановка:

``` powershell
docker compose down
```

не удаляет именованный volume.

------------------------------------------------------------------------

## 6. Проверка backend

В текущей версии все маршруты FastAPI защищены зависимостью
`verify_api_token`. Поэтому даже health-check нужно вызывать с
Bearer-токеном.

В PowerShell укажи тот же токен, который записан в `.env`:

``` powershell
$TOKEN = "твой_BACKEND_API_TOKEN"
```

Проверка backend:

``` powershell
curl.exe -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/health
```

Ожидаемый ответ:

``` json
{"status":"ok"}
```

Проверка соединения с PostgreSQL:

``` powershell
curl.exe -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/health/db
```

Ожидаемый ответ:

``` json
{"database":"ok"}
```

Если обе проверки успешны, backend запущен и может подключаться к базе.

### Основные API-маршруты

Все перечисленные маршруты требуют заголовок:

``` http
Authorization: Bearer <BACKEND_API_TOKEN>
```

  -------------------------------------------------------------------------------------
  Метод                   Маршрут                               Назначение
  ----------------------- ------------------------------------- -----------------------
  `GET`                   `/health`                             Проверка доступности
                                                                backend

  `GET`                   `/health/db`                          Проверка соединения с
                                                                PostgreSQL

  `GET`                   `/dictionaries/marks`                 Получение марок
                                                                автомобилей

  `GET`                   `/dictionaries/models?brand_id=...`   Получение моделей
                                                                выбранной марки

  `GET`                   `/dictionaries/fuel-types`            Получение типов топлива

  `GET`                   `/dictionaries/gearboxes`             Получение коробок
                                                                передач

  `GET`                   `/dictionaries/drive-types`           Получение типов привода

  `POST`                  `/searches/`                          Запуск поиска и анализа
                                                                автомобилей

  `GET`                   `/history/`                           Получение истории
                                                                поисков

  `GET`                   `/history/{search_id}`                Получение подробностей
                                                                поиска
  -------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 7. Запуск desktop-приложения

Backend должен быть запущен и успешно проходить проверки из предыдущего
раздела.

### Шаг 1. Создать виртуальное окружение

Открой второе окно PowerShell в корне проекта:

``` powershell
python -m venv .venv
```

### Шаг 2. Активировать окружение

``` powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скрипта активации, для текущего окна
можно выполнить:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Затем повторить активацию.

### Шаг 3. Установить зависимости

``` powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` включает библиотеки desktop-интерфейса и
backend-клиента.

### Шаг 4. Проверить настройки клиента

Для локального запуска в `.env` должны быть:

``` dotenv
BACKEND_BASE_URL=http://127.0.0.1:8000
BACKEND_API_TOKEN=тот_же_токен_что_и_у_backend
```

### Шаг 5. Запустить приложение

``` powershell
python -m app.ui.main_window
```

Откроется окно **AUTO.RIA Analyzer**.

------------------------------------------------------------------------

## 8. Развёртывание backend на VPS/хостинге

Этот раздел описывает размещение backend и PostgreSQL на отдельном
Linux-сервере. Desktop-приложение при этом продолжает работать на
Windows-компьютере пользователя.

### 8.1. Что нужно загрузить на сервер

Самый простой вариант --- клонировать на VPS весь репозиторий нужной
ветки:

``` bash
git clone -b client-server <URL_РЕПОЗИТОРИЯ> Pet_Parsing_AI
cd Pet_Parsing_AI
```

Полный корень проекта нужен текущей сборке Docker, потому что
`Dockerfile_backend` использует `COPY . .`.

На сервер не нужно переносить:

-   `.env` с компьютера разработчика;
-   `.venv/`;
-   `build/` и `dist/`;
-   `__pycache__/`;
-   `*.pyc`;
-   локальные логи;
-   резервные дампы БД, если они не предназначены для восстановления на
    сервере.

### 8.2. Создать серверный `.env`

Создай файл `.env` непосредственно на VPS:

``` bash
nano .env
```

Пример серверной конфигурации:

``` dotenv
AUTO_RIA_API=your_auto_ria_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-6.1-terra

BACKEND_API_TOKEN=replace_with_a_long_random_secret

POSTGRES_PASSWORD=replace_with_a_strong_database_password
POSTGRES_USER=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=pet_parsing_ai
```

На сервере `BACKEND_BASE_URL` backend-процессу не требуется: это
настройка desktop-клиента.

Сгенерируй отдельный длинный `BACKEND_API_TOKEN` и сохрани его --- он
понадобится клиенту.

### 8.3. Запустить серверные контейнеры

``` bash
docker compose up -d --build
```

Проверить состояние:

``` bash
docker compose ps
```

Посмотреть логи:

``` bash
docker compose logs -f backend
docker compose logs -f db
```

### 8.4. Создать таблицы базы данных

Для новой базы выполни один раз:

``` bash
docker compose exec backend python -c "import backend.models; from backend.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 8.5. Настроить внешний доступ

Текущий Compose публикует backend так:

``` yaml
ports:
  - "127.0.0.1:8000:8000"
```

Это означает, что порт `8000` доступен только локально на самом сервере.
Это намеренно не открывает FastAPI напрямую всему интернету.

Для удалённого desktop-клиента настрой reverse proxy:

``` text
Desktop application
        |
        | HTTPS :443
        v
Domain / Nginx or Caddy
        |
        | HTTP to 127.0.0.1:8000
        v
FastAPI container
```

Нужно:

1.  Привязать домен к IP VPS.
2.  Настроить Nginx или Caddy.
3.  Выпустить и подключить TLS-сертификат.
4.  Направить запросы домена на `http://127.0.0.1:8000`.
5.  Разрешить входящие подключения к `443` (и `80`, если он нужен для
    получения/обновления сертификата).
6.  Не публиковать PostgreSQL в интернет.
7.  Не открывать порт `8000` наружу, если используется reverse proxy.

Поиск может выполняться долго: desktop-клиент задаёт тайм-аут до 600
секунд. Поэтому в reverse proxy нужно установить тайм-аут ожидания
ответа не меньше 600 секунд, например 650 секунд.

В репозитории нет готовой конфигурации Nginx/Caddy и TLS-сертификата ---
их нужно настроить отдельно на выбранном сервере.

------------------------------------------------------------------------

## 9. Подключение desktop-приложения к удалённому серверу

На компьютере, где запускается GUI, в клиентском `.env` укажи:

``` dotenv
BACKEND_BASE_URL=https://api.example.com
BACKEND_API_TOKEN=тот_же_токен_что_на_сервере
```

Замени `api.example.com` на свой домен.

Не используй `127.0.0.1` или `localhost` для удалённого backend: на
компьютере пользователя эти адреса указывают на его собственный
компьютер, а не на VPS.

Для удалённого подключения клиенту не нужны:

-   `AUTO_RIA_API`;
-   `OPENAI_API_KEY`;
-   `POSTGRES_PASSWORD`;
-   доступ к PostgreSQL.

Эти секреты должны оставаться на сервере. Клиенту нужны только адрес
backend и токен доступа.

### Важное ограничение авторизации

Сейчас проект использует общий статический `BACKEND_API_TOKEN`, который
хранится в `.env` клиента. В собранном EXE такой токен можно извлечь.

Поэтому текущая схема подходит для личного использования или
ограниченного доверенного окружения, но **не является полноценной
пользовательской авторизацией для публичного распространения
приложения**. Перед выдачей EXE широкому кругу пользователей следует
внедрить индивидуальную авторизацию, управление пользователями и
токенами.

------------------------------------------------------------------------

## 10. Сборка Windows EXE

В проекте есть PowerShell-сборщик:

-   `build_pet_parsing_ai.ps1`;
-   `BUILD_AUTO_RIA_ANALYZER.bat`;
-   `load_env_runtime_hook.py`;
-   `AUTO_RIA_Analyzer.ico`.

Сборка выполняется на Windows.

### Требования

-   создано виртуальное окружение `.venv`;
-   установлены зависимости из `requirements.txt`;
-   в корне есть `.env`;
-   присутствуют `app/ui/assets/` и все шесть файлов ресурсов;
-   присутствует `AUTO_RIA_Analyzer.ico`.

### Запуск сборки

Дважды щёлкни:

``` text
BUILD_AUTO_RIA_ANALYZER.bat
```

Или через PowerShell:

``` powershell
.\build_pet_parsing_ai.ps1
```

Скрипт использует Python из `.venv`, при необходимости устанавливает
PyInstaller, собирает приложение в режиме `--onedir`, переносит ресурсы
и создаёт ярлык на рабочем столе.

Результат:

``` text
dist/
└── Pet_Parsing_AI/
    ├── Pet_Parsing_AI.exe
    ├── _internal/
    ├── .env
    └── ...
```

Запускаемый файл:

``` text
dist\Pet_Parsing_AI\Pet_Parsing_AI.exe
```

**Передавай всю папку `dist/Pet_Parsing_AI`, а не один EXE:** при сборке
`--onedir` рядом с исполняемым файлом находятся необходимые библиотеки и
ресурсы.

### Важное предупреждение о `.env` в EXE

Текущий `build_pet_parsing_ai.ps1` копирует исходный `.env` целиком, без
изменений, в папку сборки и проверяет копии по SHA256.

Это означает, что если в исходном `.env` есть `AUTO_RIA_API`,
`OPENAI_API_KEY` и пароль PostgreSQL, они тоже попадут в папку EXE.

-   Не публикуй такую сборку в открытом доступе.
-   Не отправляй её посторонним.
-   Для клиента, подключающегося к удалённому серверу, используй
    отдельный клиентский `.env`, содержащий только `BACKEND_BASE_URL` и
    `BACKEND_API_TOKEN`.
-   Серверный `.env` должен оставаться только на VPS.

Даже клиентский Bearer-токен можно извлечь из приложения. Для публичного
распространения нужен другой механизм авторизации.

Подробности сборщика находятся в [README_EXE.md](README_EXE.md).

------------------------------------------------------------------------

## 11. Структура проекта

``` text
Pet_Parsing_AI/
│
├── app/
│   ├── localization.py
│   └── ui/
│       ├── assets/
│       ├── combustion_page.py
│       ├── electric_page.py
│       ├── history_page.py
│       ├── home_page.py
│       ├── main_window.py
│       ├── results_page.py
│       ├── search_worker.py
│       ├── theme_dialog.py
│       └── theme_manager.py
│
├── backend/
│   ├── entities/
│   ├── integrations/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── security.py
│
├── backend_client.py
├── Dockerfile_backend
├── docker-compose.yml
├── requirements.txt
├── requirements-backend.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── build_pet_parsing_ai.ps1
├── BUILD_AUTO_RIA_ANALYZER.bat
├── load_env_runtime_hook.py
├── AUTO_RIA_Analyzer.ico
├── README.md
└── README_EXE.md
```

Подробное описание каждого модуля, архитектуры и технологий находится в
отдельном HTML-документе проекта.

------------------------------------------------------------------------

## 12. Полезные команды Docker

Запустить и пересобрать сервисы:

``` powershell
docker compose up -d --build
```

Остановить контейнеры, сохранив данные БД:

``` powershell
docker compose down
```

Показать состояние:

``` powershell
docker compose ps
```

Логи backend:

``` powershell
docker compose logs -f backend
```

Логи PostgreSQL:

``` powershell
docker compose logs -f db
```

Перезапустить только backend:

``` powershell
docker compose restart backend
```

Открыть shell в backend:

``` powershell
docker compose exec backend sh
```

Открыть PostgreSQL CLI:

``` powershell
docker compose exec db psql -U postgres -d pet_parsing_ai
```

**Не используй `docker compose down -v`, если нужно сохранить базу
данных.**

------------------------------------------------------------------------

## 13. Устранение неполадок

### Backend не запускается: не задан AUTO_RIA_API

Проверь, что в корневом `.env` есть:

``` dotenv
AUTO_RIA_API=твой_ключ
```

Интеграция AUTO.RIA читает ключ при импорте backend-модуля, поэтому без
него backend может завершиться при старте.

### Ответ `503 API authentication is not configured`

В `.env` не задан `BACKEND_API_TOKEN` или он не попал в окружение
контейнера.

После изменения `.env` пересоздай backend:

``` powershell
docker compose up -d --force-recreate backend
```

### Ответ `401 Invalid or missing API token`

Проверь, что `BACKEND_API_TOKEN` в desktop-клиенте полностью совпадает с
токеном backend.

### Backend не подключается к PostgreSQL

Проверь:

-   контейнер `db` запущен и healthy;
-   `POSTGRES_PASSWORD` одинаково используется при первоначальной
    настройке БД и backend;
-   внутри Compose `POSTGRES_HOST` равен `db`;
-   порт PostgreSQL --- `5432`.

Логи:

``` powershell
docker compose logs db
docker compose logs backend
```

### Ошибка `relation "searches" does not exist`

Таблицы ещё не созданы. Выполни команду инициализации из раздела
[5](#5-первый-запуск-и-создание-таблиц-бд).

### Desktop-клиент не подключается к backend

Проверь `BACKEND_BASE_URL`.

Локально:

``` dotenv
BACKEND_BASE_URL=http://127.0.0.1:8000
```

На удалённом сервере:

``` dotenv
BACKEND_BASE_URL=https://api.example.com
```

Также проверь, что backend запущен, reverse proxy работает и токен
совпадает.

### Ошибка 502/504 при поиске через домен

Поиск может занимать несколько минут. Проверь тайм-ауты reverse proxy:
они должны быть больше времени ожидания клиента (до 600 секунд).

### Не отображаются фоновые изображения

Проверь наличие ресурсов:

``` text
app/ui/assets/muscle_car.png
app/ui/assets/background1.jpg
app/ui/assets/background2.jpg
app/ui/assets/background3.jpg
app/ui/assets/background4.jpg
app/ui/assets/background5.jpg
```

Для EXE запускай сборщик из полного проекта: он проверяет и копирует эти
файлы.

------------------------------------------------------------------------

## 14. Важные ограничения текущей версии

1.  **Нет Alembic-миграций.** Для первой установки таблицы создаются
    вручную командой SQLAlchemy из раздела 5.
2.  **Нет готового reverse proxy.** Для публичного удалённого доступа
    самостоятельно настрой домен, HTTPS и Nginx/Caddy.
3.  **Используется общий Bearer-токен.** Это не система пользователей и
    ролей. Токен, находящийся в desktop-клиенте, можно извлечь.
4.  **Сборщик EXE копирует весь `.env`.** Не передавай сборку, если в
    этом файле есть серверные секреты.
5.  **Файлы JSON/TXT сохраняются в `search/` внутри
    backend-контейнера.** В текущем `docker-compose.yml` эта папка не
    подключена как отдельный volume. Если нужно сохранять эти файлы
    между пересозданиями backend-контейнера, добавь volume
    `./search:/app/search` в сервис `backend`.
6.  **PostgreSQL хранит данные в `postgres_data`.** Не удаляй volume при
    обычном обновлении приложения.
7.  **В проекте нет отдельного веб-интерфейса.** На хостинг отправляется
    backend, а desktop GUI запускается на Windows.
