var currentChange = document.getElementsByClassName('current-change')[0].outerText;
if(currentChange.includes("-")){
    document.getElementsByClassName('current-change')[0].style.color = 'red'
}else{
    document.getElementsByClassName('current-change')[0].style.color = 'green'
}

var onemin = document.getElementById('1min').innerText;
if(onemin.includes("-")){
    document.getElementById('1min').style.color = 'red'
}else{
    document.getElementById('1min').style.color = 'green'
    
}

var fivemin = document.getElementById('5min').innerText;
if(fivemin.includes("-")){
    document.getElementById('5min').style.color = 'red'
}else{
    document.getElementById('5min').style.color = 'green'
}

var onehour = document.getElementById('1hr').innerText;
if(onehour.includes("-")){
    document.getElementById('1hr').style.color = 'red'
}else{
    document.getElementById('1hr').style.color = 'green'
}

var oneday = document.getElementById('1d').innerText;
if(oneday.includes("-")){
    document.getElementById('1d').style.color = 'red'
}else{
    document.getElementById('1d').style.color = 'green'
}

var fivedays = document.getElementById('5d').innerText;
if(fivedays.includes("-")){
    document.getElementById('5d').style.color = 'red'
}else{
    document.getElementById('5d').style.color = 'green'
}


$(document).ready(function () {
    $.getJSON("/fetchprice",
    function getPrice(json) {

        console.log(json)
    });
})

