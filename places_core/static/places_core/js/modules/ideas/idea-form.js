//
// idea-form.js
// ============
//
// Formularz dodawania nowego pomysłu - skrypt inicjalizacyjny.
// -----------------------------------------------------------------------------

require(['jquery',
         'jqueryui',
         'js/modules/editor/plugins/uploader',
         'redactor',
         'js/modules/ui/mapinput',
         'tagsinput',
         'js/modules/content/content-form'],

function ($) {
    
  "use strict";
  
  $(document).ready(function () {
      
    $('#id_description').redactor({
      buttons: ['bold', 'italic', 'unorderedlist', 'orderedlist', 'link'],
      plugins: ['uploader']
    });
    
    $('#id_tags').tagsInput({
      autocomplete_url: '/rest/tags/',
      defaultText: gettext("Add tag")
    });
  });
  
});