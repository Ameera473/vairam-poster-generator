from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import sqlite3
import csv

app = Flask(__name__)

# Ensure output and static folders exist
os.makedirs('output', exist_ok=True)
os.makedirs(os.path.join('static', 'fonts'), exist_ok=True)

# Database setup
conn = sqlite3.connect('customers.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        major_city TEXT,
        local_area TEXT,
        created_at TEXT
    )
''')
conn.commit()

# Load fonts
def load_font(font_name, size):
    try:
        return ImageFont.truetype(os.path.join('static', 'fonts', font_name), size)
    except:
        return ImageFont.load_default()

# Preload fonts
font_large = load_font("OpenSans-Bold.ttf", 60)
font_medium = load_font("OpenSans-SemiBold.ttf", 40)
font_small = load_font("OpenSans-Regular.ttf", 30)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_poster():
    customer_name = request.form['customer_name']
    phone = request.form['phone_number']
    main_city = request.form['main_city']
    local_area = request.form['local_area']
    company = request.form['company']
    photo = request.files['photo']



    full_location = f"{local_area}, {main_city}"

    # Save to DB
    cursor.execute(''' 
        INSERT INTO customers (name, phone, major_city, local_area, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_name, phone, main_city, local_area, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    # Create base poster with colorful background
    poster = Image.new('RGB', (800, 1000), color='#f7d9e3')  # light pink
    draw = ImageDraw.Draw(poster)

    # Add customer photo
    customer_img = Image.open(photo).resize((400, 400))
    poster.paste(customer_img, (200, 50))

    # Add company logo
    logo_path = os.path.join('static', 'logos', f'{company}.png')
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path).resize((150, 150))
        poster.paste(logo_img, (325, 470), logo_img.convert("RGBA"))

    # Add texts with proper fonts
    draw.text((400, 640), "Vairam Steel Company", font=font_medium, fill="#D10000", anchor="mm")
    draw.text((400, 680), "Dharapuram", font=font_small, fill="black", anchor="mm")
    draw.text((400, 730), f"{customer_name}", font=font_large, fill="black", anchor="mm")
    draw.text((400, 770), f"From: {full_location}", font=font_small, fill="black", anchor="mm")
    draw.text((400, 810), "Congratulations on your purchase!", font=font_small, fill="#008000", anchor="mm")
    draw.text((400, 850), "Thank you for purchasing with us", font=font_small, fill="#000080", anchor="mm")
    draw.text((400, 890), "Visit Again!", font=font_small, fill="#FF4500", anchor="mm")

    # Save poster
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"poster_{timestamp}.jpg"
    filepath = os.path.join("output", filename)
    poster.save(filepath)

    # Write to CSV
    with open('customer_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([customer_name, phone, main_city, local_area, company, timestamp])

    return send_file(filepath, mimetype='image/jpeg', as_attachment=True, download_name=filename)
@app.route('/download_excel')
def download_excel():
    csv_path = 'customer_data.csv'
    if os.path.exists(csv_path):
        return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='customer_data.csv')
    else:
        return "Customer data file not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
