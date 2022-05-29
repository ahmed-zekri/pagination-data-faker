import json

import names
from faker import Faker
from faker_vehicle import VehicleProvider
from flask import Flask, render_template, Response, request
from flask_paginate import Pagination, get_page_args
from pathlib import Path

app = Flask(__name__)
app.template_folder = ''


def generate_users() -> list:
    users = list()
    user_size = 500000
    percentage = 0
    file_name = "users.txt"

    if Path(file_name).exists():
        with open(file=file_name, mode='r') as f:
            users = f.readlines()
            users.sort()
            users = list(map(lambda x: x.replace('\n', ''), users))
    else:
        with open(file=file_name, mode='a') as f:
            for i in range(user_size):
                if int((i * 100) / user_size) != percentage:
                    percentage = int((i * 100) / user_size)
                    print(percentage)
                name = names.get_full_name()
                users.append(name)
                f.write(f'{name}\n')
    return users


def generate_car_brand():
    fake = Faker()
    fake.add_provider(VehicleProvider)

    fake.vehicle_year_make_model()
    # 2014 Volkswagen Golf
    fake.vehicle_year_make_model_cat()
    # 1996 Dodge Ram Wagon 1500 (Van/Minivan)
    fake.vehicle_make_model()
    # Volvo V40
    fake.vehicle_make()
    # BMW
    fake.vehicle_model()
    # SL
    fake.vehicle_year()
    # 2008
    fake.vehicle_category()
    # Wagon
    json.dumps(fake.vehicle_object())
    return fake.vehicle_object()


def generate_car_brands() -> list:
    car_brands = list()
    vehicle_size = 500000
    percentage = 0
    file_name = "cars.txt"

    if Path(file_name).exists():
        with open(file=file_name, mode='r') as f:
            car_brands = f.readlines()
            car_brands.sort()
            car_brands = list(map(lambda x: json.loads(x.replace('\n', '')), car_brands))
    else:
        with open(file=file_name, mode='a') as f:
            for i in range(vehicle_size):
                if int((i * 100) / vehicle_size) != percentage:
                    percentage = int((i * 100) / vehicle_size)
                    print(percentage)
                vehicle = generate_car_brand()
                car_brands.append(vehicle)
                f.write(f'{json.dumps(vehicle)}\n')
    return car_brands


def get_users(users, offset=0, per_page=10, search_term=None):
    return users[offset: offset + per_page] if not search_term else list(
        filter(lambda user: search_term in user, users))[offset: offset + per_page]


@app.route('/')
def index():
    data = generate_users() if request.args.get('data') == 'user' else generate_car_brands()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(data)
    pagination_users = get_users(data, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return Response(json.dumps(pagination_users), mimetype='application/json') if request.args.get(
        'ui') is None else render_template('index.html',
                                           users=pagination_users,
                                           page=page,
                                           per_page=per_page,
                                           pagination=pagination,
                                           )


@app.route('/search')
def search():
    users = generate_users()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(users)
    search_term = request.args.get('search_term')
    pagination_users = get_users(users, offset=offset, per_page=per_page, search_term=search_term)

    return Response(json.dumps(pagination_users), mimetype='application/json')


@app.route('/all')
def all_users():
    users = generate_users()
    return Response(json.dumps(users), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
