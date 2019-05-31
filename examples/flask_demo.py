# coding=utf-8

import logging
import apyllo
import flask
from flask import Flask


app = Flask(__name__)


@app.route("/")
def config():
    client = apyllo.get_client()
    content = client.get_content("demo.yml")

    resp = flask.make_response(content)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


def init_client():
    apyllo.set_logger(
        'apyllo',
        logging.DEBUG,
        rotate_file_path='/tmp/apyllo.log',
    )
    client = apyllo.client(
        config_server_host="your-apollo-meta-service.com",
        app_id="apyllo-demo",
        namespaces=["application", "demo.yml"],
    )
    client.start()

    # user manually download ns config.
    # client.download("demo.yml")


if __name__ == "__main__":
    init_client()
    app.run(debug=True)
