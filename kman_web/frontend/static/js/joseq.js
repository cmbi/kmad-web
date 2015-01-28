ProteinSequences = function(container_id, data) {
  // TODO: Check arguments are same length
  // TODO: Private methods are actually publicly visible.
  // TODO: All methods are recreated per instance. Is this a problem?
  // TODO: Fit to canvas width.
  // TODO: Resize canvas when browser resized.
  // TODO: Pass settings in constructor
  // TODO: Smarter positioning of (long) tooltips
  // TODO: Multiple types of info in tooltips

  // Constants
  const MAX_RES_PER_ROW = data[1][1].length;
  const SEQ_LAYER_OFFSET_X = 50;
  const FONT_FAMILY = "Monospace";
  const FONT_SIZE = 16;
  const ROW_HEIGHT = 36;
  const ROW_MARGIN_T = 0;
  const ROWS = data.length - 1;


  // Attributes
  this.seq = data[0];
  this.disorder = [];
  for (var i = 1; i < data.length; i++){
    this.disorder.push(data[i])
  }
  var container_height = ROWS * ROW_HEIGHT;
  document.getElementById(container_id).style.height = (container_height + 40).toString() + 'px';

  var stage = new Kinetic.Stage({
    container: container_id,
    width: 150 + this.disorder[0][1].length*10,
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
    for (var i = 0; i < this.disorder.length; i++) {
      //var x = 0;
      //var y = (i * ROW_HEIGHT) + ROW_MARGIN_T;
      var x = 10;
      var y = 20+(i * ROW_HEIGHT) + ROW_MARGIN_T;

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
  this.draw_residue = function(res_num, seq_num, x, y) {
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    if ( r_up == 'C' || r_up == 'M'){
        letter_col = colors['yellow'];
    } 
    else if (r_up == 'V' || r_up == 'A' || r_up == 'I' || r_up == 'L' || r_up == 'F') {
      letter_col = colors['green'];
    }
    else if (r_up == 'S' || r_up == 'T' || r_up == 'Y'){
      letter_col = colors['blueishgreen'];
    }
    else if (r_up == 'H'){
      letter_col = colors['blue'];
    }
    else if (r_up == 'K' || r_up == 'R'){
      letter_col = colors['purple'];
    }
    else if (r_up == 'E' || r_up == 'Q'){
      letter_col = colors['red'];
    }
    else if (r_up == 'N' || r_up == 'D'){
      letter_col = colors['pink'];
    }
    else if (r_up == '-'){
      letter_col = colors['white'];
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
  this.draw_residue = function(res_num, seq_num, x, y) {
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    var ptm_code = this.data[seq_num][1].charAt(res_num + 4);
    if (ptm_code == 'A') {
      if ( r_up == 'C' || r_up == 'M'){
          letter_col = colors['yellow'];
      } 
      else if (r_up == 'V' || r_up == 'A' || r_up == 'I' || r_up == 'L' || r_up == 'F') {
        letter_col = colors['green'];
      }
      else if (r_up == 'S' || r_up == 'T' || r_up == 'Y'){
        letter_col = colors['blueishgreen'];
      }
      else if (r_up == 'H'){
        letter_col = colors['blue'];
      }
      else if (r_up == 'K' || r_up == 'R'){
        letter_col = colors['purple'];
      }
      else if (r_up == 'E' || r_up == 'Q'){
        letter_col = colors['red'];
      }
      else if (r_up == 'N' || r_up == 'D'){
        letter_col = colors['pink'];
      }
      else if (r_up == '-'){
        letter_col = colors['white'];
      }
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
  for (var i = 0; i < number; i++) {
    var hue = Math.floor((100 - i * norm) * 120 / 100);
    // var saturation = Math.abs(i * norm - 50) / 50;
    var saturation = 1;

    result.push(HSLtoHEX(hue, saturation, 0.5));
  }
  return result;
}

SequenceAlignmentMotifs = function(container_id, data, codon_length,
                                   feature_codemap) {
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
  var container_height = ROWS * ROW_HEIGHT + 45;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 25,
    width: 170 + (this.data[0][0].length + this.data[0][1].length / codon_length)*8
  });
  document.getElementById('download_motifs_canvas_button').addEventListener('click',
      function() {
        stage.toDataURL({
          callback: function(dataUrl) {
            window.open(dataUrl);
          }
        });
  }, false);
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  colors = {'gray':'#D9D9D9','red': '#FFBDBD','green':'#CCF0CC', 'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0', 'blue':'#CFEFFF', 'purple':'#DECFFF', 'pink':'#FFCCE6', 'white':'#FFFFFF'};
  motif_colors = ColorRange(this.feature_codemap.length);
  this.draw_residue = function(res_num, seq_num, x, y) {
    var motif_code = this.data[seq_num][1].charAt(res_num + 5) + this.data[seq_num][1].charAt(res_num + 6);

    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    if (motif_code == 'AA') {
      if ( r_up == 'C' || r_up == 'M'){
          letter_col = colors['yellow'];
      } 
      else if (r_up == 'V' || r_up == 'A' || r_up == 'I' || r_up == 'L' || r_up == 'F') {
        letter_col = colors['green'];
      }
      else if (r_up == 'S' || r_up == 'T' || r_up == 'Y'){
        letter_col = colors['blueishgreen'];
      }
      else if (r_up == 'H'){
        letter_col = colors['blue'];
      }
      else if (r_up == 'K' || r_up == 'R'){
        letter_col = colors['purple'];
      }
      else if (r_up == 'E' || r_up == 'Q'){
        letter_col = colors['red'];
      }
      else if (r_up == 'N' || r_up == 'D'){
        letter_col = colors['pink'];
      }
      else if (r_up == '-'){
        letter_col = colors['white'];
      }
    }
    else {
      var feat_number = 0;
      for (var i = 0; i < feature_codemap.length; i++) {
        if (feature_codemap[i][0].charAt(6) == motif_code.charAt(0)
            && feature_codemap[i][0].charAt(7) == motif_code.charAt(1)) {
          feat_number = i;
          break;    
        }
      }
      letter_col = motif_colors[i];
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

SequenceAlignmentDomains = function(container_id, data, codon_length,
                                    feature_codemap, legend_container) {
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
  var container_height = ROWS * ROW_HEIGHT + 45;
  document.getElementById(container_id).style.height = container_height.toString() + 'px';
  document.getElementById("canvases").style.height = container_height.toString() + 'px';
  var stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 25,
    width: 170 + (this.data[0][0].length + this.data[0][1].length / codon_length)*8
  });
  document.getElementById('download_domains_canvas_button').addEventListener('click',
      function() {
        stage.toDataURL({
          callback: function(dataUrl) {
            window.open(dataUrl);
          }
        });
  }, false);
  this.v_header_layer = new Kinetic.Layer();
  this.seq_layer = new Kinetic.Layer();
  colors = {'gray':'#D9D9D9','red': '#FFBDBD','green':'#CCF0CC', 'yellow':'#FFFFB5', 'blueishgreen': '#A6DED0', 'blue':'#CFEFFF', 'purple':'#DECFFF', 'pink':'#FFCCE6', 'white':'#FFFFFF'};
  domain_colors = ColorRange(this.feature_codemap.length);
  this.draw_residue = function(res_num, seq_num, x, y) {
    var domain_code = this.data[seq_num][1].charAt(res_num + 2) + this.data[seq_num][1].charAt(res_num + 3);
    var r = this.data[seq_num][1].charAt(res_num);
    var r_up = r.toUpperCase(); 
    var letter_col = colors['gray'];
    if (domain_code == 'AA') {
      if ( r_up == 'C' || r_up == 'M'){
          letter_col = colors['yellow'];
      } 
      else if (r_up == 'V' || r_up == 'A' || r_up == 'I' || r_up == 'L' || r_up == 'F') {
        letter_col = colors['green'];
      }
      else if (r_up == 'S' || r_up == 'T' || r_up == 'Y'){
        letter_col = colors['blueishgreen'];
      }
      else if (r_up == 'H'){
        letter_col = colors['blue'];
      }
      else if (r_up == 'K' || r_up == 'R'){
        letter_col = colors['purple'];
      }
      else if (r_up == 'E' || r_up == 'Q'){
        letter_col = colors['red'];
      }
      else if (r_up == 'N' || r_up == 'D'){
        letter_col = colors['pink'];
      }
      else if (r_up == '-'){
        letter_col = colors['white'];
      }
    }
    else {
      var feat_number = 0;
      for (var i = 0; i < feature_codemap.length; i++) {
        if (feature_codemap[i][0].charAt(7) == domain_code.charAt(0)
            && feature_codemap[i][0].charAt(8) == domain_code.charAt(1)) {
          feat_number = i;
          break;    
        }
      }
      letter_col = domain_colors[i];
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
      if (i % 7 == 0) {
        x = x + 60;
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
      if (i % 7 == 0) {
        x = x + 60;
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
