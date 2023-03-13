let LINEDATA = [];
let data = [];
let labels = [];
var response = '';
var frequency = 'daily';
var model = 'SalesOrder';
var days = '30'
var myChart = null
var tooltip_data = 'count'
var model_dict = {}
console.log('hii')

let STATE = {
  models: [],
  fields: [],
  days: 30,
  freq: 'daily'
}

function graph(model, frequency, days, tooltip_data) {
  console.log('hii')
  if(myChart != null){
    myChart.destroy();
  }

  $.ajax({url: "/get/" + model + '/' + days, success: function(response){
    response = JSON.parse(response);
    response_data = { ...response };

    if((response == {}) || (tooltip_data == null)){
      return
    }
    console.log(tooltip_data)

    keys = tooltip_data.split('(')
    key1 = keys[0]
    key2 = keys[1].slice(0, -1)
    console.log('tooltip data', tooltip_data, response, key1, key2)
    LINEDATA = response_data[key1][key2][frequency];

    data = Object.keys(LINEDATA).map(key => LINEDATA[key]);
    // tooltip_data = Object.keys(tooltip_total).map(key => LINEDATA[key]);
    labels = Object.keys(LINEDATA);
    // console.log(model+" Linedata-- "+LINEDATA+"  data--- "+data+" labels----- "+labels+" Tooltip total -------"+ tooltip_total)

    const labelTooltip = (context)=>{
      // console.log("Tooltip -------- "+context.dataset.data)
      // console.log("parsed y -------- "+tooltip_total)
      if(tooltip_data=="count")
        return "Count : " + LINEDATA[context.label]
      if(tooltip_data=="sum" && ("sum" in response_data['create_date']))
        return "Sum : " + tooltip_total[context.label]
      if(tooltip_data=="count+sale" && ("sum" in response_data['create_date']))
        return "Count : " + LINEDATA[context.label] + "\nSum : " + tooltip_total[context.label]
    };

    myChart = new Chart(document.getElementById("chart"), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: model,
            data: data,
            borderColor: "#3e95cd",
            backgroundColor: '#7D97FF',
          }
        ]
      },
      options:{
        resoponsive: true,
        plugins:{
          tooltip:{
            callbacks:{
              label: () => tooltip_data,
            }
          }
        },
        scales:{
          x: 
            {
                reverse: true,
            }
        },
      },
    });
  }});
}


function feth_models() {

  $.ajax({url: "/get/models", success: function(response){
    response = JSON.parse(response);
    // model_dict = { ...response['models'] };
    STATE.models = response.models
    createModelSelect('')
  }});
}

function feth_tooltip(model, days) {
  console.log('fetch fields ', model, days)

  $.ajax({
    url: `/get/${model}/${days}`,
    success: function (response) {
      response = JSON.parse(response);
      console.log('fetch fields ', response)
      $('#tooltip_data')
        .find('option')
        .remove()
        .end()
      
      Object.keys(response).forEach(fname => {
          Object.keys(response[fname]).forEach(field => {
            $('#tooltip_data').append(`<option value="${fname}(${field})">
                                       ${fname}(${field})
                                  </option>`);
          })
      })
      graph(model, $('#frequency').val(), days, $('#tooltip_data').val());
    }
  });
}

function createModelSelect(params) {
  // const model_list = Object.keys(model_dict);
  const model_list = STATE.models
  // const modelValues = Object.values(model_dict);

  const models_select = document.querySelector('select#model');
  for (let index = 0; index < model_list.length; index++) {
    const element = model_list[index];
    console.log("Models ----"+ element);
    models_select.options.add(new Option(element, element));
  }
}

function feth_fields(model) {
    console.log("Inside fetch fields ---"+model)
    // const modelValues = Object.values(model_dict);

    const field_select = document.querySelector('select#tooltip_data');
    $('select#tooltip_data').find('option[value="sum"]').remove();
    $('select#tooltip_data').find('option[value="count"]').remove();
    $('select#model').find('option[value="default"]').remove();

    
    if(model_dict[model]){
      countModel = "count("+model+")" ;
      sumModel = "sum("+model+")" ;
      console.log("model_dict: -------"+ model_dict[model])
      if(model_dict[model].includes(countModel)){
        field_select.options.add(new Option('Count', 'count'));
      }
      if(model_dict[model].includes(sumModel)){
        field_select.options.add(new Option('Sum', 'sum'));
      }
    }
    else{
      console.log("Inside ELSE of fetch_tooltip");
    }
}

$(document).ready(function(){
  feth_models();
  // createModelSelect();
  // feth_tooltip(model);


  $('select#days').on('change', function() {
    days = this.value;
    console.log( days );
    graph(model, frequency, days, tooltip_data);
  });

  $('select#frequency').on('change', function() {
    frequency = this.value;
    console.log( frequency );
    graph(model, frequency, days, tooltip_data);
  });

  $('select#model').on('change', function() {
    model = this.value;
    console.log( model );

    feth_tooltip(model, $('#days').val());
  });

  $('select#tooltip_data').on('change', function() {
    tooltip_data = this.value;
    console.log( tooltip_data );
    graph(model, frequency, days, tooltip_data);
  });

  graph('', frequency, days, '');
});
