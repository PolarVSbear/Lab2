from flask import Flask, jsonify, request
from flasgger import Swagger
from copy import deepcopy

app = Flask(__name__)

# Swagger базовый шаблон
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Car Market API",
        "description": "Простой веб-сервис для предметной области 'Рынок автомобилей'. "
                       "Поддерживает CRUD-операции, сортировку и статистику по числовым полям.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http"],
    "definitions": {
        "Car": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "brand": {"type": "string", "example": "Toyota"},
                "model": {"type": "string", "example": "Corolla"},
                "year": {"type": "integer", "example": 2018},
                "price": {"type": "number", "format": "float", "example": 15000.0},
                "mileage": {"type": "integer", "example": 85000}
            },
            "required": ["brand", "model", "year", "price", "mileage"]
        }
    }
}

swagger = Swagger(app, template=swagger_template)

# "База данных" в памяти (для лабораторной этого достаточно)
cars = [
    {
        "id": 1,
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2015,
        "price": 9000.0,
        "mileage": 150000
    },
    {
        "id": 2,
        "brand": "BMW",
        "model": "320i",
        "year": 2018,
        "price": 20000.0,
        "mileage": 80000
    },
    {
        "id": 3,
        "brand": "Hyundai",
        "model": "Solaris",
        "year": 2019,
        "price": 11000.0,
        "mileage": 60000
    }
]

next_id = 4  # для генерации новых id


def find_car(car_id: int):
    """Поиск машины по id."""
    for car in cars:
        if car["id"] == car_id:
            return car
    return None


@app.route("/cars", methods=["GET"])
def get_cars():
    """
    Получить список автомобилей с возможностью сортировки.
    ---
    tags:
      - Cars
    parameters:
      - name: sort_by
        in: query
        type: string
        required: false
        description: Поле для сортировки.
        enum: [id, brand, model, year, price, mileage]
      - name: order
        in: query
        type: string
        required: false
        description: Порядок сортировки.
        enum: [asc, desc]
    responses:
      200:
        description: Список автомобилей.
        schema:
          type: array
          items:
            $ref: '#/definitions/Car'
    """
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    allowed_fields = ["id", "brand", "model", "year", "price", "mileage"]
    if sort_by not in allowed_fields:
        return jsonify({"error": f"Нельзя сортировать по полю '{sort_by}'"}), 400

    reverse = (order == "desc")
    result = sorted(cars, key=lambda x: x[sort_by], reverse=reverse)
    return jsonify(result)


@app.route("/cars/<int:car_id>", methods=["GET"])
def get_car(car_id):
    """
    Получить один автомобиль по ID.
    ---
    tags:
      - Cars
    parameters:
      - name: car_id
        in: path
        type: integer
        required: true
        description: Идентификатор автомобиля
    responses:
      200:
        description: Объект автомобиля
        schema:
          $ref: '#/definitions/Car'
      404:
        description: Автомобиль не найден
    """
    car = find_car(car_id)
    if car is None:
        return jsonify({"error": "Автомобиль не найден"}), 404
    return jsonify(car)


@app.route("/cars", methods=["POST"])
def add_car():
    """
    Добавить новый автомобиль.
    ---
    tags:
      - Cars
    parameters:
      - in: body
        name: body
        description: Данные автомобиля
        required: true
        schema:
          $ref: '#/definitions/Car'
    responses:
      201:
        description: Автомобиль успешно добавлен
        schema:
          $ref: '#/definitions/Car'
      400:
        description: Некорректные данные
    """
    global next_id

    data = request.get_json()
    if not data:
        return jsonify({"error": "Ожидается JSON тело запроса"}), 400

    required_fields = ["brand", "model", "year", "price", "mileage"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Поле '{field}' обязательно"}), 400

    try:
        new_car = {
            "id": next_id,
            "brand": str(data["brand"]),
            "model": str(data["model"]),
            "year": int(data["year"]),
            "price": float(data["price"]),
            "mileage": int(data["mileage"]),
        }
    except (ValueError, TypeError):
        return jsonify({"error": "Проверьте типы данных полей"}), 400

    cars.append(new_car)
    next_id += 1
    return jsonify(new_car), 201


@app.route("/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    """
    Обновить информацию об автомобиле по ID.
    ---
    tags:
      - Cars
    parameters:
      - name: car_id
        in: path
        type: integer
        required: true
        description: Идентификатор автомобиля
      - in: body
        name: body
        description: Новые данные автомобиля (полное или частичное обновление)
        required: true
        schema:
          $ref: '#/definitions/Car'
    responses:
      200:
        description: Обновлённый автомобиль
        schema:
          $ref: '#/definitions/Car'
      404:
        description: Автомобиль не найден
      400:
        description: Некорректные данные
    """
    car = find_car(car_id)
    if car is None:
        return jsonify({"error": "Автомобиль не найден"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Ожидается JSON тело запроса"}), 400

    updated_car = deepcopy(car)

    # Разрешаем частичное обновление
    if "brand" in data:
        updated_car["brand"] = str(data["brand"])
    if "model" in data:
        updated_car["model"] = str(data["model"])
    if "year" in data:
        try:
            updated_car["year"] = int(data["year"])
        except (ValueError, TypeError):
            return jsonify({"error": "Поле 'year' должно быть целым числом"}), 400
    if "price" in data:
        try:
            updated_car["price"] = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"error": "Поле 'price' должно быть числом"}), 400
    if "mileage" in data:
        try:
            updated_car["mileage"] = int(data["mileage"])
        except (ValueError, TypeError):
            return jsonify({"error": "Поле 'mileage' должно быть целым числом"}), 400

    # Сохраняем изменения
    car.clear()
    car.update(updated_car)

    return jsonify(car)


@app.route("/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    """
    Удалить автомобиль по ID.
    ---
    tags:
      - Cars
    parameters:
      - name: car_id
        in: path
        type: integer
        required: true
        description: Идентификатор автомобиля
    responses:
      200:
        description: Автомобиль удалён
      404:
        description: Автомобиль не найден
    """
    car = find_car(car_id)
    if car is None:
        return jsonify({"error": "Автомобиль не найден"}), 404

    cars.remove(car)
    return jsonify({"message": f"Автомобиль с id={car_id} удалён"})


@app.route("/cars/stats", methods=["GET"])
def get_stats():
    """
    Получить статистику по числовым полям (min, max, avg).
    ---
    tags:
      - Cars
    responses:
      200:
        description: Статистика по числовым полям
        schema:
          type: object
          properties:
            count:
              type: integer
              example: 3
            stats:
              type: object
              properties:
                year:
                  type: object
                  properties:
                    min: {"type": "integer", "example": 2010}
                    max: {"type": "integer", "example": 2020}
                    avg: {"type": "number", "format": "float", "example": 2016.7}
                price:
                  type: object
                  properties:
                    min: {"type": "number", "format": "float", "example": 5000.0}
                    max: {"type": "number", "format": "float", "example": 25000.0}
                    avg: {"type": "number", "format": "float", "example": 15000.0}
                mileage:
                  type: object
                  properties:
                    min: {"type": "integer", "example": 10000}
                    max: {"type": "integer", "example": 200000}
                    avg: {"type": "number", "format": "float", "example": 85000.0}
    """
    if not cars:
        return jsonify({"count": 0, "stats": {}})

    numeric_fields = ["year", "price", "mileage"]
    stats = {}

    for field in numeric_fields:
        values = [c[field] for c in cars]
        stats[field] = {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }

    return jsonify({"count": len(cars), "stats": stats})


if __name__ == "__main__":
    app.run(debug=True)
