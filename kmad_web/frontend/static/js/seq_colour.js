ProteinSequences = function(container_id, data) {

  // Constants
  const MAX_RES_PER_ROW = data[1][1].length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 16;
  const ROW_HEIGHT = 36;
  const ROW_MARGIN_T = 0;
  const ROWS = data.length;


  // Attributes
  this.seq = data[0];
  this.disorder = [];
  for (var i = 1; i < data.length; i++){
    this.disorder.push(data[i])
  }
  console.debug(this.seq);
  console.debug(this.disorder);
  var container_height = ROWS * ROW_HEIGHT;
  document.getElementById(container_id).style.height = (container_height + 60).toString() + 'px';
  var cont_width = 150 + this.disorder[0][1].length * 10;
  if (cont_width < 650) {
    cont_width = 650;
  }
  var stage = new Kinetic.Stage({
    container: container_id,
    width: cont_width,
    height: ROWS * ROW_HEIGHT + 25
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();

  // Private methods
  this.draw_residue = function(res_num, seq_num, x, y) {
    var r = this.seq.charAt(res_num);
    var d = this.disorder[seq_num][1][res_num];
     
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
    for (var i = 0; i < this.disorder.length; i++) {
      //var x = 0;
      //var y = (i * ROW_HEIGHT) + ROW_MARGIN_T;
      x = 10;
      y = 20 + ((i + 1) * ROW_HEIGHT) + ROW_MARGIN_T;

      // Draw the residue number heading
      var res_num_txt = new Kinetic.Text({
        x: x,
        y: y,
        text: this.disorder[i][0],       //method name
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'gray'
      });
      this.v_header_layer.add(res_num_txt);
      var res_num_txt_w = res_num_txt.getWidth();
      v_header_width = (
          res_num_txt_w > v_header_width ? res_num_txt_w : v_header_width);

      // Calculate the number of residues for the current row. The default is
      // to draw 60, but the last row often has less.
      if (i == this.disorder.length - 1) {
        num_res_in_row = this.disorder[i][1].length - (i * MAX_RES_PER_ROW);
      } else {
        num_res_in_row = MAX_RES_PER_ROW;
      }
      // Iterate over the residues in the current row. For each residue, draw
      // it with the appropriate accessibility colour, and draw the secondary
      // structure representation.
      for (var j = 0; j < this.disorder[i][1].length; j++)
      {
        var res_text_width = this.draw_residue(j, i, x, y);
        x = x + res_text_width;
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
SequenceAlignment = function(container_id, data) {
  const MAX_RES_PER_ROW = data[0][1].length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  const ROWS = data.length;
  
  this.data = data;
  //var container_height = 40*this.data.length;
  var container_height = ROWS * ROW_HEIGHT + 45;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 25,
    width: 170 + (this.data[0][0].length + this.data[0][1].length)*8
  });
  document.getElementById('download_canvas_button').addEventListener('click',
      function() {
        stage.toDataURL({
          callback: function(dataUrl) {
            window.open(dataUrl);
          }
        });
  }, false);
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  colors = {'gray':'#CCCCCC','red': '#FF9999','green':'#ADEFAD', 'yellow':'#FFFF75', 'blueishgreen': '#5EDFBF', 'blue':'#91DAFF', 'purple':'#BD9DFF', 'pink':'#FFACD6', 'white':'#FFFFFF'};
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
  this.draw_residue = function(res_num, seq_num, x, y) {
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = color_to_hex[aa_to_color[r_up]]
    var res_text = new Kinetic.Text({
      x: x,
      y: y,
      text: r,
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });

    var res_text_w = res_text.getTextWidth();
    var res_text_h = res_text.getTextHeight();
    var rect_w = res_text_w + 1;
    var rect_h = res_text_h;
    
    var text_rect = new Kinetic.Rect({
        x: x-0.25,
        y: y,
        width: res_text_w+1,
        height: res_text_h,
        fill: letter_col,
    });
    
    this.seq_layer.add(text_rect);
    this.seq_layer.add(res_text);

    return res_text_w;
  }
  this.draw = function() {
    var v_header_width = 0;
    for (var i = 0; i < this.data.length; i++) {
      var x = 10;
      var y = 20+(i * ROW_HEIGHT) + ROW_MARGIN_T;

      // Draw the residue number heading
      var res_num_txt = new Kinetic.Text({
        x: x,
        y: y,
        text: this.data[i][0],       //sequence header
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'gray'
      });
      this.v_header_layer.add(res_num_txt);
      var res_num_txt_w = res_num_txt.getWidth();
      v_header_width = (
          res_num_txt_w > v_header_width ? res_num_txt_w : v_header_width);

      // Iterate over the residues in the current row. For each residue, draw
      // it with the appropriate accessibility colour, and draw the secondary
      // structure representation.
      for (var j = 0; j < this.data[i][1].length; j++)
      {
        var res_text_width = this.draw_residue(j, i, x, y);
        x = x + res_text_width;
      }
    }

    this.v_header_layer.width(v_header_width);
    var v_header_width = this.v_header_layer.getWidth();
    this.seq_layer.x(v_header_width + SEQ_LAYER_OFFSET_X);

    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
SequenceAlignmentPTMs = function(container_id, data, codon_length) {
  const MAX_RES_PER_ROW = data[0][1].length / codon_length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  const ROWS = data.length;
  
  this.data = data;
  //var container_height = 40*this.data.length;
  var container_height = ROWS * ROW_HEIGHT + 45;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 25,
    width: 170 + (this.data[0][0].length + this.data[0][1].length / codon_length)*8
  });
  document.getElementById('download_ptms_canvas_button').addEventListener('click',
      function() {
        stage.toDataURL({
          callback: function(dataUrl) {
            window.open(dataUrl);
          }
        });
  }, false);
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  color_to_hex = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
                  'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0', 'blue':'#CFEFFF',
                  'purple':'#DECFFF', 'pink':'#FFCCE6', 'white':'#FFFFFF'};

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
  ptm_colors = {"N": "#FF0000", "O": "#FF4000",
                "P": "#FF8000", "Q": "#FF9800",
                "d": "#FF9F00", "B": "#0000FF",
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
  this.draw_residue = function(res_num, seq_num, x, y) {
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    var ptm_code = this.data[seq_num][1].charAt(res_num + 4);
    if (ptm_code == 'A') {
      letter_col = color_to_hex[aa_to_color[r_up]];
    }
    else {
      letter_col = ptm_colors[ptm_code];
    }
    var res_text = new Kinetic.Text({
      x: x,
      y: y,
      text: r,
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });

    var res_text_w = res_text.getTextWidth();
    var res_text_h = res_text.getTextHeight();
    var rect_w = res_text_w + 1;
    var rect_h = res_text_h;
    
    var text_rect = new Kinetic.Rect({
        x: x-0.25,
        y: y,
        width: res_text_w+1,
        height: res_text_h,
        fill: letter_col,
    });
    
    this.seq_layer.add(text_rect);
    this.seq_layer.add(res_text);

    return res_text_w;
  }
  this.draw = function() {
    var v_header_width = 0;
    for (var i = 0; i < this.data.length; i++) {
      var x = 10;
      var y = 20+(i * ROW_HEIGHT) + ROW_MARGIN_T;

      // Draw the residue number heading
      var res_num_txt = new Kinetic.Text({
        x: x,
        y: y,
        text: this.data[i][0],       //sequence header
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'gray'
      });
      this.v_header_layer.add(res_num_txt);
      var res_num_txt_w = res_num_txt.getWidth();
      v_header_width = (
          res_num_txt_w > v_header_width ? res_num_txt_w : v_header_width);

      // Iterate over the residues in the current row. For each residue, draw
      // it with the appropriate accessibility colour, and draw the secondary
      // structure representation.
      for (var j = 0; j < this.data[i][1].length / codon_length; j++)
      {
        var res_text_width = this.draw_residue(j * codon_length, i, x, y);
        x = x + res_text_width;
      }
    }

    this.v_header_layer.width(v_header_width);
    var v_header_width = this.v_header_layer.getWidth();
    this.seq_layer.x(v_header_width + SEQ_LAYER_OFFSET_X);

    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}

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
    // var hue = Math.floor((100 - i * norm) * 120 / 100);
    // // var saturation = Math.abs(i * norm - 50) / 50;
    // var saturation = 1;
    // result.push(HSLtoHEX(hue, saturation, 0.5));
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
    width: 400 
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  colors = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
            'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0', 'blue':'#CFEFFF',
            'purple':'#DECFFF', 'pink':'#FFCCE6', 'white':'#FFFFFF'};
  ptm_colors = {"N": "#FF0000", "O": "#FF4000",
                "P": "#FF8000", "Q": "#FF9800",
                "d": "#FF9F00", "B": "#0000FF",
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
MotifsLegend = function(container_id, motifs) {
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  
  //var container_height = 40*this.data.length;
  var container_height = 210;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("legend_canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: container_height - 15,
    width: 260 * (1 + Math.floor(motifs.length / 6))
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  var motif_colors = ColorRange(motifs.length);
  this.draw_residue = function(res_string, motif_index, x, y) {
    var letter_col = motif_colors[motif_index];
    var rect_w = 30;
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
    for (var i = 0; i < motifs.length; i++) {
      if (i % 6 == 0 && i != 0) {
        x = x + 260;
        y = 20;
      }
      this.draw_residue('   ', i, x, y);
      var res_text = new Kinetic.Text({
        x: x + 80,
        y: y,
        text: motifs[i][1],
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'black'
      });
      this.seq_layer.add(res_text);
      y = y + 30;
    }
    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
DomainsLegend = function(container_id, domains) {
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  
  //var container_height = 40*this.data.length;
  var container_height = 210;
  this.domains = domains;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("legend_canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: container_height - 15,
    width: 260 * (1 + Math.floor(domains.length / 6))
  });
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  var domain_colors = ColorRange(domains.length);
  this.draw_residue = function(res_string, domain_index, x, y) {
    var letter_col = domain_colors[domain_index];
    var rect_w = 30;
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
    for (var i = 0; i < domains.length; i++) {
      if (i % 6 == 0 && i != 0) {
        x = x + 260;
        y = 20;
      }
      this.draw_residue('   ', i, x, y);
      var res_text = new Kinetic.Text({
        x: x + 80,
        y: y,
        text: domains[i][1],
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'black'
      });
      this.seq_layer.add(res_text);
      y = y + 30;
    }
    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
SequenceAlignmentFeatures = function(container_id, data, codon_length,
                                     feature_codemap,
                                     feature_type) {
  const MAX_RES_PER_ROW = data[0][1].length / codon_length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 15;
  const ROW_HEIGHT = 15;
  const ROW_MARGIN_T = 0;
  const ROWS = data.length;
  
  this.data = data;
  this.feature_codemap = feature_codemap;
  //var container_height = 40*this.data.length;
  var container_height = ROWS * ROW_HEIGHT + 75;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 55,
    width: 170 + (this.data[0][0].length + this.data[0][1].length / codon_length)*8
  });
  document.getElementById('download_'+feature_type+'_canvas_button').addEventListener('click',
      function() {
        stage.toDataURL({
          callback: function(dataUrl) {
            window.open(dataUrl);
          }
        });
  }, false);
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
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
  color_to_hex = {'gray':'#D9D9D9', 'red': '#FFBDBD', 'green':'#CCF0CC',
                  'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0',
                  'blue':'#CFEFFF', 'purple':'#DECFFF', 'pink':'#FFCCE6',
                  'white':'#FFFFFF'};
  feature_colors = ColorRange(this.feature_codemap.length);
  this.draw_tooltip = function(x, y, message) {
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
      fontFamily: FONT_FAMILY,
      fontSize: FONT_SIZE,
      padding: 5,
      fill: 'white'
    });
    tooltip.add(tooltip_tag);
    tooltip.add(tooltip_text);
    this.seq_layer.add(tooltip);
    this.seq_layer.draw();
    return tooltip;
  }

  this.register_tooltip = function(src, x, y, message) {
    var seq = this;
    var tooltip;
    var url = 'http://elm.eu.org/elmPages/'+message+'.html';
    if (feature_type == 'domains') {
      url = 'http://pfam.xfam.org/family/' + message;
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
        left_button_clciked = false;
      }
    });
    src.on('mouseenter', function() {
      tooltip = seq.draw_tooltip(x, y, message);
    });
    src.on('mouseleave', function() {
      tooltip.destroy();
      seq.seq_layer.draw();
    });
  }
  this.draw_residue = function(res_num, seq_num, x, y) {
    var index_add = 0;
    if (feature_type == 'motifs') {
      index_add = 3;
    }
    var feature_code = this.data[seq_num][1].charAt(res_num + 2 + index_add) + this.data[seq_num][1].charAt(res_num + 3 + index_add);
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    var is_feature = false;
    if (feature_code == 'AA') {
      letter_col = color_to_hex[aa_to_color[r_up]]
    }
    else {
      var feat_number = 0;
      var char_index = 6;
      if (feature_type == 'domains') {
        char_index = 7;
      }
      for (var i = 0; i < feature_codemap.length; i++) {
        if (feature_codemap[i][0].charAt(char_index) == feature_code.charAt(0)
            && feature_codemap[i][0].charAt(char_index + 1) == feature_code.charAt(1)) {
          feat_number = i;
          break;    
        }
      }
      is_feature = true;
      letter_col = feature_colors[i];
    }

    var res_text = new Kinetic.Text({
      x: x,
      y: y,
      text: r,
      fontSize: FONT_SIZE,
      fontStyle: 'bold',
      fontFamily: FONT_FAMILY,
      fill: 'black'
    });

    if (is_feature) {
      this.register_tooltip(
        res_text,
        x,
        y + 10,
        feature_codemap[feat_number][1]);
    }
    

    var res_text_w = res_text.getTextWidth();
    var res_text_h = res_text.getTextHeight();
    var rect_w = res_text_w + 1;
    var rect_h = res_text_h;
    
    var text_rect = new Kinetic.Rect({
        x: x-0.25,
        y: y,
        width: res_text_w+1,
        height: res_text_h,
        fill: letter_col,
    });
    this.seq_layer.add(text_rect);
    this.seq_layer.add(res_text);

    return res_text_w;
  }
  this.draw = function() {
    var v_header_width = 0;
    for (var i = 0; i < this.data.length; i++) {
      var x = 10;
      var y = 20+(i * ROW_HEIGHT) + ROW_MARGIN_T;

      // Draw the residue number heading
      var res_num_txt = new Kinetic.Text({
        x: x,
        y: y,
        text: this.data[i][0],       //sequence header
        fontSize: FONT_SIZE,
        fontStyle: 'bold',
        fontFamily: FONT_FAMILY,
        fill: 'gray'
      });
      this.v_header_layer.add(res_num_txt);
      var res_num_txt_w = res_num_txt.getWidth();
      v_header_width = (
          res_num_txt_w > v_header_width ? res_num_txt_w : v_header_width);

      // Iterate over the residues in the current row. For each residue, draw
      // it with the appropriate accessibility colour, and draw the secondary
      // structure representation.
      for (var j = 0; j < this.data[i][1].length / codon_length; j++)
      {
        var res_text_width = this.draw_residue(j * codon_length, i, x, y);
        x = x + res_text_width;
      }
    }

    this.v_header_layer.width(v_header_width);
    var v_header_width = this.v_header_layer.getWidth();
    this.seq_layer.x(v_header_width + SEQ_LAYER_OFFSET_X);

    stage.add(this.v_header_layer);
    stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
