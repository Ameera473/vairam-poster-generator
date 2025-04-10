from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

app = Flask(__name__)

# Ensure output and static folders exist
os.makedirs('output', exist_ok=True)
os.makedirs(os.path.join('static', 'fonts'), exist_ok=True)

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
    company = request.form['company']
    photo = request.files['photo']

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
    draw.text((400, 790), "Congratulations on your purchase!", font=font_small, fill="#008000", anchor="mm")
    draw.text((400, 840), "Thank you for purchasing with us", font=font_small, fill="#000080", anchor="mm")
    draw.text((400, 880), "Visit Again!", font=font_small, fill="#FF4500", anchor="mm")

    # Save poster
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"poster_{timestamp}.jpg"
    filepath = os.path.join("output", filename)
    poster.save(filepath)

    return send_file(filepath, mimetype='image/jpeg', as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
