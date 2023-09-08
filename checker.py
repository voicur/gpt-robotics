import requests
import json
import urllib.parse

url = 'https://contentatscale.ai/ai-content-detector/'
headers = {
    'Content-Encoding': 'br',
    'Content-Type': 'text/html; charset=UTF-8',
    'Date': 'Wed, 06 Sep 2023 01:45:35 GMT',
    'Host-Header': '8441280b0c35cbc1147f8ba998a563a7',
    'Server': 'nginx',
    'Vary': 'Accept-Encoding',
    'X-Httpd-Modphp': '1',
    'X-Proxy-Cache-Info': 'DT:1',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Length': '4921',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Dnt': '1',
    'Origin': 'https://contentatscale.ai',
    'Referer': 'https://contentatscale.ai/ai-content-detector/',
    'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
    'X-Requested-With': 'XMLHttpRequest'
}

text_here = "Greetings, Sussy Bakahi; greetings again, and yet another greeting to you as well. It seems there's an insatiable need to call out your name--Sussy Bakahi: a sequence that rings through the air multiple times over. But alas! An error manifests amidst this chorus of banter; thrice does it appear stating in clear terms, 'The input should contain at least 50 words.' Due to an error; the input needs a minimum of 50 words."

data = f'''
content={urllib.parse.quote_plus(text_here)}&action=checkaiscore
'''

print(data)

response = requests.post(url, headers=headers, data=data)
response.encoding = "utf-8-sig"

# if response.headers.get('Content-Encoding') == 'br':
#     # Decode the response using Brotli decompression
#     decompressed_response = brotli.decompress(response.content)
#     decoded_response = decompressed_response.decode('utf-8')
# else:
#     # Use the default decoding for other encodings

print(response.text)

decoded_response = json.loads(response.text);


print(response.status_code)

sentences = decoded_response["sentences"]


print(sentences)

