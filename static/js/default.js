var editor = CodeMirror.fromTextArea(document.getElementById("code_area"), {
	lineNumbers: true,
	styleActiveLine: true,
	matchBrackets: true
});

var theme_select = document.getElementById("theme_select");

function selectTheme() {
	var theme = theme_select.options[theme_select.selectedIndex].innerHTML;
	editor.setOption("theme", theme);
}
window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
}, 3000);
