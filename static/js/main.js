document.getElementById('upload-form').onsubmit = function(event) {
    event.preventDefault();
    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/', true);

    xhr.onload = function() {
        if (xhr.status == 202) {
            var job_id = JSON.parse(xhr.responseText).job_id;
            document.getElementById('progress-bar').style.display = 'block';
            document.getElementById('spinner').style.display = 'block';
            pollProgress(job_id);
        } else {
            console.error("Failed to start transcription, status: " + xhr.status);
        }
    };

    xhr.onerror = function() {
        console.error("Request failed");
    };

    xhr.send(formData);
};

function pollProgress(job_id) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/progress/' + job_id, true);
    xhr.onload = function() {
        if (xhr.status == 200) {
            var data = JSON.parse(xhr.responseText);
            document.getElementById('progress').style.width = data.progress + '%';
            document.getElementById('status').innerText = 'Processing chunk ' + data.processed_chunks + ' of ' + data.total_chunks + ' (' + Math.round(data.elapsed_time) + 's elapsed, ' + Math.round(data.remaining_time) + 's remaining)';
            document.getElementById('transcript').innerText = data.transcript;

            if (!data.complete) {
                setTimeout(function() {
                    pollProgress(job_id);
                }, 1000);
            } else {
                document.getElementById('spinner').style.display = 'none';
                document.getElementById('copy-button').style.display = 'block';
            }
        } else {
            console.error("Failed to load progress, status: " + xhr.status);
        }
    };
    xhr.send();
}

function copyToClipboard() {
    var text = document.getElementById("transcript").innerText;
    navigator.clipboard.writeText(text).then(function() {
        alert("Transcript copied to clipboard!");
    }, function() {
        alert("Failed to copy transcript to clipboard.");
    });
}
