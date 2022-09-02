import requests
import os


class HiperService:
    def __init__(self):
        self.key = os.environ.get('APP_HIPER_KEY')
        self.headers = {'Authorization': None}
        self.auth()

    def auth(self):
        print("Starting authentication with Hiper.")
        base_url_token = '{}/api/v1/auth/gerar-token/{}'.format(os.environ.get('APP_HIPER_URL'), self.key)
        response = requests.get(base_url_token)
        data = response.json()

        self.headers['Authorization'] = f"Bearer {data['token']}"
        self.headers['Content-type'] = 'application/json'
        print("Authenticated with Hiper.")


    def register_order(self, order_data):
        print('Receiving new order, start sending to Hiper.')
        hiper_order = {}
        hiper_order['cliente'] = {}
        hiper_order['enderecoDeCobranca'] = {}
        hiper_order['enderecoDeEntrega'] = {}
        hiper_order['itens'] = {}

        customer_data = order_data["customer"]
        hiper_order['cliente']['documento'] = customer_data["document"].replace(".", "")
        hiper_order['cliente']['nomeDoCliente'] = f"{customer_data['firstName']} {customer_data['lastName']}"
        hiper_order['cliente']['email'] = customer_data["email"]
        hiper_order['cliente']['inscricaoEstadual'] = ''
        hiper_order['cliente']['nomeFantasia'] = ''

        address_data = order_data["address"]
        hiper_order['enderecoDeCobranca']['cep'] = address_data["zipcode"] if address_data["zipcode"] else '74290-040'
        hiper_order['enderecoDeCobranca']['codigoIbge'] = self.get_ibge_code(address_data["city"], address_data["state"])
        hiper_order['enderecoDeCobranca']['logradouro'] = address_data["street"]
        hiper_order['enderecoDeCobranca']['bairro'] = address_data["neighborhood"]
        hiper_order['enderecoDeCobranca']['numero'] = address_data["number"]
        hiper_order['enderecoDeCobranca']['complemento'] = address_data["complement"]

        hiper_order['enderecoDeEntrega']['cep'] = address_data["zipcode"] if address_data["zipcode"] else '74290-040'
        hiper_order['enderecoDeEntrega']['codigoIbge'] = self.get_ibge_code(address_data["city"], address_data["state"])
        hiper_order['enderecoDeEntrega']['logradouro'] = address_data["street"]
        hiper_order['enderecoDeEntrega']['bairro'] = address_data["neighborhood"]
        hiper_order['enderecoDeEntrega']['numero'] = address_data["number"]
        hiper_order['enderecoDeEntrega']['complemento'] = address_data["complement"]

        hiper_order['itens'] = self.parse_all_products(order_data["items"])

        hiper_order['meiosDePagamento'] = [{ 'idMeioDePagamento': 1, 'parcelas': 1, 'valor': self.get_total_price(hiper_order['itens']) }]
        hiper_order['numeroPedidoDeVenda'] = ''
        hiper_order['observacaoDoPedidoDeVenda'] = ''
        hiper_order['valorDoFrete'] = 0.0

        print(hiper_order)

        base_url_order = f'{os.environ.get("APP_HIPER_URL")}/api/v1/pedido-de-venda'
        response = requests.post(base_url_order, headers=self.headers, json=hiper_order)
        print('Status code: {}'.format(response.status_code))
        print('Response: {}'.format(response.text))

    def parse_all_products(self, items):
        products = []
        for item in items:
            produto = {}
            produto['produtoId'] = item['customCode']
            produto['quantidade'] = item['amount']
            produto['precoUnitarioBruto'] = float((item["price"]["value"] / 100))
            produto['precoUnitarioLiquido'] = float((item["price"]["value"] / 100))
            products.append(produto)

        return products

    def get_ibge_code(self, city, uf):
        codigo = 0
        codigos_distritos = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/distritos').json()
        for cod_distrito in codigos_distritos:
            if cod_distrito['municipio']['nome'].lower() == city.lower():
                codigo = cod_distrito['municipio']['id']

        print("Code found: {}".format(codigo))
        return codigo


    def get_total_price(self, products):
        total_price = 0
        for product in products:
            total_price += product['precoUnitarioLiquido']

        return total_price
