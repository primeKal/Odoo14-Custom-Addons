
odoo.define("graph_api.frontend_display", function(require){

    "use strict"
    var ajax = require('web.ajax');
    const ctx = document.getElementById('chart').getContext('2d');
var hor = [];
var ver = [];
var x_param = '';
var title = '';
var descri = '';
ajax.rpc('/getting_data').then(function (data) {
console.log('hooray',data)
hor = data['hor'];
ver = data['ver'];
x_param = data['x_param']
hor.forEach( function ( date){
    console.log(date)
    date = String(date).concat(" GMT+0800")
    console.log(date)
//    date= Date.parse(date)
//    console.log(date)
////    date = new Date(date)
})
console.log('hooray',ver);
title = data['title'];
descri = data['descr'];
$("h1").val(title)
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
//        labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
        labels: hor,
        datasets: [{
            label: descri,
//            data: [12, 19, 3, 5, 2, 3],
            data: ver,
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
              x: {
                type: 'time',
                time : {
                    unit: x_param,
                    displayFormats: {
                       'day': 'MMM dd',
                       'week': 'MMM dd',
                       'month': 'MMM yyyy',
                       'quarter': 'MMM dd',
                       'year': 'yyyy',
                      }

                    }
               },
            y: {
                beginAtZero: true
            }
        }
    }
});
});
//    console.log(hor);
//    console.log(ver);
});