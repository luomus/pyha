	  var accepted = {};
	  var acceptedsens = 0;
	  function checksens() { 
		  approvetext = "{% trans 'you_accepted_terms' %}";
		  nonapprovetext = "{% trans 'you_have_not_accepted_terms' %}";
		  if(document.getElementById('checkbsens').checked){
			  document.getElementById('statustextsens').textContent=approvetext;
			  document.getElementById('checkbsens').disabled = true;
			  document.getElementById('to_step_4').disabled = false;
			  acceptedsens = 1;
		  }else{
			  document.getElementById('statustextsens').textContent=nonapprovetext;
			  document.getElementById('to_step_4').disabled = true;
			  acceptedsens = 0;
		}
	  }
	  function check(counter) { 
		  approvetext = "{% trans 'you_accepted_terms' %}";
		  nonapprovetext = "{% trans 'you_have_not_accepted_terms' %}";
		  if(document.getElementById(counter).checked){
			  document.getElementById('statustext'+ counter).textContent=approvetext;
			  document.getElementById(counter).disabled = true;
			  accepted[counter] = 1;
		  }else{
			  document.getElementById('statustext'+ counter).textContent=nonapprovetext;
			  accepted[counter] = 0;
		}
	  }
	  function remove(counter) { 
		delete accepted[counter];
		removeAjax(counter);
	  }
	  function refreshCheck() {
		var elements = document.getElementsByName("checkb");
		for(var i=0; i<elements.length; i++) {
	      check(elements[i].id);
	    }
	  }
	  function checkv(counter, value) { 
		  accepted[counter] = value;
	  }
	  function checkForApproval(){
		var approved = 0;
		var size = 0;
		for (i in accepted){
		approved += accepted[i];
		size += 1;
		}
		approved += acceptedsens;
		if(approved == size+1){
			document.getElementById('to_step_summary').disabled = false;
			document.getElementById('submit').disabled = false;
			document.getElementById('submitstatustext').hidden = true;
			document.getElementById('collections_not_approved').hidden = true;
		}else{
			document.getElementById('to_step_summary').disabled = true;
			document.getElementById('submit').disabled = true;
			document.getElementById('submitstatustext').hidden = false;
			document.getElementById('collections_not_approved').hidden = false;
		}
	}
	
	function addContact(current) {
	var newli = document.createElement("li");
	var newa = document.createElement("a");
	var newspan = document.createElement("span");
	newa.className = "vertical-tab";
	newspan.textContent = "{% trans 'new_contact' %}";
	newa.appendChild(newspan);
	newli.appendChild(newa);
	var currentli = document.getElementById(current)
	insertAfter(newli, currentli);
	}
	
	function insertAfter(newNode, referenceNode) {
	referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
	}
	
	function updateReason() { 
	var select = document.getElementById('reason_selector');
	var result = getSelectValues(select)
	document.getElementById('argument_reason').hidden = true;
	document.getElementById('argument_municipality').hidden = true;
	document.getElementById('argument_natura_areas').hidden = true;
	document.getElementById('argument_project').hidden = true;
	document.getElementById('argument_research').hidden = true;
	document.getElementById('argument_goals').hidden = true;
	document.getElementById('argument_planning').hidden = true;
	document.getElementById('reason').disabled = true;
	document.getElementById('municipality').disabled = true;
	document.getElementById('natura_areas').disabled = true;
	document.getElementById('project').disabled = true;
	document.getElementById('research').disabled = true;
	document.getElementById('goals').disabled = true;
	document.getElementById('planning').disabled = true;
	document.getElementById('additional_information').hidden = result.length == 0;
	for (var i=0; i<result.length; i++) {
		switch (result[i]) {
			case "reason_zoning":
				document.getElementById('argument_project').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('project').disabled = false;
				document.getElementById('municipality').disabled = false;
				break;
			case "reason_permission":
				document.getElementById('argument_project').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('project').disabled = false;
				document.getElementById('municipality').disabled = false;
				break;
			case "reason_enviromental":
				document.getElementById('argument_project').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('project').disabled = false;
				document.getElementById('municipality').disabled = false;
				break;
			case "reason_natura":
				document.getElementById('argument_project').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('argument_natura_areas').hidden = false;
				document.getElementById('project').disabled = false;
				document.getElementById('municipality').disabled = false;
				document.getElementById('natura_areas').disabled = false;
				break;
			case "reason_scientific":
				document.getElementById('argument_research').hidden = false;
				document.getElementById('argument_goals').hidden = false;
				document.getElementById('research').disabled = false;
				document.getElementById('goals').disabled = false;
				break;
			case "reason_forest":
				document.getElementById('argument_planning').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('planning').disabled = false;
				document.getElementById('municipality').disabled = false;
				break;
			case "reason_other":
				document.getElementById('argument_reason').hidden = false;
				document.getElementById('argument_municipality').hidden = false;
				document.getElementById('reason').disabled = false;
				document.getElementById('municipality').disabled = false;
		} 
	}
	if (result.length > 0) {
		document.getElementById("to_step_3").disabled = false;      
		 
	} else {
		document.getElementById("to_step_3").disabled = true;         
		var $tabs = $('.wizard .nav-tabs li')
		var $summary_tab = $tabs[$tabs.length - 1]
		$summary_tab.className = 'disabled'
		}
	}
	
	function getSelectValues(select) {
	var result = [];
	var options = select && select.options;
	var opt;

	for (var i=0; i<options.length; i++) {
	opt = options[i];

	if (opt.selected) {
	  result.push(opt.value || opt.text);
	}
	}
	return result;
	}
