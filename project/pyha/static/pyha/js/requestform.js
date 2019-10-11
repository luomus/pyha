	  var accepted = {};
		var acceptedsens = 0;

	  function remove(counter) {
			delete accepted[counter];
			removeAjax(counter);
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
