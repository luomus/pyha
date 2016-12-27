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
	xhttp.open("POST", "/pyha/description/", true);
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
			document.getElementById("summarytable").innerHTML = this.responseText;
			}
		};
	xhttp.open("POST", "/pyha/getSummary/", true);
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
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
	
	function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i];
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');
