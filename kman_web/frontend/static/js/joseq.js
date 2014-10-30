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

  this.stage = new Kinetic.Stage({
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

    this.stage.add(this.v_header_layer);
    this.stage.add(this.seq_layer);
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
  this.stage = new Kinetic.Stage({
    container: container_id,
    height: ROWS * ROW_HEIGHT + 25,
    width: 170 + (this.data[0][0].length + this.data[0][1].length)*8
  });
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
    
    var text_rect = new Kinetic.Shape({
        x: x-10,
        y: y,
        fill: letter_col,
        drawFunc: function(context) {
            context.beginPath();
            context.lineTo(x+rect_w, y);
            context.lineTo(x+rect_w, y+rect_h);
            context.lineTo(x, y+rect_h);
            context.lineTo(x,y);
            context.closePath();
            context.fillStrokeShape(this);
        }
    });

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

    this.stage.add(this.v_header_layer);
    this.stage.add(this.seq_layer);
  }
  this.update = function() {
    this.draw();
  }
}
