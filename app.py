from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    logos = os.listdir('static/logos')
    return render_template('index.html', logos=logos)

@app.route('/generate', methods=['POST'])
def generate_poster():
    shop_name = request.form['shop_name']
    offer = request.form['offer']
    place = request.form['place']
    logo_file = request.form['logo']

    # Load background image
    background = Image.open("static/background.jpg")
    draw = ImageDraw.Draw(background)

    # Load fonts (ensure these font files exist in your /fonts folder)
    font_large = ImageFont.truetype("fonts/OpenSans-Bold.ttf", 50)
    font_small = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 30)

    # Write text on image
    draw.text((50, 50), shop_name, font=font_large, fill="black")
    draw.text((50, 120), offer, font=font_small, fill="black")
    draw.text((50, 180), place, font=font_small, fill="black")

    # Paste logo
    logo_path = os.path.join('static/logos', logo_file)
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((200, 200))
    background.paste(logo, (background.width - 250, 50), logo)

    # Save to BytesIO
    img_io = BytesIO()
    background.save(img_io, 'PNG')
    img_io.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return send_file(img_io, mimetype='image/png', as_attachment=True,
                     download_name=f"poster_{timestamp}.png")

if __name__ == '__main__':
    app.run(debug=True)
