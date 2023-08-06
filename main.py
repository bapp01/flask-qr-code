# Example usage: http://127.0.0.1:5000/qrcode?data=Example&size=512&color=FFFFFF&bgcolor=00000
from flask import Flask, request, send_file
import os
import qrcode
import re
import hashlib
from PIL import Image, ImageFilter

app = Flask(__name__)

def filename(data,size,color,bgcolor): # hashes the entered data, size, color, and bgcolor and using it as a filename
    data = "" if data == None else data
    hasher = hashlib.sha256()
    hasher.update((data + str(size) +  color + bgcolor).encode('utf-8'))
    return hasher.hexdigest()+".jpg"

def is_valid_hex_code(hex_code): # checks if the given hex is valid
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return re.match(pattern, hex_code) is not None

qr_path = os.getcwd() + "\static\\qr\\"
# change to any as you wish
default_res = 256 # default resolution of qr codes
max_res = 1080 # max resolution of qr codes
default_color = "#000000"
default_bgcolor = "#FFFFFF"
save_limit = 1000 # limit of qr codes that should be stored

@app.route("/qrcode")
def create_qr_code():
    data = request.args.get('data')
    color = request.args.get('color')
    bgcolor = request.args.get('bgcolor')
    try:
        size = int(request.args.get('size'))
    except TypeError: # if size entered is invalid
        size = default_res

    size = max_res if size > max_res else size

    color = default_color if color is None else '#' + color # default color: #000000 (black)
    color = color if is_valid_hex_code(color) else default_color # if user entered a non valid hex code for the color it changes it to the default

    bgcolor = default_bgcolor if bgcolor is None else '#' + bgcolor  # default bgcolor: #FFFFFF (white)
    bgcolor = bgcolor if is_valid_hex_code(bgcolor) else default_bgcolor # if user entered a non valid hex code for the background color it changes it to the default

    Filename = filename(data, size, color, bgcolor) # Generates the filename

    saved_qr_codes = os.listdir(qr_path)
    if Filename in saved_qr_codes: # checks if the parameters where entered before
        return send_file(qr_path + saved_qr_codes[saved_qr_codes.index(Filename)], mimetype="image/jpg") # returns the same image if the same parameters are entered before
    else:
        # If there the number of qr codes saved equals to the value of the "save_limit" variable it deletes the oldest qr code saved
        saved_qr_codes = os.listdir(qr_path)
        while len(saved_qr_codes) >= save_limit:
            os.remove(os.path.join(qr_path, saved_qr_codes[-1])) 
            saved_qr_codes = os.listdir(qr_path)
        #creating the qr code
        qr = qrcode.QRCode(version=1, box_size=50, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        qr.make_image(fill_color=color, back_color=bgcolor).resize((size, size), resample=Image.NEAREST).filter(ImageFilter.SHARPEN).save(qr_path + Filename, quality=95)
        return send_file(qr_path + Filename, mimetype="image/jpg")

if __name__ == '__main__':
    app.run()

# using waitress 
# if __name__ == 'main':
#     from waitress import serve
#     serve(app, threads=4)