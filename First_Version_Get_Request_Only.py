from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import parse_qs

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
      print("url: " + self.path)
      if self.headers.get('X-Forwarded-Proto', 'http') == 'http':
            self.send_response(301)
            self.send_header('Location', 'https://' + self.headers['Host'] + self.path)
            self.end_headers()

      if self.path == "/":
        with open("index.html", "rb") as data:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data.read())

        return

      path = self.path[1:]

      if 'more-color' in path:

        directory = '/home/ubuntu/vivian/favorite-color'
        
        files = os.listdir(directory)
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

        next_10_files = files[10:20]

        arr = []

        for file in next_10_files:
          with open(f'/home/ubuntu/vivian/favorite-color/{file}', "r") as f:
            data = json.load(f)
            arr.append(data)

        print(arr)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(arr).encode('utf8'))
        return

      if 'favorite-color?' in path:
        url, query = path.split('?')
        values = query.split('&')

        store = {}

        for value in values:
            key, value = value.split('=')
            store[key] = value
        
        colors = ('red', 'blue', 'green')
        color_value = store.get('color')

        if not color_value in colors:
          print('Invalid parameters')
          self.send_response(400)
          self.end_headers()
          self.wfile.write(b"Invalid parameters") 
          return

        first_value = store.get('first')
        if not first_value:
          print('Invalid parameters')
          self.send_response(400)
          self.end_headers()
          self.wfile.write(b"Invalid parameters")
          return
          
        print('User Form Submitted')

        json_object = json.dumps(store, indent = 4)

        output_dir = '/home/ubuntu/vivian/favorite-color/'
        base_filename = 'output'

        file_list = [f for f in os.listdir(output_dir) if f.startswith(base_filename)]
        latest_file_num = len(file_list) + 1

        new_filename = f"{output_dir}{base_filename}{latest_file_num}.json"

        with open(new_filename, 'w') as outfile:
            outfile.write(json_object)

        with open("favorite-color.html", "rb") as data:
          
          filedata = data.read().decode('utf8')

          directory = '/home/ubuntu/vivian/favorite-color'

          files = os.listdir(directory)
          files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

          print(files)

          last_10_files = files[:10]

          to_insert = ''

          for file in last_10_files:
              with open(f'/home/ubuntu/vivian/favorite-color/{file}', "r") as f:
                  data = json.load(f)

                  first_name = data["first"]
                  color = data["color"]

                  to_insert += f'<p>{first_name}: {color}</p>'
              
              print(to_insert)
                  

          filedata = filedata.replace('%' + 'allthepeople%', to_insert)
              
          self.send_response(200)
          self.end_headers()    
          self.wfile.write(filedata.encode('utf8'))
      
      else: 
        try:
            with open(path, "rb") as data:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data.read())
                
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404")

    def do_POST(self):
      print("url: " + self.path)

      print('-- headers --')
      print(self.headers)
      try:
        content_lenght = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_lenght).decode('utf-8')
        
        print('-- post data --')
        print(post_data)
        body = parse_qs(post_data)
        
        print('-- parsed post data --')
        print(body)
        return

      except ValueError:
        print('Received non-HTTP request, ignoring')
        return

myServer = HTTPServer(("", 3000), MyServer)

try:
    print("Server Running")
    myServer.serve_forever()
except KeyboardInterrupt:
    myServer.server_close()