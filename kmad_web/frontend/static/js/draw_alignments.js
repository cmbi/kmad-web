color_to_hex = {'gray':'#CCCCCC', 'red': '#FF9999', 'green':'#ADEFAD',
                'yellow':'#FFFF75', 'blueishgreen': '#5EDFBF', 'blue':'#91DAFF',
                'purple':'#BD9DFF', 'pink':'#FFACD6', 'white':'#FFFFFF'};

aa_to_color = {'C': 'yellow', 'M': 'yellow',
               'V': 'green', 'A': 'green', 'I': 'green', 'L': 'green', 
               'F': 'green',
               'S': 'blueishgreen', 'T': 'blueishgreen', 'Y': 'blueishgreen',
               'H': 'blue',
               'K': 'purple', 'R': 'purple',
               'E': 'red', 'Q': 'red',
               'N': 'pink', 'D': 'pink',
               'G': 'gray', 'P': 'gray', 'W': 'gray',
               '-': 'white'};

draw_alignment = function(canvas_id, data) {
  const ROW_HEIGHT = 15;
  const ROWS = data.length;
  aa_to_hex ={};
  for (key in aa_to_color) {
    aa_to_hex[key] = color_to_hex[aa_to_color[key]];
  }
  var start = Date.now();
  var ctx=$("#" + canvas_id).get(0).getContext("2d");
  document.getElementById(canvas_id).width = data[0][1].length * 11;
  var container_height = ROWS * ROW_HEIGHT * 1.6;
  document.getElementById(canvas_id).height = ROWS * ROW_HEIGHT * 1.5;
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var x = 10;
  var y = 30;
  ctx.fillStyle = "#515454";
  for (var i = 0; i < data.length; i++) {
    y = 30 + i * ROW_HEIGHT;
    ctx.fillText(data[i][0], x, y)
  }
  var res;
  for (var i = 0; i < data.length; i++) {
    x = 160;
    y = 20 + (i * ROW_HEIGHT);
    for (var j = 0; j < data[i][1].length; j++) {
      res = data[i][1].charAt(j);
      ctx.fillStyle = aa_to_hex[res.toUpperCase()];
      ctx.fillRect(x,y,10,15);
      ctx.fillStyle = "#000000";
      ctx.fillText(res, x + 1, y + 10)
      x += 10;
    }
  }
  console.debug("draw_alignment");
  console.debug(Date.now() - start);
}


register_tooltip = function(src, x, y, message, t_layer, feature_type) {
  var tooltip;
  if (feature_type == "motifs") {
    var url = 'http://elm.eu.org/elmPages/'+message+'.html';
  } else {
    var url = 'http://pfam.xfam.org/family/'+message;
  }  
  var left_button_clicked = false;
  src.on('mousedown', function(e) {
    if (e.evt.buttons == 1 || e.evt.keyCode == 0) {
      left_button_clicked = true;
    }
  });
  src.on('click', function(e) {
    if (left_button_clicked) {
      window.open(url);
      left_button_clicked = false;
    }
  });
  src.on('mouseover', function(e) {
    tooltip = draw_tooltip(e.evt.layerX, e.evt.layerY, message, t_layer);
  });
  src.on('mouseout', function() {
    tooltip.destroy();
    t_layer.draw();
  });
}


draw_tooltip = function(x, y, message, t_layer) {
  tooltip = new Kinetic.Label({
    x: x,
    y: y,
    opacity: 0.75
  });
  tooltip_tag = new Kinetic.Tag({
    fill: 'gray',
    pointerDirection: 'up',
    pointerWidth: 10,
    pointerHeight: 10,
    lineJoin: 'round',
    shadowColor: 'black',
    shadowBlur: 3,
    shadowOffset: {x:2, y:2},
    shadowOpacity: 0.5
  });
  tooltip_text = new Kinetic.Text({
    text: message,
    fontFamily: "Monospace",
    fontSize: 15,
    padding: 5,
    fill: 'white'
  });
  tooltip.add(tooltip_tag);
  tooltip.add(tooltip_text);
  t_layer.add(tooltip);
  t_layer.draw();
  return tooltip;
};


create_tooltip = function(feature_coords, feature_names, shapes_layer, t_layer,
    feature_type) {
  for (var i = 0; i < feature_coords.length; i++) {
    var rect = new Kinetic.Rect({
         x: feature_coords[i][0],
         y: feature_coords[i][1],
         width: feature_coords[i][2],
         height: feature_coords[i][3],
         fill: null,
         stroke: null,
         strokeWidth: 4
    });
    shapes_layer.add(rect);
    register_tooltip(rect, feature_coords[i][0], feature_coords[i][1] + 10,
        feature_names[i], t_layer, feature_type);
  }
  shapes_layer.draw();
}


group_coords = function(feature_coords, feature_names) {
  var single_width = feature_coords[0][2];
  var new_coords = [];
  var new_names = [];
  var new_block = feature_coords[0];
  for (var i = 1; i < feature_coords.length; i++) {
    if (feature_names[i] == feature_names[i - 1] 
        && feature_coords[i][0] == feature_coords[i - 1][0] + single_width
        && feature_coords[i][1] == feature_coords[i - 1][1]) {
      new_block[2] += single_width;
    } else {
      new_coords.push(new_block);
      new_names.push(feature_names[i - 1]);
      new_block = feature_coords[i];
    }
  }
  return [new_coords, new_names];
}


draw_alignment_with_features = function(container_id, data, codon_length,
    feature_codemap, feature_type) {
  var start = Date.now();
  const ROW_HEIGHT = 15;
  const ROWS = data.length;
  const FONT_SIZE = 13;
  const FONT_FAMILY = "Monospace";

  var container_width = data[0][1].length * 1.75;
  var container_height = ROWS * ROW_HEIGHT * 1.5 + 20;

  var stage = new Kinetic.Stage({
    container: container_id,
    width: container_width,
    height: container_height,
    listening: true

  });

  var tooltip_layer = new Kinetic.Layer();
  var shapes_layer = new Kinetic.Layer();
  var native_layer = new Kinetic.Layer();
  stage.add(native_layer);
  stage.add(tooltip_layer);
  stage.add(shapes_layer);

  document.getElementById(container_id).style.width = container_width;
  document.getElementById(container_id).style.height = container_height;
  document.getElementById("canvases").style.height = (container_height + 20).toString() + 'px';
  

  var shaded_to_hex = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
                       'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0',
                       'blue':'#CFEFFF', 'purple':'#DECFFF', 'pink':'#FFCCE6',
                       'white':'#FFFFFF'};
  aa_to_hex ={};
  for (key in aa_to_color) {
    aa_to_hex[key] = shaded_to_hex[aa_to_color[key]];
  }
  // color spectrum for features
  var feature_colors = ColorRange(feature_codemap.length);
  var ctx = native_layer.getContext()._context;
  var index_add = 0;
  var char_index = 7;
  if (feature_type == 'motifs') {
    index_add = 3;
    char_index = 6;
  }
  var feature_code;
  var r;
  var r_up;
  var letter_col;
  var rect_width = 10;
  var rect_height = 15;
  var is_feature;
  var feature_coords = [];
  var feature_names = [];
  draw_residue = function(res_num, seq_num, x, y) {
    feature_code = data[seq_num][1].substring(res_num + 2 + index_add,
                                              res_num + 4 + index_add);

    r = data[seq_num][1].charAt(res_num);

    letter_col = color_to_hex['gray'];
    if (feature_code == 'AA') {
      letter_col = aa_to_hex[r.toUpperCase()];
    }
    else {
      var feat_number = 0;
      for (var i = 0; i < feature_codemap.length; i++) {
        if (feature_codemap[i][0] == feature_code) {
          feat_number = i;
          break;    
        }
      }
      feature_coords = feature_coords.concat([[x, y, rect_width, rect_height]]);
      feature_names = feature_names.concat(feature_codemap[feat_number][1]);
      letter_col = feature_colors[feat_number];
    }
      ctx.fillStyle = letter_col;
      ctx.fillRect(x, y, rect_width, rect_height);
      ctx.fillStyle = "#000000";
      ctx.fillText(r, x + 1, y + 10)
  }
  // 
  var x = 10;
  var y = 30;
  ctx.fillStyle = "#515454";
  for (var i = 0; i < data.length; i++) {
    y = 30 + i * ROW_HEIGHT;
    ctx.fillText(data[i][0], x, y)
  }
  for (var i = 0; i < data.length; i++) {
    x = 160;
    y = 20+(i * ROW_HEIGHT);
    for (var j = 0; j < data[i][1].length; j+=codon_length) {
      draw_residue(j, i, x, y);
      x += 10;
    }
  }
  [feature_coords, feature_names] = group_coords(feature_coords, feature_names);
  create_tooltip(feature_coords, feature_names, shapes_layer,
      tooltip_layer, feature_type);
  console.debug("draw_alignmenti_with_features");
  console.debug(Date.now() - start);
}

draw_alignment_ptms = function(canvas_id, data, codon_length) {
  var start = Date.now();
  const ROW_HEIGHT = 15;
  const ROWS = data.length;
  const FONT_SIZE = 13;
  const FONT_FAMILY = "Monospace";
  document.getElementById(canvas_id).width = data[0][1].length * 1.75;
  var container_height = ROWS * ROW_HEIGHT * 1.6;
  document.getElementById(canvas_id).height = ROWS * ROW_HEIGHT * 1.5;
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var shaded_to_hex = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
                       'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0',
                       'blue':'#CFEFFF', 'purple':'#DECFFF', 'pink':'#FFCCE6',
                       'white':'#FFFFFF'};
  var ptm_colors = {"N": "#FF0000", "O": "#FF4000",
                    "P": "#FF5000", "Q": "#FF6000",
                    "d": "#FFAA00", "B": "#0000FF",
                    "C": "#0090FF", "D": "#00A5FF",
                    "E": "#00BAFF", "F": "#078207",
                    "G": "#09B009", "H": "#06D606",
                    "I": "#07F507", "J": "#FAF600",
                    "K": "#EFFC56", "L": "#FAFA87",
                    "M": "#FAFAAF", "R": "#7D4C0B",
                    "S": "#94611E", "T": "#B5803C",
                    "U": "#DBA967", "V": "#601385",
                    "W": "#7F31A3", "X": "#A45EC4",
                    "Y": "#C384E0", "Z": "#F002EC",
                    "a": "#F55FF2", "b": "#F57FF3",
                    "c": "#F2A5F1"}
  aa_to_hex ={};
  for (key in aa_to_color) {
    aa_to_hex[key] = shaded_to_hex[aa_to_color[key]];
  }
  // color spectrum for features
  var ctx=$("#" + canvas_id).get(0).getContext("2d");
  var feature_code;
  var r;
  var r_up;
  var letter_col;
  var is_feature;
  var ptm_code;


  draw_residue = function(res_num, seq_num, x, y) {
    r = data[seq_num][1].charAt(res_num);
    r_up = r.toUpperCase(); 
    letter_col = aa_to_hex['gray'];
    ptm_code = data[seq_num][1].charAt(res_num + 4);
    if (ptm_code == 'A') {
      letter_col = aa_to_hex[r_up];
    }
    else {
      letter_col = ptm_colors[ptm_code];
    }
    ctx.fillStyle = letter_col;
    ctx.fillRect(x, y, 10, 15);
    ctx.fillStyle = "#000000";
    ctx.fillText(r, x + 1, y + 10)
  }


  // 
  var x = 10;
  var y = 30;
  ctx.fillStyle = "#515454";
  for (var i = 0; i < data.length; i++) {
    y = 30 + i * ROW_HEIGHT;
    ctx.fillText(data[i][0], x, y)
  }
  for (var i = 0; i < data.length; i++) {
    x = 160;
    y = 20+(i * ROW_HEIGHT);
    for (var j = 0; j < data[i][1].length; j += codon_length) {
      draw_residue(j, i, x, y);
      x += 10;
    }
  }
  console.debug("draw_alignment_ptms");
  console.debug(Date.now() - start);
}
