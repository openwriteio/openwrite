document.addEventListener('DOMContentLoaded', function () {
    var textareas = document.getElementsByTagName('textarea');

    for(var i = 0; i < textareas.length; i++) {
        textareas[i].addEventListener('keydown', function(e) {
            if (e.key == 'Tab') {
                e.preventDefault();
                var start = this.selectionStart;
                var end = this.selectionEnd;

                this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
                
                this.selectionStart = this.selectionEnd = start + 4;
            }
            if (e.key == 'Enter') {
                var start = this.selectionStart;
                var lineStart = this.value.lastIndexOf('\n', start - 1);
                if (lineStart === -1) lineStart = 0;
                else lineStart += 1;

                var currentline = this.value.slice(lineStart, start);
                var match = currentline.match(/^([\s\-\*]+)/);

                var indent = match ? match[1] : "";

                e.preventDefault();
                var before = this.value.slice(0, start);
                var after = this.value.slice(this.selectionEnd);
                this.value = before + "\n" + indent + after;

                var cursor = start + 1 + indent.length;
                this.selectionStart = this.selectionEnd = cursor;
            }
        });
    }


    var dates = document.getElementsByClassName("datetime");
    for(var i = 0; i < dates.length; i++) {
        const utc = dates[i].innerText;
        const [datePart, timePart] = utc.split(" ");
        const [year, month, day] = datePart.split("-").map(Number);
        const [hour, min, sec] = timePart.split(":").map(Number);
        const localdate = new Date(Date.UTC(year, month - 1, day, hour, min, sec));
        dates[i].innerText = localdate.toLocaleString(undefined, {
        year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
        });
    }

    var imgs = document.getElementsByTagName("img");
    for(var i = 0; i < imgs.length; i++) {
        if(imgs[i].attributes.title != undefined) {
            var caption = document.createElement("i");
            caption.classList.add("caption");
            caption.innerText = imgs[i].attributes.title.value;
            imgs[i].parentElement.appendChild(caption);
            //imgs[i].parentElement.classList.add("column");
        }
    }
});

function escapeHtml(text) {
    var map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function getUTCDate() {
    const now = new Date(); 
    const utcYear = now.getUTCFullYear();
    const utcMonth = String(now.getUTCMonth() + 1).padStart(2, '0'); 
    const utcDate = String(now.getUTCDate()).padStart(2, '0');
    const utcHours = String(now.getUTCHours()).padStart(2, '0');
    const utcMinutes = String(now.getUTCMinutes()).padStart(2, '0');
    const utcSeconds = String(now.getUTCSeconds()).padStart(2, '0');

    return `${utcYear}-${utcMonth}-${utcDate} ${utcHours}:${utcMinutes}:${utcSeconds}`;
}
