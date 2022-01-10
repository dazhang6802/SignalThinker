# -*- coding: UTF-8 -*-


from sanic import Sanic
from sanic import response

app = Sanic(__name__)


@app.route("/get", methods=['GET'])
async def get_handler(request):
    return response.json({"Hello": "world"})


@app.route("/post", methods=['POST'])
async def post_handler(request):
    return response.text("ok")


app.run(host="0.0.0.0", port=80, debug=True)
