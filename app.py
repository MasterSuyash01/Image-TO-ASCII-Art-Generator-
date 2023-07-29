from PIL import Image
from flask import Flask, render_template, request, Response
import io

app = Flask(__name__)

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']


def load_image(image_path, new_width=100, max_height=100):
    img = Image.open(image_path)
    width_ratio = new_width / float(img.size[0])
    new_height = min(int(float(img.size[1]) * float(width_ratio)), max_height)
    resized_img = img.resize((new_width, new_height))
    return resized_img


def grayify(image):
    grayscale_image = image.convert("L")
    return grayscale_image


def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel_value in pixels:
        ascii_str += ASCII_CHARS[pixel_value // 25]
    return ascii_str


@app.route("/", methods=["GET", "POST"])
def image_to_ascii():
    if request.method == "POST":
        image = request.files["image"]
        if image:
            try:
                temp_image_path = "temp.jpg"
                image.save(temp_image_path)

                img = load_image(temp_image_path)
                img = grayify(img)
                ascii_str = pixels_to_ascii(img)

                img_width = img.width
                ascii_str_len = len(ascii_str)
                ascii_img_rows = [ascii_str[i:i + img_width] for i in range(0, ascii_str_len, img_width)]

                return render_template("index.html", ascii_img_rows=ascii_img_rows)

            except Exception as e:
                error_message = "Error: " + str(e)
                return render_template("index.html", error_message=error_message)

    return render_template("index.html", ascii_img_rows=None)


@app.route("/download", methods=["GET"])
def download_ascii():
    ascii_img_rows = request.args.get('ascii_img_rows')
    if ascii_img_rows:
        ascii_content = '\n'.join(ascii_img_rows.split('|'))
        ascii_bytes = io.BytesIO(ascii_content.encode())
        return Response(ascii_bytes, content_type='text/plain', headers={'Content-Disposition': 'attachment; filename=ascii_art.txt'})
    else:
        return "No ASCII art found to download."


if __name__ == "__main__":
    app.run(debug=True)
