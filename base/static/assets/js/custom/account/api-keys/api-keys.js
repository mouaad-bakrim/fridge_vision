<<<<<<< HEAD
"use strict";var KTAccountAPIKeys={init:function(){KTUtil.each(document.querySelectorAll('#kt_api_keys_table [data-action="copy"]'),(function(e){var t=e.closest("tr"),s=KTUtil.find(t,'[data-bs-target="license"]');new ClipboardJS(e,{target:s,text:function(){return s.innerHTML}}).on("success",(function(t){var c=e.querySelector(".ki-copy"),i=e.querySelector(".ki-check");i||((i=document.createElement("i")).classList.add("ki-solid"),i.classList.add("ki-check"),i.classList.add("fs-2"),e.appendChild(i),s.classList.add("text-success"),c.classList.add("d-none"),setTimeout((function(){c.classList.remove("d-none"),e.removeChild(i),s.classList.remove("text-success")}),3e3))}))}))}};KTUtil.onDOMContentLoaded((function(){KTAccountAPIKeys.init()}));
=======
"use strict";

// Class definition
var KTAccountAPIKeys = function () {
    // Private functions
    var initLicenceCopy = function() {
        KTUtil.each(document.querySelectorAll('#kt_api_keys_table [data-action="copy"]'), function(button) {
            var tr = button.closest('tr');
            var license = KTUtil.find(tr, '[data-bs-target="license"]');

            var clipboard = new ClipboardJS(button, {
                target: license,
                text: function() {
                    return license.innerHTML;
                }                 
            });
        
            clipboard.on('success', function(e) {
                // Icons
                var svgIcon = button.querySelector('.svg-icon');                
                var checkIcon = button.querySelector('.bi.bi-check');
                
                // exit if check icon is already shown
                if (checkIcon) {
                   return;  
                }

                // Create check icon
                checkIcon = document.createElement('i');
                checkIcon.classList.add('bi');
                checkIcon.classList.add('bi-check');
                checkIcon.classList.add('fs-2x');

                // Append check icon
                button.appendChild(checkIcon);

                // Highlight target
                license.classList.add('text-success');

                // Hide copy icon
                svgIcon.classList.add('d-none');

                // Set 3 seconds timeout to hide the check icon and show copy icon back
                setTimeout(function() {
                    // Remove check icon
                    svgIcon.classList.remove('d-none');
                    // Show check icon back
                    button.removeChild(checkIcon);

                    // Remove highlight
                    license.classList.remove('text-success');
                }, 3000);
            });
        });
    }

    // Public methods
    return {
        init: function () {
            initLicenceCopy();
        }
    }
}();

// On document ready
KTUtil.onDOMContentLoaded(function() {
    KTAccountAPIKeys.init();
});
>>>>>>> origin/sef
