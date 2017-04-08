	function descriptionAjax() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var description = document.getElementById('description').value;
	var data = 'requestid='+requestid+'&description='+description;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			get_request_header();
			}
		};
	xhttp.open("POST", "/pyha/descriptionajax/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}
	
	function removeAjax(index) {
	var xhttp = new XMLHttpRequest();
	var collectionid = document.getElementById('taxoncollectionId'+index).value;
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid+'&collectionId='+collectionid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
				if(this.status == 200){
					refresh();
				} else if(this.status == 310){
					window.location = this.responseText;
				}
			}
		};
	xhttp.open("POST", "/pyha/removeAjax/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}
	
	function get_taxon_tab() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("senstable").innerHTML = this.responseText;
			checksens();
			}
		};
	xhttp.open("POST", "/pyha/getTaxon/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}
	
	function get_custom_tab() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("customtable").innerHTML = this.responseText;
			refreshCheck();
			}
		};
	xhttp.open("POST", "/pyha/getCustom/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}
	
	function get_request_header() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("request_header").innerHTML = this.responseText;
			checkHasDescription();
			}
		};
	xhttp.open("POST", "/pyha/getDescription/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function get_summary_tab() {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			for (i = 0; i < document.getElementsByName("summarytable").length; i++){
				document.getElementsByName("summarytable")[i].innerHTML = this.responseText;
			}
			}
		};
	xhttp.open("POST", "/pyha/getSummary/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
	}

	function create_contact(id) {
	var xhttp = new XMLHttpRequest();
	var requestid = document.getElementById('requestid').value;
	var data = 'requestid='+requestid+'&id='+id;
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
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
			var fields = ["request_person_name_"+id,"request_person_street_address_"+id,"request_person_post_office_name_"+id,"request_person_postal_code_"+id,"request_person_country_"+id,"request_person_email_"+id,"request_person_phone_number_"+id,"request_person_organization_name_"+id,"request_person_corporation_id_"+id];
			var fills = ["contact_name_"+id,"contact_street_address_"+id,"contact_post_office_"+id,"contact_postal_"+id,"contact_country_"+id,"contact_email_"+id,"contact_phone_number_"+id,"contact_corporation/organization_"+id,"contact_corporation_id_"+id];
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
			}
		};
	xhttp.overrideMimeType('text/xml');
	xhttp.open("POST", "/pyha/createContact/", true);
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
						}
	}

	var complete = [0,0,0];
	
	function refresh(){
	complete = [0,0,0];
	get_taxon_tab();
	get_custom_tab();
	get_summary_tab();
	}
	
	function ready(id){
	complete[id] = 1;
	for (var i = 0; i < complete.length; i++){
			if(complete[i] == 0){
				return;
			}
	allReady();
	}
	}
	
	function allReady() {
		checkForApproval();
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
