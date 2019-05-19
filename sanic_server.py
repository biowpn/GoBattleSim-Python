
import json
import ssl
import json
import os
import time

from sanic import Sanic
import sanic.views
import sanic.response
from sanic.exceptions import ServerError

import gobattlesim.application as GBS



app = Sanic()
app.config.from_pyfile("config.py")

for fname in os.listdir(app.config.ROOT_DIR):
    app.static('/' + fname, os.path.join(app.config.ROOT_DIR, fname), name=fname)



with open('data/GBS_GAME_MASTER.json', encoding='utf-8') as fd:
    game_master = GBS.GameMaster()
    game_master.from_json(json.load(fd))
    GBS.set_default_game_master(game_master)


class SimpleView(sanic.views.HTTPMethodView):

    def get(self, request):
        fpath = os.path.join(request.app.config.ROOT_DIR, "index.html")
        if os.path.isfile(fpath):
            with open(fpath) as f:
                return sanic.response.html(f.read())
        else:
            return sanic.response.text('Not Found', statuts=404)
    

    def post(self, request):
        if request.headers['Origin'] not in request.app.config.ORIGINS_ALLOWED:
            return sanic.response.text("Forbidden", status=403)
        client_req = request.json
        handler = GBS.RequestHandler()
        resp_json = handler.handle_request(client_req)

        return sanic.response.json(
            resp_json,
            headers={
                "Access-Control-Allow-Origin": request.headers['Origin']
            }
        )


app.add_route(SimpleView.as_view(), '/')


# Something is not working. Can't return Python Exception text
##@app.exception(Exception)
##async def my_error_handler(request, exception):
##    return sanic.response.text(exception, status=500, message=str(exception))



if __name__ == '__main__':
    if app.config.PATH_CERTFILE and app.config.PATH_KEYFILE:
        # HTTPS and deploying
        app.run(host=app.config.HOST,
                port=app.config.PORT,
                workers=os.cpu_count(),
                ssl={
                    'cert': app.config.PATH_CERTFILE,
                    'key': app.config.PATH_KEYFILE
                },
                debug=False,
                access_log=False)
    else:
        app.run(host=app.config.HOST,
                port=app.config.PORT)



