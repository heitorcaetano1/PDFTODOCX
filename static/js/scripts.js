console.log("Página de upload carregada.");

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
