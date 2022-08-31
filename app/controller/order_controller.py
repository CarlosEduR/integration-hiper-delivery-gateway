from main import application as app
from sanic.response import text
from app.service.hiper.hiper_service import HiperService

@app.get("hiper-delivery/health-check")
async def home(request):
    print("Health checking...")
    return text("Hello, World!")


@app.post("hiper-delivery/api/webhook")
async def order_event(request):
    HiperService().register_order(request.json["order"])
    return text("Hello, Webhook")
