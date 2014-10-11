//
// Konfiguracja dla google mapy.
// -----------------------------------------------------------------------------

require.config({
    baseUrl: window.STATIC_URL,
    
    urlArgs: "bust=" + (new Date()).getTime(),
    
    waitSeconds: 200,
    
    paths: {
        jquery: 'includes/jquery/jquery',
        bootstrap: 'includes/bootstrap/bootstrap',
        underscore: 'includes/underscore/underscore',
        backbone: 'includes/backbone/backbone',
        bootbox: 'includes/bootstrap/bootbox',
        leaflet: 'includes/leaflet/leaflet'
    },
    
    shim: {
        jqueryui: { deps: ['jquery'] },
        
        underscore: {
            deps: ['jquery'],
            exports: '_'
        },
        
        backbone: {
            deps: ['underscore'],
            exports: 'Backbone'
        },
        
        bootstrap: {
            deps: ['jquery']
        },
        
        bootbox: {
            deps: ['bootstrap'],
            exports: 'bootbox'
        },
        
        tagsinput: {
            deps: ['jquery']
        }
    }
});

require(['jquery',
         'js/maps/map',
         'js/maps/autocomplete',
         'bootstrap',
         'js/common/bookmarks'],

function ($, CivilMap) {
    
    "use strict";
    
    function getCoords (success) {
        
        var callback = null;
        
        if (success !== undefined && typeof(success) === 'function') {
            callback = success;
        } else {
            callback = function (x, y) {console.log(x,y);};
        }
        
        var fallback = function () {
            var x = window.CIVILAPP.position.lat;
            var y = window.CIVILAPP.position.lng;
            callback(x, y);
        };
        
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var x = position.coords.latitude;
                var y = position.coords.longitude;
                callback(x, y);
            }, function () {
                fallback();
            });
        } else {
            fallback();
        }
    }
    
    getCoords(function (lat, lng) {
        
        var app = {
        
            // Create main map application
            
            application: new CivilMap({
                elementID: 'main-map',
                center: [lat, lng]
            }),
            
            // Get map content filters
            
            getFilters: function getFilters () {
                var filters = [], t = '', ct = null;
                $('.map-filter-toggle').each(function () {
                    if ($(this).is(':checked')) {
                        t = $(this).attr('data-target');
                        ct = _.findWhere(window.CONTENT_TYPES, {model: t});
                        filters.push(ct.content_type);
                    }
                });
                return filters;
            },
            
            // Initialize all plugins
            
            initialize: function () {
                $('.map-filter-toggle').change(function () {
                    this.application.setFilters(this.getFilters());
                }.bind(this));
                
                $('.angle-icon-toggle').on('click', function () {
                    $('#map-options-panel').slideToggle('fast');
                });
                
                $('#select-location-field').autocomplete({
                    onSelect: function (locationID) {
                        app.application.setLocation(locationID);
                    },
                    onClear: function () {
                        app.application.setLocation(null);
                        app.application.fetchData();
                    }
                });
            }
        };
        
        app.initialize();
    });
    
    $(document).trigger('load');
    
});