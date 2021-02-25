# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:06:16
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:06:18
from flask.helpers import make_response
from flask.json import jsonify


def process_ipc_response(response):
    if response:
        if response["result"]:
            return jsonify(response.get("value"))
        else:
            return make_response(jsonify({"message": response["message"]}), 500)
    else:
        return make_response(jsonify({"message": "No response from monitoring service"}), 503)
