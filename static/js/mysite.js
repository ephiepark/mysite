function addTextToCursor(el, newText) {
  var start = el.prop("selectionStart");
  var end = el.prop("selectionEnd");
  var text = el.val();
  var before = text.substring(0, start);
  var after  = text.substring(end, text.length);
  el.val(before + newText + after);
  el[0].selectionStart = el[0].selectionEnd = start + newText.length;
  el.focus();
  console.log("being called");
}
