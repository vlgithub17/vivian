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

      if "favorite-animal?page=" in path:
    
        originalpath, page = path.split('=')
        page = int(page)
        print(path)

        # Read the HTML file
        with open("favorite-animal.html", "r", encoding='utf-8') as f:
            filedata = f.read()

        directory = '/home/ubuntu/vivian/favorite-animal'
        files = os.listdir(directory)
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True) 

        if page > 0:
            lower_bound = (page) * 10
            upper_bound = lower_bound + 10
        
        last_10_files = files[(lower_bound):(upper_bound)]
        print('LENGHT')
        print(len(last_10_files))
        to_insert_list = ''
        
        for file in last_10_files:
            with open(os.path.join(directory, file), "r") as f:
                data = json.load(f)
                first_name = data["name"][0]
                animal = data["animal"][0]
                to_insert_list += f'<p>{first_name}: {animal}</p>'

        if len(last_10_files) < 10:
            new_page_url = ''
        else: 
            new_page_url = f'<a id="nextPageLink" href="/favorite-animal?page={page + 1}">Next page</a>'

        #Replacing HTML holders
        filedata = filedata.replace('%nextpage%', new_page_url)
        filedata = filedata.replace('%' + 'allthepeople%', to_insert_list) 
        filedata = filedata.replace('%' + 'message%', f'<h>Other peoples favorite colors</h1>')

        self.send_response(200)
        self.send_header('Cache-Control', 'max-age=600')
        self.end_headers()
        self.wfile.write(filedata.encode('utf8'))
        return

      else: 
        try: 
            if os.path.isfile(path):
              with open(path, "rb") as data:      
                  self.send_response(200)
                  self.send_header('Cache-Control', 'max-age=600')
                  #   self.send_header('Content-Type', 'application/octet-stream')
                  self.end_headers()
                  self.wfile.write(data.read())
            else:
              self.send_response(403)
              self.end_headers()
              self.wfile.write(b"403 Forbidden: Path is a directory")   

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404")
    

    def do_POST(self):
        print("url: " + self.path)
        print('-- headers --')
        print(self.headers)
        
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            print('-- post data --')
            print(post_data)
            body = parse_qs(post_data)
            
            print('-- parsed post data --')
            print(body)
            
            path = self.path[1:]
            print(path)

            # Age form

            if path == 'age':
                user = json.loads(post_data)
                name_string = user['name']

                age = len(name_string)
                message = ''

                if age < 10:
                    message = "You're a baby!"
                elif age >= 20:
                    message = "When are you going to get a job?"
                elif age >= 10:
                    message = "What are you doing here? Go to school!"
                
                self.send_response(200)
                self.send_header('access-control-allow-origin', 'https://vivian-lima.com')
                self.end_headers()
                self.wfile.write(f'Hi, {name_string}. {message}'.encode('utf-8'))
                return
            
            #Favorite animal form
            
            if 'favorite-animal' in path:      
                print('User Form Submitted')

                # Saving the file
                name_string = body['name'][0]
                json_object = json.dumps(body, indent=4, ensure_ascii=False)

                output_dir = '/home/ubuntu/vivian/favorite-animal/'
                base_filename = f'{name_string}.json'
                new_filename = os.path.join(output_dir, base_filename)
                
                # Write on existing file
                if os.path.isfile(new_filename):
                    with open(new_filename, "r") as f:
                        data = json.load(f)
                        new_animal = body['animal'][0]
                        
                        if new_animal not in data['animal']:
                            data['animal'].append(body['animal'][0])
                        
                    # Write the updated data back to the file
                    with open(new_filename, "w") as f:
                        json.dump(data, f, indent=4)

                # Write a new file
                else:
                    with open(new_filename, 'w') as outfile:
                        outfile.write(json_object + '\n') 

                # Organize Files 
                directory = '/home/ubuntu/vivian/favorite-animal'
                files = os.listdir(directory)

                #Sort based on the modification time
                files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True) 

                # Read the HTML file
                with open("favorite-animal.html", "r") as f:
                    filedata = f.read()

                #Link to next page
                page = 0
                new_page_url = f'<a id="nextPageLink" href="/favorite-animal?page={page + 1}">Next page</a>'
                filedata = filedata.replace('%nextpage%', new_page_url) 

                # Process the latest file
                latest_file = files[0]

                with open(os.path.join(directory, latest_file), "r") as f:
                    data = json.load(f)
                    first_name = data["name"][0]
                    animal = data["animal"][0]
                    to_insert = f'Hello, {first_name}. <p>Your favorite animal nowadays is {animal}</p>'
                    filedata = filedata.replace('%' + 'message%', to_insert)

                # Process the last 10 files
                last_10_files = files[:10]
                to_insert_list = ''

                for file in last_10_files:
                    with open(os.path.join(directory, file), "r") as f:
                        data = json.load(f)
                        first_name = data["name"][0]
                        animal = ", ".join(data["animal"][::-1])
                        to_insert_list += f'<p>{first_name}: {animal}</p>'

                filedata = filedata.replace('%' + 'allthepeople%', to_insert_list)
      
                self.send_response(200)
                self.end_headers()
                self.wfile.write(filedata.encode('utf8'))

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404")        
            

myServer = HTTPServer(("", 3000), MyServer)

try:
    print("Server Running")
    myServer.serve_forever()
except KeyboardInterrupt:
    myServer.server_close()