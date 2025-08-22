document.getElementById('add-file-input').addEventListener('click', function() {
    var fileInputs = document.getElementById('file-inputs');
    var fileInputCount = fileInputs.getElementsByClassName('input-group').length;
    var newFileInput = document.createElement('div');
    newFileInput.className = 'input-group mb-3';
    newFileInput.innerHTML = `
        <input type="file" name="file${fileInputCount + 1}" id="upfile${fileInputCount + 1}" class="form-control" required>
        <label for="upfile${fileInputCount + 1}" class="input-group-text"><i class="bi bi-cloud-arrow-up-fill"></i></label>
        <button type="button" class="btn btn-danger btn-sm remove-file-input">删除</button>
    `;
    fileInputs.appendChild(newFileInput);
});

document.getElementById('file-inputs').addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-file-input')) {
        var fileInputs = document.getElementById('file-inputs');
        if (fileInputs.getElementsByClassName('input-group').length > 1) {
            event.target.parentElement.remove();
        }
    }
});