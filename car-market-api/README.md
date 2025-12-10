# Car Market API

Учебный веб-сервис на Flask для предметной области «Рынок автомобилей».

## Функциональность

- Хранение информации об автомобилях:
  - id
  - brand (марка)
  - model (модель)
  - year (год выпуска)
  - price (цена)
  - mileage (пробег)
- Получение списка автомобилей с сортировкой по любому полю (`/cars?sort_by=...&order=asc|desc`)
- Получение одной записи по ID (`/cars/<id>`)
- Добавление автомобиля (`POST /cars`)
- Обновление автомобиля (`PUT /cars/<id>`)
- Удаление автомобиля (`DELETE /cars/<id>`)
- Статистика по числовым полям: min, max, avg (`/cars/stats`)
- Документация и тестирование API через Swagger UI (`/apidocs`)

## Установка и запуск

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
