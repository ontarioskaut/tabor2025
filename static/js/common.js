function handleForms(event, url) {
    event.preventDefault();
    const formData = new FormData(event.target);
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('Operation successful!');
            window.location.reload();
        }
    })
    .catch(error => {
        alert('An error occurred: ' + error);
    });
}
