$(document).ready(function() {
	$("#filterlist").on("hide.bs.collapse", function(){
		$("#filterbutton").html(translations["show"]);
	});
	$("#filterlist").on("show.bs.collapse", function(){
		$("#filterbutton").html(translations["hide"]);
	});

	let fields = ["request_person_name_1","request_person_street_address_1","request_person_postal_code_1","request_person_post_office_name_1","request_person_country_1","request_person_email_1","request_person_phone_number_1","request_person_organization_name_1","request_person_corporation_id_1"];
	const fills = ["contact_name_1","contact_street_address_1","contact_postal_1","contact_post_office_1","contact_country_1","contact_email_1","contact_phone_number_1","contact_corporation/organization_1","contact_corporation_id_1"];
	for (let i = 0; i < fields.length; i++){
		const namefield = document.getElementById(fields[i]);
		const fillfield = document.getElementsByName(fills[i]);
		if (i === 0){
			namefield.onkeyup = updateTabField(namefield, fillfield, 1);
			namefield.onchange = updateTabField(namefield, fillfield, 1);
			updateTabField(namefield, fillfield, 1)();
		}else{
			namefield.onkeyup = updateField(namefield, fillfield);
			namefield.onchange = updateField(namefield, fillfield);
			updateField(namefield, fillfield)();
		}
	}
	fields = ['project', 'planning', 'municipality', 'natura_areas', 'research', 'research_address', 'goals', 'customer', 'customer_contact', 'reason', 'other_party_details'];
	for (let i = 0; i < fields.length; i++){
		const namefield = document.getElementById(fields[i]);
		const fillfield = document.getElementsByName('argument_' + fields[i] + '_fill');

		namefield.onkeyup = updateArgumentField(namefield, fillfield);
		namefield.onchange = updateArgumentField(namefield, fillfield);
		updateArgumentField(namefield, fillfield)();
	}

	$(document).on('click','.deleteContainer',function(e){
		const name ="#delete" + $(this).find('.removeCollectionButton').attr('id');
		e.preventDefault();
		$('#confirm-modal').off()
		$('#confirm-modal').modal({backdrop: 'static', keyboard: false})
			.one('click', '#delete', function(){
				$(name).submit();
			});

	});
	$(document).on('click','.sensDeleteContainer',function(e){
		const name = "#deletesens" + $(this).find('.removeSensitiveButton').attr('id');
		e.preventDefault();
		$('#confirm-modal').off()
		$('#confirm-modal').modal({backdrop: 'static', keyboard: false})
			.one('click', '#delete', function(){
				$(name).submit();
			});

	});
	$(document).on('click','.customDeleteContainer',function(e){
		const name = "#deletecustom" + $(this).find('.removeCustomButton').attr('id');
		e.preventDefault();
		$('#confirm-modal').off()
		$('#confirm-modal').modal({backdrop: 'static', keyboard: false})
			.one('click', '#delete', function(){
				$(name).submit();
			});
	});
	$("form").submit(function() {
		$("input").removeAttr("disabled");
	});

	$('#reason_selector').multiselect({
		nonSelectedText: translations["request_choose_reason"],
		nSelectedText: translations["request_chosen_multiple_reasons"],
		allSelectedText: translations["request_chosen_all_reasons"],
		onChange: function(option, checked, select) {
			this.$button.click();
		}

	});

	$('#usage_selector').val('').multiselect({
		nonSelectedText: translations["usage_choose"],
		onChange: function(option, checked, select) {
			const apiKeySelected = document.getElementById("usage_selector").value === downloadTypes["api_key"];
			document.getElementById("expiration_section").style.display = apiKeySelected ? "" : "none";
			argumentsFilled();
		}
	});

	$('#expiration_selector').val('').multiselect({
		nonSelectedText: translations["expiration_choose"],
		onChange: function(option, checked, select) {
			argumentsFilled();
		}
	});

	$('input[name="argument_other_parties"]').change(function () {
		const id = $(this).attr("id");
		const isChecked = $(this).is(":checked");

		if (isChecked) {
			if (id === "only_requester_check") {
				$("#customer_check").prop("checked", false);
				$("#other_party_check").prop("checked", false);
			} else {
				$("#only_requester_check").prop("checked", false);
			}
		}

		updateArgumentOtherPartiesFill();
		argumentsFilled();
	});

	refresh_skip_official();
	get_request_header();
	updateReason();
	updateArgumentOtherPartiesFill();
	contactsFilled();
	argumentsFilled();
});
