var editor = CodeMirror.fromTextArea(document.getElementById("code_area"), {
	lineNumbers: true,
	styleActiveLine: true,
	matchBrackets: true,
	tabSize: 4,
});
editor.setSize(null, 600);

var theme_select = document.getElementById("theme_select");

function selectTheme() {
	var theme = theme_select.options[theme_select.selectedIndex].innerHTML;
	editor.setOption("theme", theme);
}
function refreshCode() {
    editor.setOption("theme", "darcula");
}
window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
}, 3000);
