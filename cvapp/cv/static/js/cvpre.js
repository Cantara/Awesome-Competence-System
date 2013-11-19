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
		handle: '.draghandle',
		axis: 'y'
	})
	.disableSelection()
	.children().each(function() {
		$(this).append('<div class="draghandle"></div>');
	});
	
	// Delete an item (delete the parent)
	$(".toggle").click( function(){
		if(confirm("Are you sure you want to hide this?")) $(this).parent().remove();
	});
	
	 function makeExpandingArea(container) {
		 var area = container.querySelector('textarea');
		 var span = container.querySelector('span');
		 if (area.addEventListener) {
		   area.addEventListener('input', function() {
			 span.textContent = area.value;
		   }, false);
		   span.textContent = area.value;
	 } else if (area.attachEvent) {
	   // IE8 compatibility
	   area.attachEvent('onpropertychange', function() {
		 span.innerText = area.value;
	   });
	   span.innerText = area.value;
	 }
	 // Enable extra CSS
	 container.className += ' active';
	}

	var areas = document.querySelectorAll('.expandingArea');
	var l = areas.length;

	while (l--) {
	 makeExpandingArea(areas[l]);
	}
	
});