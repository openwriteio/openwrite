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
        dates[i].innerText = localdate.toLocaleString();
    }
});
