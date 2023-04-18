let translations;
let descriptionLength;
let downloadTypes;

const accepted = {};
let acceptedsens = 0;

function setContext(_translations, _descriptionLength, _downloadTypes) {
	translations = _translations;
	descriptionLength = _descriptionLength;
	downloadTypes = _downloadTypes;
}

function checksens() {
	const approvetext = translations["you_accepted_terms"];
	const nonapprovetext = translations["you_have_not_accepted_terms"];

	if (document.getElementById('checkbsens').checked) {
		document.getElementById('statustextsens').textContent = approvetext;
		document.getElementById('checkbsens').disabled = true;
		document.getElementById('to_step_summary').disabled = false;
		acceptedsens = 1;
	} else {
		document.getElementById('statustextsens').textContent = nonapprovetext;
		document.getElementById('to_step_summary').disabled = true;
		acceptedsens = 0;
	}
}

function remove(counter) {
	delete accepted[counter];
	removeAjax(counter, refresh_skip_official);
}

function addContact(current) {
	const newli = document.createElement("li");
	const newa = document.createElement("a");
	const newspan = document.createElement("span");
	const addli = document.getElementById("add_contact_tab");
	const adda = document.getElementById("add_contact_link");
	const remli = document.getElementById("remove_contact_tab");
	const rema = document.getElementById("remove_contact_link");
	const ul = document.getElementById("contact_list");
	newa.className = "request-tab";
	newa.setAttribute("href", "#contact"+current);
	newa.setAttribute("data-toggle", "tab");
	newa.setAttribute("role", "tab");
	newa.id ="contact_tab_button_" + current;
	newspan.textContent = translations["new_contact"];
	newspan.id = "contact_tab_text_" + current;
	newli.id = "contact_tab" + current;
	newli.className = "vertical-li";
	newa.appendChild(newspan);
	newli.appendChild(newa);
	ul.insertBefore(newli, addli);
	create_contact(current);
	rema.setAttribute("href", "javascript:removeContact("+current+")");
	current += 1;
	adda.setAttribute("href", "javascript:addContact("+current+")");
	remli.hidden = false;
}

function removeContact(current) {
	if (current > 1){
		const li = document.getElementById("contact_tab" + current);
		const remli = document.getElementById("remove_contact_tab");
		const rema = document.getElementById("remove_contact_link");
		const adda = document.getElementById("add_contact_link");
		const div = document.getElementById("contact" + current);
		const modaldivs = document.getElementsByName("contact_" + current);
		for (let i = 0; i < modaldivs.length; i = 0) {
			modaldivs[i].parentNode.removeChild(modaldivs[i]);
		}
		const summarytr = document.getElementById("summary_contacts_" + current);
		adda.setAttribute("href", "javascript:addContact("+current+")");
		current -= 1;
		rema.setAttribute("href", "javascript:removeContact("+current+")");
		summarytr.parentNode.removeChild(summarytr);
		div.parentNode.removeChild(div);
		li.parentNode.removeChild(li);
		if(current === 1){
			remli.hidden = true;
		}
	}
	contactsFilled();
	document.getElementById("contact_tab_button_1").click();
}

function updateReason() {
	const select = document.getElementById("reason_selector");
	const result = getSelectValues(select);
	const inputs = ["project", "planning", "municipality", "natura_areas", "research", "research_address", "goals", "customer", "customer_contact", "reason", "customer_check"];

	for (let i=0; i<inputs.length; i++) {
		const argument = "argument_" + inputs[i];
		document.getElementById(inputs[i]).disabled = true;
		document.getElementById(argument).hidden = true;

		const names = document.getElementsByName(argument)
		for (let j=0; j<names.length; j++) {
			names[j].style.display = "none";
		}
	}

	document.getElementById("additional_information").hidden = result.length === 0;
	document.getElementById("request_other_parties").hidden = result.length === 0;
	for (let i=0; i<result.length; i++) {
		let reasoninputs;
		switch (result[i]) {
			case "reason_zoning":
				reasoninputs = ["project", "planning", "municipality", "customer", "customer_contact", "reason", "customer_check"];
				break;
			case "reason_permission":
				reasoninputs = ["project", "planning", "municipality", "customer", "customer_contact", "reason", "customer_check"];
				break;
			case "reason_enviromental":
				reasoninputs = ["project", "planning", "municipality", "customer", "customer_contact", "reason", "customer_check"];
				break;
			case "reason_natura":
				reasoninputs = ["project", "planning", "municipality", "natura_areas", "customer", "customer_contact", "reason", "customer_check"];
				break;
			case "reason_scientific":
				reasoninputs = ["research", "research_address", "goals", "reason"];
				break;
			case "reason_forest":
				reasoninputs = ["project", "planning", "municipality", "customer", "customer_contact", "reason", "customer_check"];
				break;
			case "reason_other":
				reasoninputs = ["municipality", "reason"];
				break;
		}

		for (let j=0; j<reasoninputs.length; j++) {
			const argument = "argument_" + reasoninputs[j];
			document.getElementById(reasoninputs[j]).disabled = false;
			document.getElementById(argument).hidden = false;

			if (reasoninputs[j] === "reason") {
				const elem = document.getElementById("argument_" + reasoninputs[j] + "_label");
				let label = translations["argument_reason"] + " ";
				if (result.indexOf("reason_other") > -1) {
					label = translations["argument_reason_more_detail"] + " * ";
				}
				elem.firstChild.nodeValue = label;
			}

			const names = document.getElementsByName(argument)
			for (let k=0; k<names.length; k++) {
				names[k].style.display = "table-row";
			}
		}
	}

	$('input[name="argument_other_parties"]:hidden').prop("checked", false);
	updateArgumentOtherPartiesFill();

	argumentsFilled();
}

function contactsFilled() {
	let count = 0;
	const fills = ["request_person_name_","request_person_street_address_","request_person_postal_code_","request_person_post_office_name_","request_person_country_","request_person_email_","request_person_phone_number_"];
	while(true){
		count ++;
		if (document.getElementById("request_person_name_"+count) != null){
		}else{
			count --;
			break;
		}
	}
	let state = false;
	for (let i=1; i<=count; i++) {
		for (let j=0; j<fills.length; j++){
			if (document.getElementById(fills[j]+""+i).value == ''){
				state = true;
				break;
			}
		}
		if(state){
			break;
		}
	}
	document.getElementById('to_step_2').disabled = state;
	document.getElementById('send_to_be_accepted').disabled = state;
	const secfills = ["request_person_organization_name_","request_person_corporation_id_"];
	const seccontacts = ["li_contact_corporation/organization_","li_contact_corporation_id_"];
	for (let i=1; i<=count; i++) {
		for (let j=0; j<secfills.length; j++){
			if (document.getElementById(secfills[j]+""+i).value == ''){
				for (k = 0; k < document.getElementsByName(seccontacts[j]+""+i).length; k++){
					document.getElementsByName(seccontacts[j]+""+i)[k].style.display = "none";
				}
			}else{
				for (k = 0; k < document.getElementsByName(seccontacts[j]+""+i).length; k++){
					document.getElementsByName(seccontacts[j]+""+i)[k].style.display = "";
				}
			}
		}
	}
}


function argumentsFilled() {
	const select = document.getElementById('reason_selector');
	const result = getSelectValues(select);
	let fills = [];
	let missingAnswers = false;

	if(result.length > 0) {
		for (let i=0; i<result.length; i++) {
			switch (result[i]) {
				case "reason_zoning":
					fills = fills.concat(['project', 'planning', 'municipality', 'customer', 'customer_contact']);
					break;
				case "reason_permission":
					fills = fills.concat(['project', 'planning', 'municipality', 'customer', 'customer_contact']);
					break;
				case "reason_enviromental":
					fills = fills.concat(['project', 'planning', 'municipality', 'customer', 'customer_contact']);
					break;
				case "reason_natura":
					fills = fills.concat(['project', 'planning', 'municipality', 'natura_areas', 'customer', 'customer_contact']);
					break;
				case "reason_scientific":
					fills = fills.concat(['research', 'research_address', 'goals']);
					break;
				case "reason_forest":
					fills = fills.concat(['project', 'planning', 'municipality', 'customer', 'customer_contact']);
					break;
				case "reason_other":
					fills = fills.concat(['municipality', 'reason']);
					break;
			}
		}
		for (let i=0; i<fills.length; i++){
			if (document.getElementById(fills[i]).value == ''){
				missingAnswers = true;
				break;
			}
		}
	} else {
		missingAnswers = true;
	}

	if (!missingAnswers) {
		const usage = document.getElementById("usage_selector").value;
		missingAnswers = usage === "" || (
			usage === downloadTypes["api_key"] && document.getElementById("expiration_selector").value === ""
		);
	}

	if (!missingAnswers) {
		missingAnswers = !$('input[name="argument_other_parties"]').is(":checked") || (
			$("#other_party_check").is(":checked") && $("#other_party_details").val() === ""
		);
	}

	if (!missingAnswers) {
		document.getElementById("to_step_3").disabled = false;
	} else {
		document.getElementById("to_step_3").disabled = true;
		const $tabs = $('.wizard .nav-tabs li')
		const $summary_tab = $tabs[$tabs.length - 1]
		$summary_tab.className = 'disabled'
	}
}

function getSelectValues(select) {
	const result = [];
	const options = select && select.options;
	let opt;
	for (let i=0; i<options.length; i++) {
		opt = options[i];
		if (opt.selected) {
			result.push(opt.value || opt.text);
		}
	}
	return result;
}

<!-- näytä kuvauksen muokkaus elementti jos kuvauksen pituus on 0 -->
let done = false;
function checkHasDescription(){
	if (descriptionLength === 0 && !done) {
		$("#descriptionEdit").collapse("show");
		done = true;
	}
}

function updateArgumentOtherPartiesFill() {
	const checkedValues = [];
	let otherPartyChecked = false;

	$('input:checkbox[name="argument_other_parties"]:checked').each(function() {
	    const value = $(this).val();
		checkedValues.push(translations[value]);
		if (value === "argument_other_party_check") {
		    otherPartyChecked = true;
		}
	});

	$('[name="argument_other_parties_fill"]').html(checkedValues.join(", "));
    $('tr[name="argument_other_party_details"]').css("display", otherPartyChecked ? "table-row" : "none");
}
