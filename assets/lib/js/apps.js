var progressBar = document.getElementById("progress-bar");
var loading = document.getElementById("loading");
const modalTitle = document.getElementById("appsModalTitle");
// modalTitle.innerHTML='asd';
var id;

function showLoading() {
    $('#flashContainer').html('');
    $('#appsModalBody').html('');
    var loading = document.getElementById("loading");
    loading.classList.remove("d-none");
    $('#warningProcess').show();
}
  
function hideLoading() {
    var loading = document.getElementById("loading");
    loading.classList.add("d-none");
    $('#warningProcess').hide();
}

$('#modalButton').on("click", function(e) {
    $('#appsModal').modal('hide'); 
});

$('#getConfig').on('click', function(event) {
    event.preventDefault();
    $('#appsModal').modal({
        backdrop: 'static',
        keyboard: false
    }).modal('show');
    
    // var alert = '<div class="alert alert-info floating-alert fade show">'+
    //             'Getting Configuration Device Success'+
    //             '</div>'
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
        },
        error: function(xhr, status, error) {
            hideLoading()
            console.error('Error:', error);
            var flashList = $('<ul>').addClass('flash-messages');
            flashList.append($('<li>').text('Error: '+error));
            flashContainer.append(flashList);
        },
        complete: function(){
            // $('#layoutSidenav_content').append(messages)
            // setTimeout(function() {
            //     $('.alert').alert('close')
            // }, 2000); 
            var closedModal = $('<a href="#" class="btn btn-primary">Close</a>');
            $('#appsModalFooter').append(closedModal);

            closedModal.click(function () {  
                $('#appsModal').modal('hide'); 
                $(this).remove();
            })
        }
    })
});


$('#getInvent').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting Inventory Device Success'+
                '</div>'
    modalTitle.innerHTML="Get Inventory Devices"
    showLoading()
    $.ajax({
        url: '/getInvent',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            hideLoading()
            // alert(JSON.stringify(resData))
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
        },
        complete: function(){
            // $('#layoutSidenav_content').append(alert)
            // setTimeout(function() {
            //     $('.alert').alert('close')
            // }, 2000); 
            var closedModal = $('<a href="#" class="btn btn-primary">Close</a>');
            $('#appsModalFooter').append(closedModal);

            closedModal.click(function () {  
                $('#appsModal').modal('hide'); 
                $(this).remove();
            })
        },
        error: function (xhr, status, error) {
            hideLoading()
            console.error('Error:', error);
            var flashList = $('<ul>').addClass('flash-messages');
            flashList.append($('<li>').text('Error: '+error));
            flashContainer.append(flashList);
        }
    });
});


$('#getMemUtils').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting Memmory Utilization Success'+
                '</div>'
    modalTitle.innerHTML="Get Memmory Utilization Devices"
    showLoading()
    $.ajax({
        url: '/getMemUtils',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            hideLoading()
            // alert(JSON.stringify(resData))
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
        },
        error: function(xhr, status, error) {           
            if (xhr.status === 500) {
                hideLoading()
                console.log("Error: "+error);
                var messages = ["Error API getting memory utilization, please contact the administrator"];
                var flashContainer = $('#flashContainer');
                if (messages.length > 0) {
                    var flashList = $('<ul>').addClass('flash-messages');
                    messages.forEach(function(message) {
                        flashList.append($('<li>').text(message));
                    });
                flashContainer.append(flashList);
                }
            }else{
                hideLoading()
                console.log("Error API getting Memory Utilization");
                var messages = ["Error API getting memory utilization, please contact your administrator"];
                var flashContainer = $('#flashContainer');
                if (messages.length > 0) {
                    var flashList = $('<ul>').addClass('flash-messages');
                    messages.forEach(function(message) {
                        flashList.append($('<li>').text(message));
                    });
                flashContainer.append(flashList);
                }
            }
        }
    });
});


$('#getCPUUtils').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting CPU Utilization Success'+
                '</div>'
    modalTitle.innerHTML="Get CPU Utilization Devices"
    showLoading()
    $.ajax({
        url: '/getCPUUtils',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            hideLoading()
            // alert(JSON.stringify(resData))
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
        },
        complete: function(){
            $('#layoutSidenav_content').append(alert)
            setTimeout(function() {
                $('.alert').alert('close')
            }, 2000); 

        },
        error: function (error) {
            console.log("Error getting Memmory Utilization")
        }
    });
});

$('#getCDPDevice').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting CDP Neighbours Success'+
                '</div>'
    modalTitle.innerHTML="Get CDP Neighbours Devices"
    showLoading()
    $.ajax({
        url: '/getCDP',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            hideLoading()
            // alert(JSON.stringify(resData))
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
        },
        complete: function(){
            $('#layoutSidenav_content').append(alert)
            setTimeout(function() {
                $('.alert').alert('close')
            }, 2000); 

        },
        error: function (error) {
            console.log("Error getting CDP Neighbours Devices")
        }
    });
});


$('#getCRCinterface').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var crcMenu1 = '<div class="card mb-3"> <div class="card-body text-center"> <i class="fas fa-network-wired fa-2x mb-3"></i> <h5 class="card-title">Get all CRC from all devices</h5> <button id="getCRCinterfaceAll" class="btn btn-primary">Start</button> </div> </div>';
    var crcMenu2 = '<div class="card mb-3"> <div class="card-body text-center"> <i class="fas fa-list fa-2x mb-3"></i> <h5 class="card-title">Get CRC from interface listed</h5> <button id="getCRCfromInterfaceList" class="btn btn-primary">Start</button> </div> </div>';
    var closeCRCMenu = $('<button type="button" class="btn btn-secondary" id="modalButton">Close</button>');
    modalTitle.innerHTML="Get CRC Interface Devices";
    $('#warningProcess').html('');
    $('#appsModalBody').html("");
    $('#appsModalBody').html(crcMenu1+crcMenu2);
    $('#appsModalFooter').append(closeCRCMenu);

    closeCRCMenu.click(function () {  
        $('#appsModal').modal('hide'); 
        $(this).remove();
    })

    $('#getCRCinterfaceAll').on("click",function () {  
        showLoading()
        $.ajax({
            url: '/getCRCAll',
            type: 'post',
            contentType: 'application/json',
            // data: JSON.stringify(chat),
            success: function (resData) {
                hideLoading()
                console.info(resData)
                // alert(JSON.stringify(resData))
                var messages = resData.data;
                var flashContainer = $('#flashContainer');
                if (messages.length > 0) {
                    var flashList = $('<ul>').addClass('flash-messages');
                    messages.forEach(function(message) {
                        flashList.append($('<li>').text(message));
                    });
                flashContainer.append(flashList);
                }
            },
            complete: function(){
                // $('#layoutSidenav_content').append(alert)
                // setTimeout(function() {
                //     $('.alert').alert('close')
                // }, 2000); 

            },
            error: function (error) {
                console.error(error)
                console.log("Error getting CRC Interface Devices")
            }
        });
    })

    $('#getCRCfromInterfaceList').on("click",function () {  
        showLoading()
        $.ajax({
            url: '/getCRClisted',
            type: 'post',
            contentType: 'application/json',
            // data: JSON.stringify(chat),
            success: function (resData) {
                hideLoading()
                // alert(JSON.stringify(resData))
                var messages = resData.data;
                var flashContainer = $('#flashContainer');
                if (messages.length > 0) {
                    var flashList = $('<ul>').addClass('flash-messages');
                    messages.forEach(function(message) {
                        flashList.append($('<li>').text(message));
                    });
                flashContainer.append(flashList);
                }
            },
            complete: function(){
                // $('#layoutSidenav_content').append(alert)
                // setTimeout(function() {
                //     $('.alert').alert('close')
                // }, 2000); 

            },
            error: function (error) {
                console.log("Error getting CRC Interface Devices")
            }
        });
    })
    // showLoading()
    // $.ajax({
    //     url: '/getCRC',
    //     type: 'post',
    //     contentType: 'application/json',
    //     // data: JSON.stringify(chat),
    //     success: function (resData) {
    //         hideLoading()
    //         // alert(JSON.stringify(resData))
    //         var messages = resData.data;
    //         var flashContainer = $('#flashContainer');
    //         if (messages.length > 0) {
    //             var flashList = $('<ul>').addClass('flash-messages');
    //             messages.forEach(function(message) {
    //                 flashList.append($('<li>').text(message));
    //             });
    //         flashContainer.append(flashList);
    //         }
    //     },
    //     complete: function(){
    //         $('#layoutSidenav_content').append(alert)
    //         setTimeout(function() {
    //             $('.alert').alert('close')
    //         }, 2000); 

    //     },
    //     error: function (error) {
    //         console.log("Error getting CRC Interface Devices")
    //     }
    // });
});


$('#getEnvi').on("click", function() {
    alert("working get Environment");
});

$('#getCustomCmd').on("click", function(event) {
    event.preventDefault();
    $('#appsModal').modal('show'); 
    var alert = '<div class="alert alert-info floating-alert fade show">'+
                'Getting Custom Command Success'+
                '</div>'
    modalTitle.innerHTML="Get Custom Command"
    showLoading()
    $.ajax({
        url: '/customPage',
        type: 'post',
        contentType: 'application/json',
        // data: JSON.stringify(chat),
        success: function (resData) {
            hideLoading()
            // alert(JSON.stringify(resData))
            var messages = resData.data;
            var flashContainer = $('#flashContainer');
            if (messages.length > 0) {
                var flashList = $('<ul>').addClass('flash-messages');
                messages.forEach(function(message) {
                    flashList.append($('<li>').text(message));
                });
            flashContainer.append(flashList);
            }
        },
        complete: function(){
            $('#layoutSidenav_content').append(alert)
            setTimeout(function() {
                $('.alert').alert('close')
            }, 2000); 

        },
        error: function (error) {
            console.log("Error getting Custom Command")
        }
    });
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
                if (resData['status']===true){
                    clearFileInput('csvFileInput')
                    location.reload();
                }else{
                    alert(resData['message'])
                    console.error(resData)
                }              
            },
            error: function (error) {
                console.log("Error while uploading file,"+error)
                // alert(error)
            }
        });
    }
});

$('#uploadInterfaceCRCfile').on("click", function() {
    const csvFileInput = document.querySelector("#interfaceCRClist");
    const file = csvFileInput.files[0];

    if (file == null){
        alert("file not selected")
    }else{
        var formData = new FormData();
        formData.append("file", file);
        startProgressAnimation()
        $.ajax({
            url: '/uploadInterfaceCRCfile',
            type: 'post',
            data: formData,
            processData: false,
            contentType: false,
            success: function (resData) {
                // alert(resData)
                clearFileInput('interfaceCRClist')
                setTimeout(function() {
                    location.reload();
                }, 100); // Delay of 100 milliseconds
            },
            error: function (error) {
                console.log("Error while uploading file")
                alert(error)
            }
        });
    }
});

function folderOutput(event) {
    id = event.target.id;; // Get the ID of the current element
    modalTitle.innerHTML=id;

    console.log(modalTitle.innerHTML)

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
};

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