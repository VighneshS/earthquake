var urlParams = new URLSearchParams(window.location.search);
var page = urlParams.has('page') ? urlParams.get('page') : 1
var minTime2 = urlParams.has('minTime2') ? urlParams.get('minTime2') : 5000
var maxTime2 = urlParams.has('maxTime2') ? urlParams.get('maxTime2') : 8000
var fromDate = urlParams.has('fromDate') ? decodeURIComponent(urlParams.get('fromDate')) : '6/9/2021'
var toDate = urlParams.has('toDate') ? decodeURIComponent(urlParams.get('toDate')) : '6/16/2021'

// don't forget to include leaflet-heatmap.js
var testData = {
    max: 8,
    data: [{lat: 24.6408, lng: 46.7728, count: 3}, {lat: 50.75, lng: -1.55, count: 1}]
};

var baseLayer = L.tileLayer(
    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '...',
        maxZoom: 18
    }
);

var cfg = {
    // radius should be small ONLY if scaleRadius is true (or small radius is intended)
    // if scaleRadius is false it will be the constant radius used in pixels
    "radius": 2,
    "maxOpacity": .8,
    // scales the radius based on map zoom
    "scaleRadius": true,
    // if set to false the heatmap uses the global maximum for colorization
    // if activated: uses the data maximum within the current map boundaries
    //   (there will always be a red spot with useLocalExtremas true)
    "useLocalExtrema": true,
    // which field name in your data represents the latitude - default "lat"
    latField: 'lat',
    // which field name in your data represents the longitude - default "lng"
    lngField: 'lng',
    // which field name in your data represents the data value - default "value"
    valueField: 'count'
};


var heatmapLayer = new HeatmapOverlay(cfg);

var map = new L.Map('map-canvas', {
    center: new L.LatLng(25.6586, -80.3568),
    zoom: 4,
    layers: [baseLayer, heatmapLayer]
});

heatmapLayer.setData(testData);

$(function () {
    $("#time2-rage").slider({
        range: true,
        min: 5000,
        max: 8000,
        values: [minTime2, maxTime2],
        step: 1,
        slide: function (event, ui) {
            $("#time2").val(ui.values[0] + " - " + ui.values[1]);
        }
    });

    $("#time2").val($("#time2-rage").slider("values", 0) +
        " to " + $("#time2-rage").slider("values", 1));

    $("#from").val(fromDate)
    $("#to").val(toDate)
    var dateFormat = "mm/dd/yy",
        from = $("#from")
            .datepicker({
                defaultDate: fromDate,
                changeMonth: true,
                numberOfMonths: 1,
                minDate: "6/9/2021",
                maxDate: "6/16/2021"
            })
            .on("change", function () {
                to.datepicker("option", "minDate", getDate(this));
            }),
        to = $("#to").datepicker({
            defaultDate: toDate,
            changeMonth: true,
            numberOfMonths: 1,
            minDate: "6/9/2021",
            maxDate: "6/16/2021"
        })
            .on("change", function () {
                from.datepicker("option", "maxDate", getDate(this));
            });

    function getDate(element) {
        var date;
        try {
            date = $.datepicker.parseDate(dateFormat, element.value);
        } catch (error) {
            date = null;
        }

        return date;
    }
});

function apply() {
    minTime2 = $("#time2-rage").slider("values", 0)
    maxTime2 = $("#time2-rage").slider("values", 1)
    fromDate = $('#from').val()
    toDate = $('#to').val()
    fromDate =
        window.location.replace("/?page=" + page + "&minTime2=" + minTime2 + "&maxTime2=" + maxTime2 + "&fromDate=" + encodeURIComponent(fromDate) + "&toDate=" + encodeURIComponent(toDate));
}