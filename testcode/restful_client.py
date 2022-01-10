import requests

r = requests.get("http://127.0.0.1/get?a=1")
print(r)
s = requests.post("http://127.0.0.1/post", {"key":"value"})
print(s)