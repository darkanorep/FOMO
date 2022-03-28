const investment_amount = document.getElementById('investment_amount');
const interest_rate = document.getElementById('interest_rate');
const years = document.getElementById('years');

const data = {
  labels: ['Investment', 'Interest', 'Years'],
  datasets: [{
  label: 'ROI Calculator',
  data: [investment_amount.value, interest_rate.value, years.value],
  backgroundColor: [
    'rgb(43, 44, 170,1)',
    'rgba(0,128,0)',
    'rgba(50, 192, 192, 1)'
  ],
  borderColor: [
    'rgba(0,0,0)',            
  ]
}]
};

// config 
const config = {
  type: 'pie',
  data,
  options: {

  }
};

    // render init block
//const myChart = new Chart(
  //document.getElementById('myChart'),
  //config
//);

function updateChart(){
  //myChart.config.data.datasets[0].data = [investment_amount.value,interest_rate.value, years.value];
  //myChart.update();
  
  calculator();
};

function calculator (){
  const cellinvestment = document.getElementById('cellinvestment')
  cellinvestment.innerText = investment_amount.value;

  const cellrate = document.getElementById('cellrate')
  cellrate.innerText = interest_rate.value;

  const cellyear = document.getElementById('cellyear')
  cellyear.innerText = years.value;

  const cellprofit = document.getElementById('cellprofit');
  const profit = investment_amount.value * (interest_rate.value/100) * years.value;
  cellprofit.innerText = profit.toFixed(2);

};