function show_sequence_input() {
    $('#sequence_div').removeClass('hidden');
}
function show_forms_predict() {
  $('#predictionMethod').removeClass('hidden');
  $('#alignment_options_div').addClass('hidden');
}
function show_forms_panda() {
  $('#predictionMethod').removeClass('hidden');
  $('#alignment_options_div').removeClass('hidden');
}
function show_forms_align() {
  $('#predictionMethod').addClass('hidden');
  $('#alignment_options_div').removeClass('hidden');
}
function hide_forms() {
  console.debug("hejehej");
  $('#predictionMethod').addClass('hidden');
  $('#alignment_options_div').addClass('hidden');
}
function show_forms() {
  var selected = $('#output_type').children(":selected").attr('value');
    switch (selected) {
    case 'align':
      show_forms_align();
      break;
    case 'annotate':
      hide_forms();
      break;
    case 'refine':
      show_forms_align();
      break;
    case 'predict_and_align':
      show_forms_panda();
      break;
    case 'predict':
      show_forms_predict();
      break;
    }
}
function show_tour_data_input(index) {
    switch (index) {
    case 3:
      show_sequence_input();
      break;
    }
}


function useExample() {
  document.getElementById('sequence').innerHTML = ">sp|P21815|SIAL_HUMAN "
    + "Bone sialoprotein 2 OS=Homo sapiens GN=IBSP PE=1 SV=4\n"
    + "MKTALILLSILGMACAFSMKNLHRRVKIEDSEENGVFKYRPRYYLYKHAYFYPHLKRFPV"
    + "QGSSDSSEENGDDSSEEEEEEEETSNEGENNEESNEDEDSEAENTTLSATTLGYGEDATP"
    + "GTGYTGLAAIQLPKKAGDITNKATKEKESDEEEEEEEEGNENEESEAEVDENEQGINGTS"
    + "TNSTEAENGNGSSGGDNGEEGEEESVTGANAEDTTETGRQGKGTSKTTTSPNGGFEPTTP"
    + "PQVYRTTSPPFGKTTTVEYEGEYEYTGANEYDNGYEIYESENGEPRGDNYRAYEDEYSYF"
    + "KGQGYDGYDGQNYYHHQ";
}


function show_data_input() {
    var selected = $('#input_type').children(":selected").attr('value');
    switch (selected) {
    case 'sequence':
      show_sequence_input();
      break;
    }
}

function show_prediction_alert() {
  if (document.getElementById('prediction_alert')){
    document.getElementById("prediction_alert").style.display = '';
  }
}

$(document).ready( function() {

  document.getElementById("start_tour").style.display = '';
  document.getElementById("start_tour2").style.display = 'none';
  // $('#KMADlogo').removeClass('navbar-brand');
  $('#KMADlogo').addClass('navbar-brand-active');
  // Setup tour
  var tour = new Tour({
    backdrop: true,
    orphan: true,
    storage: false,
    onNext: function (tour) {
      show_tour_data_input(tour.getCurrentStep() + 1)
    },
    onPrev: function (tour) {
      show_tour_data_input(tour.getCurrentStep() - 1)
    },
    onEnd: function (tour) { show_data_input(); },
    steps: [
    {
      element: "",
      title: "Start Tour",
      content: "This tour will walk you through the usage of KMAN." +
               " Once the tour is complete, you can get started!" +
               "<br><br>Click next to begin."
    },
    {
      element: "#output_type_inner_div",
      title: "Output Type",
      content: "Select the action to be performed.",
      placement: "top",
      onShown:  function() {
        document.getElementById("output_type_inner_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("output_type_inner_div").style.background="";
      }
    },
    {
      element: "#sequence_div",
      title: "Sequence",
      content: "Enter protein sequence(s) - if it is a single sequence "
               + "both FASTA and plain sequence formats are accepted, in case "
               + "of multiple sequences only FASTA is allowed",
      placement: "right"
    },
    {
      element: "#gap_open_div",
      title: "Gap opening penalty",
      content: "Set the penalty for opening a gap (has to be negative)",
      placement: "left",
      onShown:  function() {
        document.getElementById("gap_open_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("gap_open_div").style.background="";
      }
    },
    {
      element: "#gap_ext_div",
      title: "Gap extension penalty",
      content: "Set the penalty for extending a gap (has to be negative)",
      placement: "left",
      backdrop: true,
      onShown:  function() {
        document.getElementById("gap_ext_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("gap_ext_div").style.background="";
      }
    },
    {
      element: "#end_gap_div",
      title: "End gap penalty",
      content: "Set the penalty for a gap at the end or beginning of a" +
               " sequence (has to be negative)",
      placement: "bottom",
      onShown:  function() {
        document.getElementById("end_gap_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("end_gap_div").style.background="";
      }

    },
    {
      element: "#ptm_score_div",
      title: "Posttranslational modification score",
      content: "Set the additional score for aligning two residues with a" +
               " certain PTM assigned to them (has to be greater than or" + 
               " equal to 0)",
      placement: "bottom",
      onShown:  function() {
        document.getElementById("ptm_score_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("ptm_score_div").style.background="";
      }
    },
    {
      element: "#domain_score_div",
      title: "Domain score",
      content: "Set the additional score for aligning two residues with a" +
               " certain domain assigned to them (has to be greater than" +
               " or equal to 0)",
      placement: "bottom",
      onShown:  function() {
        document.getElementById("domain_score_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("domain_score_div").style.background="";
      }
    },
    {
      element: "#motif_score_div",
      title: "Motif score",
      content: "Set the additional score for aligning two residues with a" +
               " certain motif assigned to them (has to be greater than or" +
               " equal to 0)",
      placement: "bottom",
      onShown:  function() {
        document.getElementById("motif_score_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("motif_score_div").style.background="";
      }
    },
    {
      element: "#gapped_div",
      title: "First sequence",
      content: "The produced alignment might be either with or without" +
               " gaps in the first sequence (HSSP style)",

      placement: "bottom",
      onShown:  function() {
        document.getElementById("gapped_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("gapped_div").style.background="";
      }
    },
    {
      element: "#usr_feat_inner_div",
      title: "User defined features",
      content: "You may define new features that will be assigned to " +
               "sequences either based on the specified positions or" +
               " pattern",
      placement: "bottom",
      onShown:  function() {
        document.getElementById("usr_feat_inner_div").style.background="#EBEBEB";
      },
      onHidden:  function() {
        document.getElementById("usr_feat_inner_div").style.background="";
      }
    },
    {
      element: "#submit_inner_div",
      title: "Submit",
      content: "When you're ready, click <code>Submit</code> to send your " +
               "request to the server.<br><br>A result page will be shown " +
               "with the status of your request, and when completed, the " +
               "output will be shown.",

      placement: "left" 
    }
  ]});
  tour.init();

  $('#start_tour').click(function() { tour.restart(); });
  if (window.location.hash == '#start_tour') {tour.restart();}

  // Ensure that the input types listed are correct for the selected output
  // type.
  var selected = $('#output_type').children(":selected").attr('value');
  $('#output_type option[value=' + selected + ']').prop('selected', true);
  show_forms();
  $('#output_type').change(function() { show_forms(); });
  $('#prediction_method-1').change( function() {show_prediction_alert(); });
  $('#prediction_method-2').change( function() {show_prediction_alert(); });
  $('#prediction_method-3').change( function() {show_prediction_alert(); });
  $('#prediction_method-4').change( function() {show_prediction_alert(); });
  

});


