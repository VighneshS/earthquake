var minRange1 = -1
var maxRange1 = 6
var sliders = 0
var spinner
var figure

function createNewSlider() {
    const rangeSliders = $('#range-sliders')
    const $label = $("<label for=\"range" + (sliders + 1) + "\"></label>").text('Range ' + (sliders + 1) + ':');
    const $br = $('<br>');
    const $input = $('<input type="text" readonly style="border:0; color:#f6931f; font-weight:bold;"/>').attr({
        id: "range" + (sliders + 1)
    });
    var $div = $('<div></div>').attr({id: 'range' + (sliders + 1) + '-rage'});
    var $container = $('<div></div>').attr({id: 'range' + (sliders + 1) + '-container'});

    $label.appendTo($container)
    $br.appendTo($container)
    $input.appendTo($container)
    $div.appendTo($container)
    $br.appendTo($container)
    rangeSliders.append($container)

    var sliderNumber = (sliders + 1)

    $("#range" + (sliders + 1) + "-rage").slider({
        range: true,
        min: -1,
        max: 6,
        values: [minRange1, maxRange1],
        step: 0.1,
        slide: function (event, ui) {
            $("#range" + sliderNumber).val(ui.values[0] + " - " + ui.values[1]);
        }
    });
    $("#range" + sliderNumber).val($("#range" + sliderNumber + "-rage").slider("values", 0) +
        " to " + $("#range" + sliderNumber + "-rage").slider("values", 1));
    ++sliders
}

function deleteSlider() {

    $("#range" + (sliders) + "-container").remove()
    --sliders
}

$(function () {
    spinner = $('#spinner')
    figure = $('#figure')
    spinner.show()
    figure.hide()
    createNewSlider();
    createNewSlider();
    createNewSlider();
    loadChart()
});

function loadChart() {
    var payLoad = []
    for (let i = 0; i < sliders; i++) {
        var range_slider = $("#range" + (i + 1) + "-rage")
        payLoad.push({
            'from': range_slider.slider("values", 0),
            'to': range_slider.slider("values", 1)
        })
    }
    $.ajax({
        type: 'POST',
        url: "/graphs",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        // $(this).addClass("done");
        createChart(data)
        spinner.hide()
        figure.show()
    });
}

function createChart(data) {
    var categories = _.map(data, 'magRange');
    var values = _.map(data, 'value');
    Highcharts.chart('bar-chart', {
        chart: {
            height: "50%",
            type: 'column'
        },
        title: {
            text: 'Number of earthquakes based on magnitude range'
        },
        subtitle: {
            text: 'Bar Chart'
        },
        xAxis: {
            categories: categories,
            crosshair: true,
            title: {
                text: 'Earthquake Magnitude Range'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Number of Earthquakes'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            series: {
                color: '#EE6363'
            },
            column: {
                zones: [{
                    value: _.max(_.map(data, 'value')), // Values up to max value (not including) ...
                    color: '#79973F' // ... have the color pea.
                }, {
                    color: '#EE6363' // Values from max value (including) and up have the color fire brick red
                }],
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: 'Number of Earthquakes',
            data: values

        }]
    });

    var pieChartData = []
    data.map(item => {
        pieChartData.push(
            _.mapKeys(item, (value, key) => {
                let newKey = key;
                if (key === 'magRange') {
                    newKey = 'name';
                }

                if (key === 'value') {
                    newKey = 'y';
                }

                return newKey;
            })
        )
    });

    Highcharts.chart('pie-chart', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Number of earthquakes based on magnitude range'
        },
        subtitle: {
            text: 'Pie Chart'
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                    connectorColor: 'silver'
                }
            }
        },
        series: [{
            name: 'Percentage of Earthquakes',
            data: pieChartData
        }]
    });
}