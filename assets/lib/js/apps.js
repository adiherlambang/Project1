$('#getConfig').on("click", function() {
    $.ajax({
        url: '/getConfig',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            alert(JSON.stringify(resData))
        },
        error: function (error) {
            console.log("Error getting configuration")
        }
    });
});


$('#getInvent').on("click", function() {
    $.ajax({
        url: '/getInvent',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            alert(JSON.stringify(resData))
        },
        error: function (error) {
            console.log("Error getting Inventory")
        }
    });
});


$('#getMemUtils').on("click", function() {
    $.ajax({
        url: '/getMemUtils',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            alert(JSON.stringify(resData))
        },
        error: function (error) {
            console.log("Error getting Memmory Utilization")
        }
    });
});


$('#getCPUUtils').on("click", function() {
    $.ajax({
        url: '/getCPUUtils',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            alert(JSON.stringify(resData))
        },
        error: function (error) {
            console.log("Error getting Memmory Utilization")
        }
    });
});

$('#getCDP').on("click", function() {
    alert("working get CDP Neighbours");
});


$('#getCRCinterface').on("click", function() {
    alert("working get CRC Interface");
});


$('#getEnvi').on("click", function() {
    alert("working get Environment");
});

$('#getCustom').on("click", function() {
    alert("working get Custom Command");
});