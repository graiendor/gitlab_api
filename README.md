# gitlab_api
Консольное приложение для работы с гитлабом: добавление и удаление пользователей

Создано для упрощения администрирования гитлаба, обработки множественных пользователей.
## Запуск

```python3 main.py```

## Использование

1. С помощью комманд добавить ссылку на нужный гитлаб.

    Он будет храниться в локальной базе данных вместе с токеном.
2. Далее в выбранном инструменте возможно исполнить следующие функции:
   1. Добавление пользователей (вручную/из таблицы)
   2. Удаление пользователей (вручную/из логов[пока не реализовано])
   3. Блокировка пользователей
