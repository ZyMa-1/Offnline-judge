var editor = CodeMirror.fromTextArea(document.getElementById("code_area"), {
	lineNumbers: true,
	styleActiveLine: true,
	matchBrackets: true,
	readOnly: true,
	showCursorWhenSelecting: false,
	tabSize: 4,
});
editor.setSize(null, 600);

var theme_select = document.getElementById("theme_select");

function selectTheme() {
	var theme = theme_select.options[theme_select.selectedIndex].innerHTML;
	editor.setOption("theme", theme);
}
function copyCode(element) {
    var $temp = $("<textarea>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
    document.getElementById('copy_button').value = "Copied";
    $(element).toggleClass('btn-outline-dark');
    $(element).toggleClass('btn-dark');
}