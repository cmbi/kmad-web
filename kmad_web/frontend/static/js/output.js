changeMode = function(newMode) {
  modes = ["regular", "ptm", "domain", "motif"];
  $('#' + newMode + '_mode_button').addClass('disabled');
  if (newMode != "regular") {
    document.getElementById('legend_canvases_container').style.display = ''; 
    document.getElementById('legend_canvas_' + newMode).style.display = ''; 
  } else {
    document.getElementById('legend_canvases_container').style.display = 'none'; 
  }
  document.getElementById('canvas_' + newMode).style.display = ''; 
  document.getElementById('download_' + newMode + '_canvas_button').style.display = ''; 
  for (i in modes) {
    m = modes[i];
    if (m != newMode) {
      document.getElementById('canvas_' + m).style.display = 'none'; 
      document.getElementById(
          'download_' + m + '_canvas_button').style.display = 'none'; 
      $('#' + m + '_mode_button').removeClass('disabled');
      $('#' + m + '_mode_button').removeClass('active');
      if (m != "regular") {
        document.getElementById('legend_canvas_' + m).style.display = 'none'; 
      }
    }
  }
}
