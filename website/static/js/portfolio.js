$(document).ready(function(){
    load_data();
    function load_data(query='')
    {
        $.ajax({
            url:"/fetchvalue",
            method:"POST",
            data:{query:query},
            success:function(data)
            { 
                $('main').html(data);
                $('main').append(data.value);
            }
        })
    }

    $('#search_filter').change(function(){
        $('#hidden_value').val($('#search_filter').val());
        var query = $('#hidden_value').val(); 
        load_data(query);
    });
    
});

$(document).ready(function () {
    $.getJSON("/myportfolio",
    function getPortfolio(json) {
        
        var table = document.getElementById("portfolio");
        var e = document.getElementById('e');
        e.href = "/editportfolio"
        
        var d = document.getElementById('d');
        d.href = "/deleteportfolio"

        var tableHTML = `<tr>
            <th>Stock</th>
            <th>Quantity</th>
            <th>Initial Value</th>
            <th>Current Price</th>
            <th>Total cost</th>
            <th>Current value</th>
            <th>PnL</th>
            <th>PnL (%)</th>
        </tr>`;

        var portfolioCost = 0;
        var portfolioCurrent = 0;
        var portfolioProfit = 0;

        for (var i = 0; i < json.length; i++) {

            var id = json[i].id;
            var ticker = json[i].symbol;
            var currentPrice = json[i].currentprice;
            var initialValue = json[i].initial_value;
            var totalShares = json[i].quantity;
            var totalCost  = json[i].totalcost;
            var currentValue  = json[i].currentvalue;
            var profit = json[i].profit;

            var percentChange = percentChangeCalc(totalCost, currentValue);
            
            row = "<tr>";
            row += "<td data-label=Stock>" + ticker + '<a href="' + e +'/'+ id + '">'+"<i class='bx bxs-edit'></i>"+'</a>' + '<a href="' + d +'/'+ id + '">'+"<i class='bx bxs-trash' >"+'</a>'; +"</td>";
            row += "<td data-label=Quantity>" + totalShares + "</td>";
            row += "<td data-label=InitialValue>$" + initialValue.toFixed(2) + "</td>";
            row += "<td data-label=CurrentPrice>$" + currentPrice + "</td>";
            row += "<td data-label=TotalCost>$" + totalCost.toFixed(2)  + "</td>";
            row += "<td data-label=CurrentValue>$" + currentValue.toFixed(2) + "</td>";
            row += profitRow(profit);
            row += percentChangeRow(percentChange);
            row += "</tr>";
            tableHTML += row;

            portfolioCost += totalCost;
            portfolioCurrent += currentValue;
            portfolioProfit += profit;


        }

        portfolioPercentChange = percentChangeCalc(portfolioCost, portfolioCurrent);
        portfolioProfitChange = portfolioProfit;

        tableHTML += "<tr>";
        tableHTML += "<th>Total</th>";
        tableHTML += "<th>&nbsp;</th>";
        tableHTML += "<th>&nbsp;</th>";
        tableHTML += "<th>&nbsp;</th>";
        tableHTML += "<td data-label=PortfolioCost>$" + portfolioCost.toFixed(2) + "</td>";
        tableHTML += "<td data-label=PortfolioValue>$" + portfolioCurrent.toFixed(2) + "</td>";
        tableHTML += profitRow(portfolioProfitChange);
        tableHTML += percentChangeRow(portfolioPercentChange);
        tableHTML += "</tr>"

        table.innerHTML = tableHTML;

        console.log(json)
    });
})

function getPortfolio(json) {
    fetch("/myportfolio")
        .then(response => response.json())
        .then(data => {

            console.log(data);

        });
}

function percentChangeCalc(x, y) {
    return (x != 0 ? (y - x) * 100 / x : 0);
}

function percentChangeRow(percentChange) {
    if (percentChange > 0) {
        return "<td class='positive' data-label=PnL(%)>+" + percentChange.toFixed(2) + "%</td>";
    }
    else if (percentChange < 0) {
        return "<td class='negative' data-label=PnL(%)>" + percentChange.toFixed(2) + "%</td>";
    }
    else {
        return "<td data-label=PnL(%)>" + percentChange.toFixed(2) + "%</td>";
    }
}

function profitRow(profit) {
    if (profit > 0) {
        return "<td class='positive' data-label=PnL>+$" + profit.toFixed(2) + "</td>";
    }
    else if (profit < 0) {
        var x = profit *= -1
        return "<td class='negative' data-label=PnL>-$" + x.toFixed(2) + "</td>";
    }
    else {
        return "<td data-label=CurrentValue data-label=PnL>$" + profit.toFixed(2) + "</td>";
    }
}

getPortfolio();

setInterval(function() {
getPortfolio()
}, 10000)