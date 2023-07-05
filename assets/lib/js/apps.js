var progressBar = document.getElementById("progress-bar");
var loading = document.getElementById("loading");

function showLoading() {
    $('#flashContainer').html('');
    $('#appsModalBody').html('');
    var loading = document.getElementById("loading");
    loading.classList.remove("d-none");
}
  
function hideLoading() {
    var loading = document.getElementById("loading");
    loading.classList.add("d-none");
}

$('#modalButton').on("click", function(e) {
    $('#appsModal').modal('hide'); 
});

$('#getConfig').on('click', function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    const modalTitle = document.getElementById("appsModalTitle");
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting Configuration Device Success'+
                '</div>'
    modalTitle.innerHTML="Get Configuration Devices"
    showLoading()
    $.ajax({
        url: '/getConfig',
        type: 'post',
        contentType:'application/json',
        success: function(resData){
            hideLoading()
            console.log(resData)
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
            // var alertInfo = '<div class="alert alert-info floating-alert fade show">'+
            //     'Getting Configuration Device, Please Wait'+
            //     '</div>'
            // $('#layoutSidenav_content').append(alertInfo)
        },
        complete: function(){
            $('#layoutSidenav_content').append(alert)
            setTimeout(function() {
                $('.alert').alert('close')
            }, 2000); 

        }
    })
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

function clearFileInput(id) 
{ 
    var oldInput = document.getElementById(id); 

    var newInput = document.createElement("input"); 

    newInput.type = "file"; 
    newInput.id = oldInput.id; 
    newInput.name = oldInput.name; 
    newInput.className = oldInput.className; 
    newInput.style.cssText = oldInput.style.cssText; 
    newInput.accept = oldInput.accept;
    // TODO: copy any other relevant attributes 

    oldInput.parentNode.replaceChild(newInput, oldInput); 
}

function startProgressAnimation() {
    loading.classList.remove("d-none");
   
    progressBar.style.width = "0%";
    progressBar.setAttribute("aria-valuenow", "0");
  
    var intervalId = setInterval(incrementProgress, 100);
  
    function incrementProgress() {
      var currentValue = parseInt(progressBar.getAttribute("aria-valuenow"));
      if (currentValue >= 100) {
        clearInterval(intervalId);
        setTimeout(resetProgressBar, 2000);
        
      } else {
        var newValue = currentValue + 50;
        progressBar.style.width = newValue + "%";
        progressBar.setAttribute("aria-valuenow", newValue.toString());
      }
    }
  }

  function resetProgressBar() {
    progressBar.style.width = "0%";
    progressBar.setAttribute("aria-valuenow", "0");
    
    loading.classList.add("d-none");
  }


$('#uploadButton').on("click", function() {
    const csvFileInput = document.querySelector("#csvFileInput");
    const file = csvFileInput.files[0];

    if (file == null){
        alert("file not selected")
    }else{
        var formData = new FormData();
        formData.append("file", file);
        startProgressAnimation()
        $.ajax({
            url: '/uploadCSV',
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            success: function (resData) {
                // alert(resData)
                clearFileInput('csvFileInput')
                location.reload();
            },
            error: function (error) {
                console.log("Error while uploading file")
                alert(error)
            }
        });
    }
});

$('.folderOutput').on("click", function(event) {
    event.preventDefault();
    let id;
    
    $('.folderOutput').each(function() {
        id = $(this).attr('id'); // Get the ID of the current element
        const modalTitle = document.getElementById("appsModalTitle");
        modalTitle.innerHTML=id
    });

    $('#appsModal').modal('show'); 
    const folder={
        'name':id
    }
    var tableBody = $('#dataTable');
    tableBody.empty();
    $.ajax({
        url: '/getOutput',
        type: 'post',
        data: JSON.stringify(folder),
        contentType: 'application/json',
        success: function (resData) {
            // console.log(resData)
            resData.forEach(function(item,index) {
                // console.log(item)
                setTimeout(function () {
                    var tableRow = $('<tr>').append($("<td>", { html: index+1 }),$("<td>", { html: item }),$("<td><a class='downloadFile' onClick='downloadFile()' id="+item+" href='#'><i class='fas fa-download'>"));                    
                      $('#dataTable').append(tableRow);
                }, 500);
            });
            
        },
        error: function (error) {
            console.log("Error"+error)
        }
    });
});

function downloadFile() {
    const id = document.querySelector(".downloadFile");
    const path = document.querySelector("#appsModalTitle");
    const pathFile={
        'folder': path.innerHTML,
        'file':id.id
    }
    $.ajax({
        url: '/downloadFile',
        type: 'post',
        data: JSON.stringify(pathFile),
        success: function (data) {
            // console.log(typeof data)
            var url;
            if (typeof window.navigator.msSaveBlob !== 'undefined') {
                // For Internet Explorer
                window.navigator.msSaveBlob(data, id.id);
            } else {
                // Create a Blob object from the response data
                var blob = new Blob([data]);

                // Use the fallback approach
                url = URL.createObjectURL(blob);

                // Create a temporary link element
                var link = document.createElement('a');
                link.href = url;
                link.download = id.id;

                // Append the link to the document and trigger the download
                document.body.appendChild(link);
                link.click();

                // Clean up the temporary link and object URL
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }
        },
        error: function(xhr, status, error) {
            alert('Error occurred during file download.',error);
            console.log(error)
        }
    });
};