### Тестовое задание
Вашей задачей в рамках этого тестового задания будет написание
алгоритма агрегации статистических данных о зарплатах
сотрудников компании по временным промежуткам. Ссылка на
скачивание коллекции со статистическими данными, которую
необходимо использовать при выполнении задания, находится в
конце документа.

Ваш алгоритм должен принимать на вход:
1. Дату и время старта агрегации в ISO формате (далее dt_from)
2. Дату и время окончания агрегации в ISO формате (далее dt_upto)
3. Тип агрегации (далее group_type). Типы агрегации могут быть
следующие: hour, day, month. То есть группировка всех данных
за час, день, неделю, месяц.


### Описание решения

Простой бот, который парсит входящий запрос, делает запрос к MongoDB
и возвращает результат. Агрегация данных полностью выполняется в
базе данных.

### Команды

- `make format` форматирование black и isort
- `make lint` проверка flake8
- `make dev-run` запуск бота на хосте (локально)