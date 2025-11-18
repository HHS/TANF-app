'use strict';
///Remove actions buttons from the admin interface.
{
    window.addEventListener("load", function(event) {
        const actions = document.getElementsByClassName('actions');
        actions[0].style.display = 'none';
    })
    
    
}