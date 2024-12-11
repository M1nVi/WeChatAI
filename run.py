import sys
import os
import requests
import hashlib
import time
from flask import Flask, request, make_response, jsonify
import xmltodict
from wxcloudrun import app


if __name__ == '__main__':
    print(app.url_map)
    app.run(host=sys.argv[1], port=sys.argv[2])
