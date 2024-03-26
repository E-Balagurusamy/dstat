from flask import Flask, render_template, request, abort
import cloudscraper
import requests 
import os


app = Flask(__name__)

counter_file = 'count.txt'
counter_length = 8


def requests_counter():
    try:
        with open(counter_file, 'r+') as fp:
            counter_str = fp.read().strip().split(',')
            
            if not counter_str[0]:
                counter_str[0] = '0'  # Set default value as string '0'
            
            counter_int = int(counter_str[0]) + 1  # Convert to integer and increment
            
            counter_str[0] = str(counter_int)  # Convert back to string for writing
            
            fp.seek(0)
            fp.write(','.join(counter_str))  # Write back as string
            fp.truncate()
        
        res = ','.join(counter_str)
        return res
    except IOError:
        # Error handling
        pass
  
def blocked_counter():
    try:
        with open(counter_file, 'r+') as fp:
            counter_str = fp.read().strip().split(',')
            
            if not counter_str[1]:
                counter_str[1] = '0'  # Set default value as string '0'
            
            counter_int = int(counter_str[1]) + 1  # Convert to integer and increment
            
            counter_str[1] = str(counter_int)  # Convert back to string for writing
            
            fp.seek(0)
            fp.write(','.join(counter_str))  # Write back as string
            fp.truncate()
    except IOError:
        # Error handling
        pass
    
            
COMMON_USER_AGENTS = [
    'Mozilla', 'Chrome', 'Safari', 'Firefox', 'Opera', 'Edge'
]
    

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

@app.route('/')
def index():
    new_count = requests_counter()
    return render_template('index.html')#f"{new_count}"

@app.route('/get')
def get():
    new_count = requests_counter()
    return f"{new_count}"

@app.route('/api')
def get_count():
    with open(counter_file, 'r') as fp:
        counter = fp.read().strip()
        
    return f"{     {counter}     }"
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    
