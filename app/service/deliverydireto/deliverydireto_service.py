import os
import requests
from copy import deepcopy
from urllib.request import urlopen


class DeliveryDiretoService:
    def __init__(self):
        self.base_url = os.environ.get("APP_DELIVERYDIRETO_URL")
        self.authentication_body = {
            "grant_type": "password",
            "client_id": os.environ.get('APP_DELIVERYDIRETO_CLIENT_ID'),
            "client_secret": os.environ.get('APP_DELIVERYDIRETO_CLIENT_SECRET'),
            "username": os.environ.get('APP_DELIVERYDIRETO_ADMIN_USERNAME'),
            "password": os.environ.get('APP_DELIVERYDIRETO_ADMIN_PASSWORD')
        }
        self.headers = {
            "X-DeliveryDireto-ID": os.environ.get('APP_DELIVERYDIRETO_X_ID'),
            "X-DeliveryDireto-Client-Id": os.environ.get('APP_DELIVERYDIRETO_CLIENT_ID')
        }

        self.auth()

    def auth(self):
        print("Starting authentication with Delivery Direto.")
        response = requests.post(f"{self.base_url}/admin-api/token",
                                 headers=self.headers,
                                 data=self.authentication_body)
        data = response.json()
        self.headers['Authorization'] = f"Bearer {data['access_token']}"
        self.headers['Content-Type'] = "application/json"
        print("Authenticated with Delivery Direto.")

    def get_all_categories(self):
        categories = []
        offset = 0
        base_url_list_categories = f"{self.base_url}/admin-api/v1/catalog/categories?offset={offset}&limit=1"

        response = requests.get(base_url_list_categories, headers=self.headers)
        data = response.json()['data']
        categories.extend(data['categories'])

        end = data['pagination']['totalItems']
        for offset in range(1, end):
            url_categories_paginated = f"{self.base_url}/admin-api/v1/catalog/categories?offset={offset}&limit=1"
            response = requests.get(url_categories_paginated, headers=self.headers)
            data = response.json()['data']

            if len(data['categories']) == 0:
                break

            categories.extend(data['categories'])

        return categories

    def create_category(self, category_name):
        base_url_create_category = f"{self.base_url}/admin-api/v1/catalog/categories"
        data = {
            "name": category_name,
            "description": "",
            "status": "ACTIVE",
            "showOnMobile": True,
            "hiddenWhenUnavailable": True,
            "showOnlyImage": True,
            "viewOrder": 1,
        }

        response = requests.post(base_url_create_category, headers=self.headers, json=data)
        if response.json()["status"] == "success":
            print(f"Category [{category_name}] created at Delivery Direto.")

    def create_categories(self, categories_from_source):
        existing_categories = [product['name'] for product in self.get_all_categories()]
        not_existing_categories = list(set(categories_from_source) - set(existing_categories))

        for not_existing_category in not_existing_categories:
            self.create_category(not_existing_category.capitalize())

    def create_image(self, item_id, image_url):
        base_url_add_image = f"{self.base_url}/admin-api/v1/catalog/items/{item_id}/image"
        headers = deepcopy(self.headers)
        headers["Content-Type"] = "multipart/form-data"

        image_data = {"file": urlopen(image_url).read()}

        response = requests.post(base_url_add_image, headers=headers, files=image_data)
        print(response.text)

    def create_product(self, product_from_source, category_id):
        base_url_create_item = f"{self.base_url}/admin-api/v1/catalog/categories/{category_id}/items"
        print(f"Creating product [{product_from_source['nome']}] at Delivery Direto.")

        status_value = "ACTIVE"
        if not product_from_source["ativo"]: status_value = "SHORT_SUPPLY"

        product_data = {
            "name": product_from_source["nome"],
            "price": {
                "value": int(product_from_source["preco"] * 100),
                "currency": "BRL"
            },
            "type": "CUSTOM",
            "status": status_value,
            "showAtCheckout": True,
            "customCode": product_from_source["id"],
            "description": "",
            "hiddenWhenUnavailable": True,
            "viewOrder": 1,
            "isFractional": 1
        }

        response = requests.post(base_url_create_item, headers=self.headers, json=product_data)
        data_response = response.json()
        if data_response["status"] == "success":
            print(f"Product [{product_from_source['nome']}] created at Delivery Direto.")

            # if product_from_source["imagem"]:
            #     self.create_image(data_response["data"]["id"], product_from_source["imagem"])

    def get_products_by_category(self, category_id):
        offset = 0
        products = []
        base_url_products = f"{self.base_url}/admin-api/v1/catalog/categories/{category_id}/items?offset={offset}&limit=10"

        response = requests.get(base_url_products, headers=self.headers)
        data = response.json()['data']
        products.extend(data['items'])

        end = data['pagination']['totalItems']
        for offset in range(1, end):
            url_categories_paginated = f"{self.base_url}/admin-api/v1/catalog/categories/{category_id}/items?offset={offset}&limit=10"
            response = requests.get(url_categories_paginated, headers=self.headers)
            data = response.json()['data']

            if len(data['items']) == 0:
                break

            products.extend(data['items'])

        return products

    def update_product(self, existing_product, product_from_source):
        base_url_update_item = f"{self.base_url}/admin-api/v1/catalog/items/{existing_product['id']}"
        print(f"Updating product [{product_from_source['nome']}] at Delivery Direto.")

        status_value = "ACTIVE"
        if not product_from_source["ativo"]: status_value = "SHORT_SUPPLY"

        product_data = {
            "name": product_from_source["nome"],
            "price": {
                "value": int(product_from_source["preco"] * 100),
                "currency": "BRL"
            },
            "type": "CUSTOM",
            "status": status_value,
            "showAtCheckout": True,
            "customCode": product_from_source["id"],
            "description": "",
            "hiddenWhenUnavailable": True,
            "viewOrder": 1,
            "isFractional": 1
        }

        response = requests.put(base_url_update_item, headers=self.headers, json=product_data)
        data_response = response.json()
        if data_response["status"] == "success":
            print(f"Product [{product_from_source['nome']}] updated at Delivery Direto.")

    def create_products(self, products_from_source):
        all_categories = self.get_all_categories()
        all_products = []
        for category in all_categories:
            all_products.extend(self.get_products_by_category(category["id"]))

        for product in products_from_source:
            category = next((c for c in all_categories if c["name"] == product["categoria"].capitalize()), None)
            existing_product = next((p for p in all_products if p["customCode"] == product["id"]), None)
            if not existing_product:
                self.create_product(product, category["id"])
            else:
                self.update_product(existing_product, product)
