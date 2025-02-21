import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from pdf2docx import Converter
import mammoth
import pypandoc
from werkzeug.utils import secure_filename
import pdfkit

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "sua_chave_secreta"

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Desativar cache
app.config['TIMEOUT'] = 300  # Aumenta o tempo máximo para 5 minutos


# Pastas de trabalho
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

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

def convert_html_to_docx(edited_html, output_docx):
    try:
        # Utiliza um arquivo de referência customizado para manter a formatação.
        # Certifique-se de ter um arquivo "templates/reference.docx" com os estilos desejados.
        pypandoc.convert_text(
            edited_html,
            'docx',
            format='html',
            extra_args=['--reference-doc=templates/reference.docx'],
            outputfile=output_docx
        )
        return output_docx
    except Exception as e:
        raise Exception("Falha na conversão HTML → DOCX: " + str(e))

def convert_html_to_pdf(edited_html, output_pdf):
    try:
        # Cria um template HTML inline com CSS para preservar margens, fontes e alinhamento
        html_template = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              font-family: Calibri, sans-serif;
              margin: 40px;
              line-height: 1.6;
            }}
          </style>
          <title>Documento Editado</title>
        </head>
        <body>
          {edited_html}
        </body>
        </html>
        """
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        options = {
          'encoding': "UTF-8",
          # Outras opções podem ser adicionadas aqui (margens, cabeçalhos, etc.)
        }
        pdfkit.from_string(html_template, output_pdf, configuration=config, options=options)
        return output_pdf
    except Exception as e:
        raise Exception("Falha na conversão HTML → PDF: " + str(e))

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
    edited_html = request.form['content']
    docx_filename = request.form['docx_filename']
    # Opcional: converter o HTML editado para DOCX final
    output_docx = os.path.join(app.config['CONVERTED_FOLDER'], "edited_" + os.path.splitext(docx_filename)[0] + ".docx")
    try:
        convert_html_to_docx(edited_html, output_docx)
    except Exception as e:
        flash(str(e))
    # Converte o HTML para PDF
    output_pdf = os.path.join(app.config['CONVERTED_FOLDER'], "edited_" + os.path.splitext(docx_filename)[0] + ".pdf")
    try:
        convert_html_to_pdf(edited_html, output_pdf)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('edit', docx_filename=docx_filename))
    return send_file(output_pdf, as_attachment=True)

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


@app.route('/termos')
def termos():
    return render_template('termos.html')

@app.route('/tutorial')
def tutorial():
    return render_template('/tutorial.html')

if __name__ == '__main__':
    app.run(debug=True)
