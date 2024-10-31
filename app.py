from flask import Flask, request, render_template, send_file, url_for
from PIL import Image, ImageOps
import io
import os

app = Flask(__name__)

# Caminho para a pasta de imagens
IMAGE_FOLDER = 'static/images'

def process_image(image):
    # Verificar se a imagem está no modo RGBA e, se estiver, converter para RGB
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Dividir em blocos e processar
    block_size = 100
    processed_blocks = []
    for i in range(0, image.size[0], block_size):
        for j in range(0, image.size[1], block_size):
            block = image.crop((i, j, i + block_size, j + block_size))
            processed_block = ImageOps.autocontrast(ImageOps.solarize(block, threshold=128))
            processed_blocks.append((processed_block, i, j))
    
    # Recombinar os blocos processados
    final_image = Image.new("RGB", image.size)
    for block, x, y in processed_blocks:
        final_image.paste(block, (x, y))
    return final_image


@app.route('/')
def index():
    # Listar as imagens da pasta
    image_files = os.listdir(IMAGE_FOLDER)
    return render_template('index.html', images=image_files)

@app.route('/process/<image_name>')
def process(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    if os.path.exists(image_path):
        image = Image.open(image_path)
        processed_image = process_image(image)

        # Salvar imagem processada em memória para envio
        img_io = io.BytesIO()
        processed_image.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    return "Erro: Imagem não encontrada.", 404

if __name__ == '__main__':
    app.run(debug=True)