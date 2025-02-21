<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Editor de Texto</title>
  <script src="https://cdn.ckeditor.com/ckeditor5/29.1.0/classic/ckeditor.js"></script>
</head>
<body>

<h1>Página de Upload</h1>
<input type="file" id="file-upload">
<button id="convert-btn">Converter</button>
<button id="edit-btn">Editar</button>

<div id="editor"></div>

<script>
  console.log("Página de upload carregada.");

  // Inicializa o editor CKEditor
  ClassicEditor
    .create(document.querySelector('#editor'), {
      toolbar: [
        'heading', '|',
        'bold', 'italic', 'underline', 'strikethrough', '|',
        'fontFamily', 'fontSize', 'fontColor', 'fontBackgroundColor', '|',
        'alignment', 'outdent', 'indent', '|',
        'bulletedList', 'numberedList', 'blockQuote', '|',
        'insertTable', 'uploadImage', '|',
        'undo', 'redo'
      ],
      fontFamily: {
        options: [
          'default',
          'Arial, Helvetica, sans-serif',
          'Courier New, Courier, monospace',
          'Georgia, serif',
          'Lucida Sans Unicode, Lucida Grande, sans-serif',
          'Tahoma, Geneva, sans-serif',
          'Times New Roman, Times, serif',
          'Trebuchet MS, Helvetica, sans-serif'
        ],
        supportAllValues: true
      },
      fontSize: {
        options: [ '10px', '12px', '14px', '16px', '18px', '24px', '32px', '48px' ],
        supportAllValues: true
      },
      alignment: {
        options: [ 'left', 'center', 'right', 'justify' ]
      }
    })
    .catch(error => {
      console.error(error);
    });

  // Manipulação dos botões de conversão e edição
  document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file-upload");
    const convertButton = document.getElementById("convert-btn");
    const editButton = document.getElementById("edit-btn");

    // Esconde os botões no início
    convertButton.style.display = "none";
    editButton.style.display = "none";

    // Exibe os botões somente quando o usuário selecionar um arquivo
    fileInput.addEventListener("change", function () {
      if (fileInput.files.length > 0) {
        convertButton.style.display = "block";
        editButton.style.display = "block";
      } else {
        convertButton.style.display = "none";
        editButton.style.display = "none";
      }
    });
  });
</script>

</body>
</html>
