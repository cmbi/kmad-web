get_text_data = function(prediction, sequence){
    methods = ['filtered', 'consensus'];
    for (var m in prediction) {
        if (m != 'consensus' && m != 'filtered'){
          methods.push(m);
        }
    }
    var txt_pred = "ResNo AA";
    var length = 0;
    for (var i in prediction){
        txt_pred = txt_pred + " ";
        txt_pred = txt_pred + prediction[i];
        length += 1;
    }
    txt_pred = txt_pred + "\n";
    for (var i = 0; i < sequence.length; i++){
        var newline ="";
        newline = newline + (i+1).toString() + " ";
        newline = newline + sequence[i] + " ";
        for (var j in prediction){
            console.debug(prediction[j])
            newline = newline + prediction[j][i].toString()+" ";
        }
        txt_pred = txt_pred + newline + "\n";
    }
    return txt_pred;
}
