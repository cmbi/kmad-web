ProteinSequences = function(container_id, data, sequence) {
  // TODO: Check arguments are same length
  // TODO: Private methods are actually publicly visible.
  // TODO: All methods are recreated per instance. Is this a problem?
  // TODO: Fit to canvas width.
  // TODO: Resize canvas when browser resized.
  // TODO: Pass settings in constructor
  // TODO: Smarter positioning of (long) tooltips
  // TODO: Multiple types of info in tooltips

  // Constants
  this.methods = ['filtered', 'consensus'];
  for (var m in data) {
      if (m != 'consensus' && m != 'filtered'){
        this.methods.push(m);
      }
  }
  const MAX_RES_PER_ROW = data[this.methods[0]].length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 16;
  const ROW_HEIGHT = 36;
  const ROW_MARGIN_T = 0;
  const ROWS = this.methods.length + 1;

  // Attributes
  this.seq = sequence;
  this.data = data;
  var container_height = ROWS * ROW_HEIGHT;
  document.getElementById(container_id).style.height = (container_height + 60).toString() + 'px';
  var cont_width = 350 + MAX_RES_PER_ROW * 10;
  if (cont_width < 650) {
    cont_width = 650;
  }
  if (cont_width > 30000 || container_height > 30000) {
      document.getElementById("canvases").style.display="none";
      document.getElementById("collapseTwo").style.display="none";
      window.alert("Sorry, this sequence is too long to visualize the prediction. You can still download the text file with prediction.");
      return 0;
  }
  var stage = new Kinetic.Stage({
    container: container_id,
    width: cont_width,
    height: ROWS * ROW_HEIGHT + 25
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();


  // Private methods
  this.draw_residue = function(res_num, method, x, y) {
    var r = this.seq.charAt(res_num);
    var d = this.data[method][res_num];
     
    var letter_col;
    if (d == 0){
        letter_col = 'green';
    } 
    else if (d == 2) {
      letter_col = 'red';
    }
    else{
        letter_col = 'orange';
    }
    
    var res_text = new Kinetic.Text({
      x: x,
      y: y,
      text: r,
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: letter_col
    });

    var res_text_w = res_text.getTextWidth();
    var res_text_h = res_text.getTextHeight();

    this.seq_layer.add(res_text);

    return res_text_w;
  }

  this.draw = function() {
    //var rows = Math.ceil(seq.length / MAX_RES_PER_ROW);
    var v_header_width = 0;
    var x = 10;
    var y = 20 + ROW_MARGIN_T; 
    var res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: 'A',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'red'
    });
    x += res_num_leg.getTextWidth();
    this.v_header_layer.add(res_num_leg);
    res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: ' - disordered  ',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'gray'
    });
    x += res_num_leg.getTextWidth();
    this.v_header_layer.add(res_num_leg);
    res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: 'A',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'orange'
    });
    x += res_num_leg.getTextWidth();
    this.v_header_layer.add(res_num_leg);
    res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: ' - ambiguous disorder prediction  ',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'gray'
    });
    x += res_num_leg.getTextWidth();
    this.v_header_layer.add(res_num_leg);
    res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: 'A',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'green'
    });
    x += res_num_leg.getTextWidth();
    this.v_header_layer.add(res_num_leg);
    res_num_leg = new Kinetic.Text({
      x: x,
      y: y,
      text: ' - structured ',
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'gray'
    });
    this.v_header_layer.add(res_num_leg);

    for (var i = 0; i < this.methods.length; i++) {
      x = 10;
      y = 40 + ((i + 1) * ROW_HEIGHT) + ROW_MARGIN_T;

      // Draw the method name
      var method_name = new Kinetic.Text({
        x: x,
        y: y,
        text: this.methods[i],       //method name
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'gray'
      });
      this.v_header_layer.add(method_name);
      var method_name_w = method_name.getWidth();
      v_header_width = (
         method_name_w > v_header_width ? method_name_w : v_header_width);

      // iterate over all residues, use the colour according to the disorder
      // prediction
      for (var j = 0; j < this.seq.length; j++)
      {
        var res_text_width = this.draw_residue(j, this.methods[i], x, y);
        x = x + res_text_width;
      }
    }
    x = 50;
    y = 55;
    for (var i = 0; i < MAX_RES_PER_ROW; i++) {
      if (i % 5 == 0) {
        var ruler_text = new Kinetic.Text({
          x: x,
          y: y,
          text: i.toString(),
          fontSize: FONT_SIZE - 6,
          fontStyle: 'bold',
          fontFamily: FONT_FAMILY,
          fill: 'gray'
        });
        var tick  = new Kinetic.Text({
          x: x,
          y: y + 10,
          text: '|',
          fontSize: FONT_SIZE - 7,
          fontStyle: 'bold',
          fontFamily: FONT_FAMILY,
          fill: 'gray'
        });
        this.seq_layer.add(ruler_text);
        this.seq_layer.add(tick);
        x += 50;
      }
    }

    this.v_header_layer.width(v_header_width);
    var v_header_width = this.v_header_layer.getWidth();
    this.seq_layer.x(v_header_width + SEQ_LAYER_OFFSET_X);

    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }

  // Public methods
  this.update = function() {
    this.draw();
  }

};

RGBtoHEX = function(r, g, b) {
  var hexcode = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1,7);
  return hexcode;
}
HSLtoHEX = function(h, s, l) {
  var c = (1 - Math.abs(2*l - 1)) *s;
  var x = c * (1 - Math.abs((h / 60) % 2 - 1));
  var m = l - c / 2;
  var r_p;
  var g_p;
  var b_p;
  if (h >= 0 && h < 60 ) {
    r_p = c;
    g_p = x;
    b_p = 0; 
  }
  else if (h >= 60 && h < 120 ) {
    r_p = x;
    g_p = c;
    b_p = 0; 
  }
  else if (h >= 120 && h < 180 ) {
    r_p = 0;
    g_p = c;
    b_p = x; 
  }
  else if (h >= 180 && h < 240 ) {
    r_p = 0;
    g_p = x;
    b_p = c; 
  }
  else if (h >= 240 && h < 300 ) {
    r_p = x;
    g_p = 0;
    b_p = c; 
  }
  else if (h >= 300 && h < 360 ) {
    r_p = c;
    g_p = 0;
    b_p = x; 
  }
  var r = Math.floor(255 * (r_p + m));
  var g = Math.floor(255 * (g_p + m));
  var b = Math.floor(255 * (b_p + m));
  return RGBtoHEX(r, g, b);
}

ColorRange = function(number) {
  var norm = 100 / number;
  result = [];
  var frequency = Math.PI*2 / number;
  for (var i = 0; i < number; i++) {
    var r = Math.sin(frequency*i + 0) * 127 + 128;
    var g = Math.sin(frequency*i + 2) * 127 + 128;
    var b = Math.sin(frequency*i + 4) * 127 + 128;
    result.push(RGBtoHEX(r, g, b));

  }
  return result;
}

PTMsLegend = function(container_id) {
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  
  //var container_height = 40*this.data.length;
  var container_height = 200;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("legend_canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: 185,
    width: 900 
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  colors = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
            'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0', 'blue':'#CFEFFF',
            'purple':'#DECFFF', 'pink':'#FFCCE6', 'white':'#FFFFFF'};
  ptm_colors = {"N": "#FF0000", "O": "#FF4000",
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
  this.draw_residue = function(res_char, ptm_code, x, y) {
    var letter_col = ptm_colors[ptm_code];
    var rect_w = 10;
    var rect_h = 15;

    var text_rect = new Kinetic.Rect({
        x: x-0.25,
        y: y,
        width: rect_w,
        height: rect_h,
        fill: letter_col,
    });
    
    this.seq_layer.add(text_rect);
  }
  this.draw = function() {
    var x = 10;
    var y = 20;
    var res_text = new Kinetic.Text({
      x: x,
      y: y,
      text: "Color intensities indicate the level of annotation",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'grey'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'N', x, y);
    this.draw_residue(' ', 'O', x + 10, y);
    this.draw_residue(' ', 'P', x + 20, y);
    this.draw_residue(' ', 'Q', x + 30, y);
    this.draw_residue(' ', 'd', x + 40, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "phosphorylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'B', x, y);
    this.draw_residue(' ', 'C', x + 10, y);
    this.draw_residue(' ', 'D', x + 20, y);
    this.draw_residue(' ', 'E', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "acetylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'F', x, y);
    this.draw_residue(' ', 'G', x + 10, y);
    this.draw_residue(' ', 'H', x + 20, y);
    this.draw_residue(' ', 'I', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "N-glycosylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'J', x, y);
    this.draw_residue(' ', 'K', x + 10, y);
    this.draw_residue(' ', 'L', x + 20, y);
    this.draw_residue(' ', 'M', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "amidated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'R', x, y);
    this.draw_residue(' ', 'S', x + 10, y);
    this.draw_residue(' ', 'T', x + 20, y);
    this.draw_residue(' ', 'U', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "hydroxylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    y = 50;
    x += 300;
    this.draw_residue(' ', 'V', x, y);
    this.draw_residue(' ', 'W', x + 10, y);
    this.draw_residue(' ', 'X', x + 20, y);
    this.draw_residue(' ', 'Y', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "methylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    y = y + 30; 
    this.draw_residue(' ', 'Z', x, y);
    this.draw_residue(' ', 'a', x + 10, y);
    this.draw_residue(' ', 'b', x + 20, y);
    this.draw_residue(' ', 'c', x + 30, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "O-glycosylated residues",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    this.seq_layer.add(res_text);
    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}

register_link = function(src, name, feature_type, canvas_id) {
  if (feature_type == "motif") {
    var url = 'http://elm.eu.org/elms/'+name+'.html';
  } else {
    var url = 'http://pfam.xfam.org/family/'+name;
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
    $('#' + canvas_id).css('cursor', 'pointer');
  });
  src.on('mouseleave', function(e) {
    $('#' + canvas_id).css('cursor', 'auto');
  });
}

StructureLegend = function(container_id) {
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  
  //var container_height = 40*this.data.length;
  var container_height = 200;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("legend_canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: 185,
    width: 900 
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  var color_map = {'T': '#49ce6c', 'H': '#3e87d8', 'S': '#e15555',
      'C': '#e1d131', 'M': '#4e63ce'
  }

  this.draw_residue = function(res_char, strct_code, x, y) {
    var letter_col = color_map[strct_code];
    var rect_w = 10;
    var rect_h = 15;

    var text_rect = new Kinetic.Rect({
        x: x-0.25,
        y: y,
        width: rect_w,
        height: rect_h,
        fill: letter_col,
    });
    
    this.seq_layer.add(text_rect);
  }
  this.draw = function() {
    var x = 10;
    var y = 20;
    this.draw_residue('      ', 'H', x, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "helix",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    y += 30;
    this.seq_layer.add(res_text);
    this.draw_residue('      ', 'M', x, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "transmembrane helix",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    y += 30;
    this.seq_layer.add(res_text);
    this.draw_residue('      ', 'T', x, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "turn",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    y += 30;
    this.seq_layer.add(res_text);
    this.draw_residue('      ', 'S', x, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "strand",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    y += 30;
    this.seq_layer.add(res_text);
    this.draw_residue('      ', 'C', x, y);
    var res_text = new Kinetic.Text({
      x: x + 60,
      y: y,
      text: "cysteine bridge",
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });
    y += 30;
    this.seq_layer.add(res_text);
    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
