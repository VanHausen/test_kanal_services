//alert('it is work')
function usd2rub(){
        var usd = document.getElementById("usd").value;
        var rate = document.getElementById("rate").innerHTML;
        var rub = usd * rate
        document.getElementById("rub").value = rub
//        console.log(usd)
//        console.log(rate)
//        console.log(rub)
    }
