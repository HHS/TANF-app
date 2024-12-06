$(window).on('load', function() {
    console.log('loaded');
    var submitBtn=document.querySelector('button[type=submit]');    // add the first listener
    var theForm = submitBtn.parentNode.parentNode;
    var action = "";
    var number_of_files_line = "";

    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // number of files
        action_counter = document.querySelector('span.action-counter')
        is_action_counter_hidden = action_counter.className === "action-counter hidden"

        action_counter_all = document.querySelector('span.all')

        if (is_action_counter_hidden) {
          number_of_files_line = action_counter_all.innerText;
        } else {
          number_of_files_line = action_counter.innerText;
        }
        
        // what action is selected
        action = document.querySelector('select[name=action]').value;

        if (action === "reparse") {
          console.log('reparse');
          var splitted_number_of_files = number_of_files_line.split(/(\s+)/);
          if (Number(splitted_number_of_files[0]) > 0 ) {
            number_of_files = splitted_number_of_files[0];
          } else {
            number_of_files = splitted_number_of_files[2];
          }
          if (confirm("You are about to re-parse " + number_of_files + " files. Are you sure you want to continue?")) {
              console.log('submitting');
              theForm.submit();
          } else {
              console.log('not submitting');
          };
        } else {
          console.log('not reparse');
          alert('Please select the "Reparse" action to continue.');
        }
    });

});
