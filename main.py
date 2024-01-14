from flask import Flask, request, Response
from http_req import get_response, get_responses, get_responses_async
from editor import processes
from data import get_data
from urllib.parse import unquote
import base64
import asyncio

app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/')
def process_query():
    query_url = request.args.get('url')
    if not query_url:
      return "Vui lòng cung cấp tham số URL", 200
    uuid = request.args.get('uuid')
    sni = request.args.get('sni')
    tag = request.args.get('tag')
    headers = {"User-Agent": "v2rayNG/1.8.12"}
    query_url = unquote(query_url)
    list_links = get_response(query_url)
    links = processes(list_links, uuid, sni, tag)
    links = '\n'.join(links).encode('utf-8')
    result = base64.b64encode(link).decode('utf-8')
    return Response(result, mimetype='text/plain')

@app.route('/list/<filename>')
def get_all_urls(filename):
    try:
      urls = get_data(filename)
      resp = make_response('\n'.join(urls))
      resp.mimetype = 'text/plain'
      return resp
    except Exception as e:
      return {"status": "failed", "message": str(e)}, 404
     
@app.route('/get/<filename>')
def process_all_config(filename):
  uuid = request.args.get('uuid')
  sni = request.args.get('sni')
  tag = request.args.get('tag')
  try:
    urls = get_data(filename)
  except Exception as e:
    return {"status": "failed", "message": str(e)}, 404
  list_links = loop.run_until_complete(get_responses_async(urls))
  links = processes(list_links, uuid, sni, tag)
  links = '\n'.join(links).encode('utf-8')
  result = base64.b64encode(links).decode('utf-8')
  return Response(result, mimetype='text/plain')