# RBF CLAN BOT

Телеграм бот для подачи заявок на вступление в беседу клана RBF (PUBG Mobile). Данный проект призван упростить процесс подачи заявок, обеспечить администраторам удобный интерфейс для работы с заявками и улучшить общение между администраторами и пользователями.

## Используемые технологии

- Библиотека для работы с Telegram API - [python-telegram-bot](https://docs.python-telegram-bot.org/en/v21.0.1/)
- ORM для работы с базой данных - [SQLAlchemy](https://www.sqlalchemy.org/)
- Движок базы данных - [asyncpg](https://magicstack.github.io/asyncpg/current/)
- Библиотека для логирования - [loguru](https://loguru.readthedocs.io/en/stable/)

## Текущий функционал

- Пользователь может подать заявку на вступление в клан. Во время подачи производится валидация ответов на вопросы анкеты.
- Администраторы могут просматривать заявки и принимать/отклонять в них.
- Администраторы могут банить или снимать бан с пользователей.

## Технические улучшения

- [ ] Переписать приложение с использованием иной библиотеки для взаимодействия с telegram api.
- [ ] Использовать Pydantic для env переменных и валидации данных.
- [ ] Добавить обработку ошибок.
- [ ] Упаковать приложение в Docker контейнер.
- [ ] Переписать логирование с использованием стандартной библиотеки Python.
- [ ] Переписать репозитории и сервисы.
- [ ] Добавить тесты.
- [ ] Добавить CI/CD.

## Развитие функционала

- [ ] Добавить возможность админам вести чат с пользователем через бота.
- [x] Автоматически аннулировать пригласительные ссылки после их использования.
- [x] Добавить возможность админам банить пользователей.
- [ ] Добавить возможность снимать отказ с заявки.
- [ ] Добавить показ правил чата после принятия заявки.
- [x] Изменить взаимодействие админов с заявками в чате заявок. Теперь для работы с анкетой нужно "взять ее в обработку" и обработать в личных сообщениях.
- [ ] Добавить кнопку "Вернуть из обработки" для админов, если они по каким-то причинам не могут обработать заявку.
