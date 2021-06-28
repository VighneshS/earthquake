var spinner
var figure

$(function () {
    spinner = $('#spinner')
    figure = $('#figure')
    spinner.show()
    figure.hide()
    loadChart()
});

function loadChart() {
    spinner.show()
    figure.hide()
    var countryName = $("#countryName")
    $.ajax({
        type: 'POST',
        url: "/graphs/2",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify({
            'countryName': countryName.val()
        })
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
            text: 'Number of Volcanoes based on Longitude range'
        },
        subtitle: {
            text: 'Bar Chart'
        },
        xAxis: {
            categories: categories,
            crosshair: true,
            title: {
                text: 'Volcano Longitude Range'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Number of Volcanoes'
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
                dataLabels: {
                    enabled: true
                },
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
            name: 'Number of Volcanoes',
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
            height: "50%",
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Number of Volcanoes based on Longitude range'
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
            name: 'Percentage of Volcanoes',
            data: pieChartData
        }]
    });
}