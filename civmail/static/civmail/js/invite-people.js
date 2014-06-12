(function ($) {
//
// Send invitations for currently browsed page.
// --------------------------------------------
//
"use strict";
var $modal     = $('#invite-modal'),               // Modal window
    $toggle    = $('#invite-people-toggle'),       // Toggle link (open modal)
    $form      = $modal.find('form:first'),        // Form
    $submit    = $modal.find('.submit-btn'),       // Submit button
    $emails    = $('#invite-emails'),              // Emails input
    inviteText = $emails.attr('data-defaulttext'), // Text for TagsInput
    apiUrl     = $form.attr('action'),             // Api target URL
    currentUrl = window.location.href;             // Current page address

$modal.modal({show:false});

$emails.tagsInput({
    defaultText: inviteText
});

$toggle.bind('click', function (evt) {
    evt.preventDefault();
    $modal.modal('show');
});

$submit.bind('click', function (evt) {
    evt.preventDefault();
    $modal.modal('hide');
    sendAjaxRequest('POST', apiUrl, {
        data: {
            'emails': $emails.val(),
            'link': currentUrl,
            'name': document.title
        },
        success: function (resp) {
            display_alert(resp.message, resp.level);
        }
    });
});

})(jQuery);