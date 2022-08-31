from sanic import Sanic
from dotenv import load_dotenv

load_dotenv()

application = Sanic(name="IntegracaoHiperDeliveryDireto")

import app
