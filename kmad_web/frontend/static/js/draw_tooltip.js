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
  // shapesLayer.add(tooltip);
  // shapesLayer.draw();
  t_layer.add(tooltip);
  t_layer.draw();
  return tooltip;
};


register_tooltip = function(src, x, y, message, t_layer) {
  console.debug("register");
  var tooltip;
  // var url = 'http://elm.eu.org/elmPages/'+message+'.html';
  // var left_button_clicked = false;
  // src.on('mousedown', function(e) {
  //   if (e.evt.buttons == 1 || e.evt.keyCode == 0) {
  //     left_button_clicked = true;
  //   }
  // });
  // src.on('click', function(e) {
  //   if (left_button_clicked) {
  //     window.open(url);
  //     left_button_clicked = false;
  //   }
  // });
  src.on('mouseover', function() {
    // tooltip = draw_tooltip(x, y, message, shapesLayer);
    tooltip = draw_tooltip(x, y, message, t_layer);
    console.debug("mouseenter");
  });
  src.on('mouseout', function() {
    console.debug("mouseout");
    tooltip.destroy();
    // shapesLayer.draw();
    t_layer.draw();
  });
}

create_tooltip = function(container_id) {
  var stage = new Kinetic.Stage({
    container: container_id,
    width: 578,
    height: 200,
    listening: true
  });
  var shapesLayer = new Kinetic.Layer();
  var t_layer = new Kinetic.Layer();
  stage.add(shapesLayer);
  stage.add(t_layer);
  // var tooltipLayer = new Kinetic.Layer();
var triangle = new Kinetic.Shape({
      x:0,
      y:0,
      stroke:"blue",
      fill: 'red',
     drawFunc: function(context){
         // var context = this.getContext();
         context.beginPath();
         context.lineWidth = 4;
         context.strokeStyle = "black";
         context.fillStyle = "#00D2FF";
         context.moveTo(120, 50);
         context.lineTo(250, 80);
         context.lineTo(150, 170);
         context.closePath();
         // context.fill();
         // context.stroke();
          context.fillStrokeShape(this);
     }
 });

   register_tooltip(triangle, 120, 50 + 10, "some tooltip", t_layer);
  
   console.debug("wtf");
  
  
   shapesLayer.add(triangle);
   triangle.on("click", function(){
       alert("mouseenter");
   });
   shapesLayer.draw();
   var ctx = shapesLayer.getContext()._context;
   ctx.fillStyle = "blue";
   ctx.fillRect(30, 20, 10, 15);
   ctx.fillStyle = "#000000";
   ctx.fillText("czesc czesc", 30 + 1, 20 + 10)
}
