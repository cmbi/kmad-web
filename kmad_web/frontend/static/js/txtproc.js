get_text_data = function(data){
    var txt_pred = "ResNo AA";
    for (var i = 1; i < data.length; i++){
        txt_pred = txt_pred + " ";
        txt_pred = txt_pred + data[i][0];
    }
    txt_pred = txt_pred + "\n";
    var sequence = data[0];
    for (var i = 0; i < sequence.length; i++){
        var newline ="";
        newline = newline + (i+1).toString() + " ";
        newline = newline + sequence[i] + " ";
        for (var j = 1 ; j < data.length; j++){
            newline = newline + data[j][1][i].toString()+" ";
        }
        txt_pred = txt_pred + newline + "\n";
    }
    return txt_pred;
}
