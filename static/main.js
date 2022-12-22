var anHttpRequestServices = new XMLHttpRequest();
var HttpClient = function() {
    
    this.get = function(url, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.onreadystatechange = function() { 
            if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200)
                aCallback(anHttpRequest.responseText);
            
        }

        anHttpRequest.open( "GET", url, true );            
        anHttpRequest.send( null );
    }

    this.post = function(url, data, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.open( "POST", url, true );
        anHttpRequest.onreadystatechange = function() { 
            if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200)
                aCallback(anHttpRequest.responseText);
            else if (anHttpRequest.readyState == 4 && anHttpRequest.status != 200)
                message_center("[ERROR] status_code:" + anHttpRequest.status + " " + anHttpRequest.statusText , false);
        }
        anHttpRequest.send( data );
        
    }

}

function make_url(url)
{
    var the_arr = url.split('/');
    the_arr.pop();
    return( the_arr.join('/') );
}

function notify(text, action)
{
    const toastLive = document.getElementById("liveToast");
    const message_toast = document.getElementById("message-toast");
    toastLive.style.backgroundColor = "white";
    if(!action){
        //toastLive.style.backgroundColor = "#e84118";
        message_toast.style.color="#e84118";
    }

    message_toast.innerHTML=text;
    
    var toast = new bootstrap.Toast(toastLive, {
        keyboard: false
    });
    
    
    toast.show();

}


//form 
tab_tredesicion();
function tab_tredesicion()
{
    var url = make_url(window.location.href) + "/brands";
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);
        console.log(data);

        if(!data.error)
        {
            const brands = document.getElementById("brand_id");
            data.data.map(function(item){
                const _option = document.createElement("option");

                _option.value=item.id;
                _option.innerHTML=item.name;
                brands.appendChild(_option);
            });
            
        }
        else {
            notify("Getting brands error " + data.msg, false);
        }
    });
    
    // countries
    var url = make_url(window.location.href) + "/countries";
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);
        console.log(data);

        if(!data.error)
        {
            const countries = document.getElementById("country_mcc");
            const mccRegression = document.getElementById("mccRegression");

            data.data.map(function(item){

                const _option = document.createElement("option");
                _option.value=item.id;
                _option.innerHTML=item.name;
                countries.appendChild(_option);

                const _option_r = document.createElement("option");
                _option_r.value=item.id;
                _option_r.innerHTML=item.name;
                mccRegression.appendChild(_option_r);
                
            });
            
        }
        else {
            notify("Getting countries mcc error " + data.msg, false);
        }
    });

    //templates
    var url = make_url(window.location.href) + "/templates";
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);

        if(!data.error)
        {
            const brands = document.getElementById("template");
            data.data.map(function(item){
                const _option = document.createElement("option");

                _option.value=item.id;
                _option.innerHTML=item.name;
                brands.appendChild(_option);
            });
            
        }
        else {
            notify("Getting templates mcc error " + data.msg, false);
        }
    })
}

//  LINEAR REGRESSION
function start_regression()
{
    const mcc = document.getElementById("mccRegression");
    if(mcc.value == "")
    {
        notify("Fill all the form, please", false);
        return;
    }

    const startDate = document.getElementById("dateRegression");

    document.getElementById("spinnerOpenPush").style.display="block";
    document.getElementById("spinnerDeleviry").style.display="block";
    by_open(startDate.value, mcc)
    by_delivery(startDate.value, mcc)
}

function by_open(startDate, mcc)
{
    const cOpen = document.getElementById("containerOpen");
    cOpen.style.display="none";
    document.getElementById("dashboardOpen").style.display="none";
    var url = make_url(window.location.href) + "/regression/open/" + mcc.value + "/" + startDate;
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);
        cOpen.style.display="block";
        cOpen.innerHTML = "";
        document.getElementById("dashboardOpen").style.display="block";
        document.getElementById("dashboardOpen").innerHTML="";
        if(!data.error)
        {
            if (data.data.length > 0)
            {
                dasboard_linear("dashboardOpen", data.data,"Open_Push","Forecast by opened push");
                const h4 = document.createElement("h4");
                h4.innerHTML = "The best hour is at " + data.bestHour + " with a result of " + data.bestCount;
                cOpen.appendChild(h4);
                notify("Linear Regression by open push is ready...", true);
            }
            else{
                notify("No data was found in the selected country " + mcc.options[mcc.selectedIndex].text , true);
                cOpen.innerHTML="The last execution no data was found";
            }
        }
        else
        {
            notify("Linear Regression by opened push has error " + data.msg, false);
            cOpen.innerHTML="this section has error...";
        }

        document.getElementById("spinnerOpenPush").style.display="none";
    })
}

function by_delivery(startDate, mcc)
{
    const c_delivery = document.getElementById("containerDelivery");
    c_delivery.style.display = "none";
    document.getElementById("dashboardDelivery").style.display="none";
    var url = make_url(window.location.href) + "/regression/delivery/" + mcc.value + "/" + startDate;
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);
        c_delivery.style.display = "block";
        c_delivery.innerHTML="";
        document.getElementById("dashboardDelivery").style.display="block";
        document.getElementById("dashboardDelivery").innerHTML="";

        if(!data.error)
        {
            if (data.data.length > 0)
            {
                dasboard_linear("dashboardDelivery", data.data,"Delivery","Forecast by delevired push");
                const h4 = document.createElement("h4");
                h4.innerHTML = "The best hour is at " + data.bestHour + " with a result of " + data.bestCount;
                c_delivery.appendChild(h4);
                notify("Linear Regression by open container is ready...", true);
            }
            else{
                c_delivery.innerHTML="The last execution no data was found";
                notify("No data was found in the selected country " + mcc.options[mcc.selectedIndex].text , true);
            }
        }
        else
        {
            notify("Linear Regression by open container has error " + data.msg, false);
            c_delivery.innerHTML="this section has error...";
        }

        document.getElementById("spinnerDeleviry").style.display="none";
    })
}

function start_decision()
{
    const universe = document.getElementById("universe").value;
    const brand = document.getElementById("brand_id").value;
    const country = document.getElementById("country_mcc").value;
    const date_time = document.getElementById("campaign_date").value;
    const template = document.getElementById("template").value;

    if(template == "" || universe < 1 || brand == "" || country == "")
    {
        notify("Fill all the form, please", false);
        return;
    }

    const table_result = document.getElementById("tableResult");
    table_result.style.display = "none";

    const result_text = document.getElementById("emptyResultTree");
    result_text.style.display = "none";

    const spinner = document.getElementById("spinnerTree");
    spinner.style.display = "block";

    
    var url = make_url(window.location.href) + "/tree/" + brand+ "/"+ country + "/" + date_time + "/"  + template + "/" + universe;
    var client = new HttpClient();
    client.get(url, function(response) {
        data = JSON.parse(response);
        console.log(data);
        if(!data.error)
        {
            const tbody = document.getElementById("resultDecision");
            tbody.innerHTML = "";
            data.data.map(function(item){
                const tr = document.createElement("tr");
                const td_key = document.createElement("td");
                const td_count = document.createElement("td");
                const td_button = document.createElement("td");

                td_key.innerHTML = item.name;
                td_count.innerHTML = item.total;

                const btn = document.createElement("a");
                btn.classList.add("btn","btn-success","btn-sm");
                btn.innerHTML = "download csv";
                btn.href = make_url(window.location.href) + "/download-csv/" + item.name;

                td_button.appendChild(btn);

                

                tr.appendChild(td_key);
                tr.appendChild(td_count);
                tr.appendChild(td_button);

                tbody.appendChild(tr);
            });

            notify("preddict by tree decision was successful", true);

            if (data.data.length > 0){
                table_result.style.display = "block";
            }
            else{
                result_text.style.display = "block";
                document.getElementById("textResponse").innerHTML="The last execution reponse empty values";
            }
            
        }
        else
        {
            notify("Tree decision error response " + data.msg, false);
            result_text.style.display = "block";
            document.getElementById("textResponse").innerHTML= "The last execution fail";

        }

        spinner.style.display = "none";
    });

}

function dasboard_linear(container, data, _type, _title){
    document.getElementById(container).innerHTML = "";
    const categories = [...new Set(data.map(item => item.hour))];
    const data_series = [ {
            name:_type,
            data: categories.map(hour => {
                var sum_total = 0;
                data.map(item => {
                    if (hour === item.hour)
                        sum_total += item.count;
                })
                return sum_total;
            })
    }];

    const options = {
        chart: {
            type: 'spline'
        },
        title: {
            text: _title
        },
        xAxis: {
            min:0,
            categories: categories,
            crosshair: true,
            offset:0,
        },
        yAxis: {
            title: {
                text: 'Count by hour',
            },
            gridLineColor: '#f39c12'
        },
        tooltip: {
            crosshairs: true,
            shared: true
        },
        credits: {
            enabled: false
        },
        series: data_series
    }

    Highcharts.chart(container, options);
}
