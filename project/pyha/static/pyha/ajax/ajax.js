	function descriptionAjax() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var description = document.getElementById('description').value;
	var data = 'requestid='+requestid+'&description='+description;
	xhttp.onreadystatechange = function() {
			if (this.readyState == 4) {
				if (this.status == 200) {
					get_request_header();
				} else if(this.status == 310){
					window.location = this.responseText;
				}
			}
		};
	xhttp.open("POST", document.getElementById("setDescriptionURL").value, true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function removeAjax(index, on_success) {
	var xhttp = new XMLHttpRequest();
	var collectionid = document.getElementById('removecollectionId'+index).value;
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid+'&collectionId='+collectionid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
				if(this.status == 200){
					on_success();
				} else if(this.status == 310){
					window.location = this.responseText;
				}
			}
		};
	xhttp.open("POST", document.getElementById("removeCollectionURL").value, true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function get_collection_tab() {
		var xhttp = new XMLHttpRequest();
		var requestid = document.getElementById('requestid').value;
		var data = 'requestid='+requestid;
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4) {
				if (this.status == 200) {
					document.getElementById("collectiontable").innerHTML = this.responseText;
				} else if(this.status == 310){
					window.location = this.responseText;
				}
			}
		};
		xhttp.open("POST", document.getElementById("getCollectionURL").value, true);
		xhttp.setRequestHeader('X-CSRFToken', csrftoken);
		xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
		xhttp.send(data);
		}

	function get_request_header() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
			if (this.status == 200) {
				document.getElementById("request_header").innerHTML = this.responseText;
				checkHasDescription();
			} else if(this.status == 310){
				window.location = this.responseText;
			}
		}
	};
	xhttp.open("POST", document.getElementById("getDescriptionURL").value, true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function get_summary_tab() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
			if (this.status == 200) {
				for (i = 0; i < document.getElementsByName("summarytable").length; i++){
					document.getElementsByName("summarytable")[i].innerHTML = this.responseText;
				}
			} else if(this.status == 310){
				window.location = this.responseText;
			}
		}
	};
	xhttp.open("POST", document.getElementById("getSummaryURL").value, true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function create_contact(id) {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid+'&id='+id;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
			if (this.status == 200) {
				var contacthtml = sessionStorage.getItem("contacts"+requestid);
				var xmlcontent = this.responseXML;
				if(contacthtml != null){
					contacthtml += this.responseText;
				}else{
					contacthtml = this.responseText;
				}
				//sessionStorage.setItem("contacts"+requestid, contacthtml);
				var end = document.getElementById("contacts_content_end");
				end.insertAdjacentHTML('beforebegin', new XMLSerializer().serializeToString(xmlcontent.getElementsByTagName("contact")[0].getElementsByTagName("div")[0]));
				end = document.getElementById("modal_contacts_end");
				end.insertAdjacentHTML('beforebegin', new XMLSerializer().serializeToString(xmlcontent.getElementsByTagName("modal")[0].getElementsByTagName("div")[0]));
				end = document.getElementById("pdf_contacts_end");
				end.insertAdjacentHTML('beforebegin', new XMLSerializer().serializeToString(xmlcontent.getElementsByTagName("modal")[0].getElementsByTagName("div")[0]));
				end = document.getElementById("summary_contacts_end");
				end.insertAdjacentHTML('beforebegin', new XMLSerializer().serializeToString(xmlcontent.getElementsByTagName("summary")[0].getElementsByTagName("tr")[0]));
				contactsFilled();
				var fields = ["request_person_name_"+id,"request_person_street_address_"+id,"request_person_postal_code_"+id,"request_person_post_office_name_"+id,"request_person_country_"+id,"request_person_email_"+id,"request_person_phone_number_"+id,"request_person_organization_name_"+id,"request_person_corporation_id_"+id];
				var fills = ["contact_name_"+id,"contact_street_address_"+id,"contact_postal_"+id,"contact_post_office_"+id,"contact_country_"+id,"contact_email_"+id,"contact_phone_number_"+id,"contact_corporation/organization_"+id,"contact_corporation_id_"+id];
				for (i = 0; i < fields.length; i++){
					var namefield = document.getElementById(fields[i]);
					var fillfield = document.getElementsByName(fills[i]);
					if(i == 0){
						namefield.onkeyup = updateTabField(namefield, fillfield, id);
						namefield.onchange = updateTabField(namefield, fillfield, id);
					}else{
						namefield.onkeyup = updateField(namefield, fillfield);
						namefield.onchange = updateField(namefield, fillfield);
						updateField(namefield, fillfield)();
					}
				}
				document.getElementById("contact_tab_button_"+id).click();
			} else if(this.status == 310){
				window.location = this.responseText;
			}
		}
	};

	xhttp.overrideMimeType('text/xml');
	xhttp.open("POST", document.getElementById("createContactURL").value, true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}


	function updateTabField(namefield, fillfield, id){
	return function() { document.getElementById("contact_tab_text_"+id).textContent = namefield.value;
						for(var e in fillfield){
							fillfield[e].textContent = namefield.value;
						}
						contactsFilled();
						}
	}

	function updateField(namefield, fillfield){
	return function() { for(var e in fillfield){
							fillfield[e].textContent = namefield.value;
						}
						contactsFilled();
						}
	}

	function updateArgumentField(namefield, fillfield){
	return function() { for(var e in fillfield){
							fillfield[e].textContent = namefield.value;
						}
						argumentsFilled();
						}
	}

	function refresh_skip_official(){
	get_collection_tab()
	get_summary_tab();
	}

	function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
	}

	function download() {
		var fields = ["requestid", "format", "geometry", "CRS"];
		var data = "";
		for (var i = 0; i < fields.length; i++) {
		    data += fields[i] + "=" + document.getElementById(fields[i]).value + "&";
		}
		data += "fileType=" + document.querySelector("input[name='fileType']:checked").value;

        updateProgressBar();
		$("#loading-modal").modal('show');

		var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
				if (this.status == 200) {
				    var jsonResponse = JSON.parse(this.responseText);
				    if (jsonResponse["status"] === "complete") {
				    	downloadSuccess(jsonResponse);
				    } else {
				        updateProgressBar(jsonResponse["progressPercent"]);
				        pollDownloadStatus(jsonResponse["statusUrl"]);
				    }
				} else {
				    downloadError(this.responseText);
				}
            }
        };
        xhttp.open("POST", document.getElementById("getDownloadURL").value, true);
        xhttp.setRequestHeader("X-CSRFToken", csrftoken);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send(data);
	}

	function pollDownloadStatus(url) {
	    var xhttp = new XMLHttpRequest();
	    xhttp.onreadystatechange = function() {
		    if (this.readyState == 4) {
				if (this.status == 200) {
				    var jsonResponse = JSON.parse(this.responseText);
				    if (jsonResponse["status"] === "complete") {
				        downloadSuccess(jsonResponse);
				    } else {
                        updateProgressBar(jsonResponse["progressPercent"]);

                        setTimeout(() => {
                            pollDownloadStatus(url);
                        }, 5000);
				    }
				} else {
				    downloadError(this.responseText);
				}
			}
		};
	    xhttp.open("GET", url, true);
	    xhttp.send();
	}

	function updateProgressBar(progressPercent) {
		var progressBar = document.getElementById("loadingProgressBar");
		progressBar.innerHTML = progressPercent == null ? "" : progressPercent + "%";
		progressBar.style.width = progressPercent == null ? "100%" : progressPercent + "%";
	}

	function downloadSuccess(jsonResponse) {
	    $("#loading-modal").modal("hide");
        window.location = jsonResponse["downloadUrl"];
	}

	function downloadError(responseText) {
	    var errorTextInputId = "getDownloadFailedText";
	    try {
	        var jsonResponse = JSON.parse(responseText);
	        var errName = jsonResponse["errName"];
	        if (errName === "too_complex") {
	            errorTextInputId = "getDownloadFailedTooComplexText";
	        }
	    } catch (e) {}

	    $("#loading-modal").modal("hide");
	    alert(document.getElementById(errorTextInputId).value);
	}

	function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');
