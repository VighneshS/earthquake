var urlParams = new URLSearchParams(window.location.search);
var page = urlParams.has('page') ? urlParams.get('page') : 1
var minMag = urlParams.has('minMag') ? urlParams.get('minMag') : -1
var maxMag = urlParams.has('maxMag') ? urlParams.get('maxMag') : 6
var lat = urlParams.has('lat') ? urlParams.get('lat') : null
var lon = urlParams.has('lon') ? urlParams.get('lon') : null
var dist = urlParams.has('dist') ? urlParams.get('dist') : null
var fromDate = urlParams.has('fromDate') ? decodeURIComponent(urlParams.get('fromDate')) : '6/6/2021'
var toDate = urlParams.has('toDate') ? decodeURIComponent(urlParams.get('toDate')) : '6/14/2021'
var night = urlParams.has('night') ? urlParams.get('night') : false

$(function () {
    $("#magnitude-rage").slider({
        range: true,
        min: -1,
        max: 6,
        values: [minMag, maxMag],
        step: 0.1,
        slide: function (event, ui) {
            $("#magnitude").val(ui.values[0] + " - " + ui.values[1]);
        }
    });

    $("#magnitude").val($("#magnitude-rage").slider("values", 0) +
        " to " + $("#magnitude-rage").slider("values", 1));

    $("#from").val(fromDate)
    $("#to").val(toDate)
    var dateFormat = "mm/dd/yy",
        from = $("#from")
            .datepicker({
                defaultDate: fromDate,
                changeMonth: true,
                numberOfMonths: 1,
                minDate: "6/6/2021",
                maxDate: "6/14/2021"
            })
            .on("change", function () {
                to.datepicker("option", "minDate", getDate(this));
            }),
        to = $("#to").datepicker({
            defaultDate: toDate,
            changeMonth: true,
            numberOfMonths: 1,
            minDate: "6/6/2021",
            maxDate: "6/14/2021"
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

    $("#lat").val(lat)
    $("#lon").val(lon)
    $("#dist").val(dist)
    night ? $('#night').prop('checked', true) : $('#night').prop('checked', false)
});

function apply() {
    minMag = $("#magnitude-rage").slider("values", 0)
    maxMag = $("#magnitude-rage").slider("values", 1)
    fromDate = $('#from').val()
    toDate = $('#to').val()
    lat = $("#lat").val()
    lon = $("#lon").val()
    dist = $("#dist").val()
    night = $('#night').prop('checked')
    fromDate =
        window.location.replace("/analyse?page=" + page + "&minMag=" + minMag + "&maxMag=" + maxMag
            + "&fromDate=" + encodeURIComponent(fromDate) + "&toDate=" + encodeURIComponent(toDate)
            + "&lat=" + lat + "&lon=" + lon + "&dist=" + dist + "&night=" + night);
}