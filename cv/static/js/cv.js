//Binding functions and making things sortable/draggable - Some are here, some are in the buttons or whatever, I'm not that consistent
$(function() {
	$( "#technologies" ).sortable({
		forcePlaceholderSize: true,
		placeholder: 'dragplaceholder',
		axis: 'y'
	}).disableSelection();
	$( ".sortwithin" ).sortable({
		forcePlaceholderSize: true,
		placeholder: 'dragplaceholder',
		axis: 'y'
	}).disableSelection();
	// Delete an item (delete the parent)
	$(".toggle").click( function(){
		if(confirm("Er du sikker på at du vil slette?")) $(this).parent().remove();
	});
});