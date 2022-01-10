import ssl

from sanic import Sanic
from sanic import response

app = Sanic(__name__)


@app.route("/get", methods=['GET'])
async def get_handler(request):
    return response.text("Hello ssl get")


@app.route("/post", methods=['POST'])
async def post_handler(request):
    return response.text("hello ssl post")

context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain("ssl.crt", keyfile="ssl.key.nopassword")

#app.run(host="0.0.0.0", port=8080)

app.run(host="0.0.0.0", port=8080, ssl=context)
