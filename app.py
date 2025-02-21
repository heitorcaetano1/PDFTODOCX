import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from pdf2docx import Converter
import mammoth
import pypandoc
from werkzeug.utils import secure_filename
import pdfkit
from PIL import Image
import io
import re
from bs4 import BeautifulSoup
import base64


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "sua_chave_secreta"

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Aumentado para 500MB
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TIMEOUT'] = 300

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True) # Cria a pasta templates



def convert_pdf_to_docx(pdf_path, docx_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
    except Exception as e:
        raise Exception("Falha na conversão PDF → DOCX: " + str(e))

def convert_docx_to_html(docx_path):
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value
        # Envolve o HTML com um template inline customizado (CSS inline)
        wrapped_html = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              font-family: Calibri, sans-serif;
              margin: 20px;
              line-height: 1.6;
            }}
          </style>
          <title>Documento Convertido</title>
        </head>
        <body>
          {html}
        </body>
        </html>
        """
        return wrapped_html
    except Exception as e:
        raise Exception("Falha na conversão DOCX → HTML: " + str(e))

def convert_html_to_docx(html_content, output_docx):
    try:
        reference_doc = 'templates/reference.docx'
        extra_args = ['--reference-doc=' + reference_doc] if os.path.exists(reference_doc) else []
        pypandoc.convert_text(html_content, 'docx', format='html', extra_args=extra_args, outputfile=output_docx)
        return output_docx
    except Exception as e:
        raise Exception(f"Falha na conversão HTML → DOCX: {str(e)}")

def convert_html_to_pdf(html_content, output_pdf):
    try:
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")  # Ajuste o caminho
        options = {
            'encoding': "UTF-8",
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'page-size': 'A4',
        }
        pdfkit.from_string(html_content, output_pdf, configuration=config, options=options)
        return output_pdf
    except Exception as e:
        raise Exception(f"Falha na conversão HTML → PDF: {str(e)}")

def optimize_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for element in soup.find_all(text=lambda text: isinstance(text, str)):
        element.replace_with(element.strip())

    for tag in soup.find_all(['script', 'style', 'meta', 'link', 'head']):
        tag.decompose()

    for img_tag in soup.find_all('img'):
        if 'src' in img_tag.attrs:
            img_src = img_tag['src']
            if img_src.startswith('data:'):
                continue
            try:
                if not os.path.isabs(img_src):
                    img_path = os.path.join(os.path.dirname(request.path), img_src)
                    if not os.path.exists(img_path):
                        img_path = os.path.join(app.static_folder, img_src)
                else:
                    img_path = img_src

                if os.path.exists(img_path):
                    compressed_image = compress_image(img_path)
                    if compressed_image:
                        img_tag['src'] = "data:image/jpeg;base64," + compressed_image.decode('utf-8')
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

    return str(soup)

def compress_image(image_path, quality=80):
    try:
        img = Image.open(image_path)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality)
        return base64.b64encode(img_buffer.getvalue())
    except Exception as e:
        print(f"Erro ao comprimir imagem: {e}")
        return None



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash("Nome de arquivo inválido")
        return redirect(url_for('index'))

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename) # Segurança: Limpa o nome do arquivo
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            # Salva o arquivo usando streaming
            file.save(pdf_path)

            # Resto do seu código (conversão, etc.) ...
            docx_filename = os.path.splitext(filename)[0] + ".docx"
            docx_path = os.path.join(app.config['CONVERTED_FOLDER'], docx_filename)
            convert_pdf_to_docx(pdf_path, docx_path)

            action = request.form.get('action')
            if action == 'edit':
                return redirect(url_for('edit', docx_filename=docx_filename))
            elif action == 'convert':
                return send_file(docx_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document') # Define o mimetype correto

        except Exception as e:
            flash(f"Ocorreu um erro: {str(e)}") # Mensagem de erro mais informativa
            return redirect(url_for('index'))

    else:
        flash("Arquivo inválido, envie um PDF")
        return redirect(url_for('index'))

@app.route('/edit/<docx_filename>')
def edit(docx_filename):
    docx_path = os.path.join(app.config['CONVERTED_FOLDER'], docx_filename)
    try:
        html_content = convert_docx_to_html(docx_path)
    except Exception as e:
        flash(str(e))
        html_content = ""
    return render_template('edit.html', filename=docx_filename, content=html_content)

@app.route('/save', methods=['POST'])
def save():

    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return "Request Entity Too Large", 413

    edited_html = request.form['content']
    docx_filename = request.form['docx_filename']

    optimized_html = optimize_html(edited_html)

    output_docx = os.path.join(app.config['CONVERTED_FOLDER'], "edited_" + os.path.splitext(docx_filename)[0] + ".docx")
    try:
        convert_html_to_docx(optimized_html, output_docx)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('edit', docx_filename=docx_filename))

    output_pdf = os.path.join(app.config['CONVERTED_FOLDER'], "edited_" + os.path.splitext(docx_filename)[0] + ".pdf")
    try:
        convert_html_to_pdf(optimized_html, output_pdf)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('edit', docx_filename=docx_filename))

    return send_file(output_pdf, as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
