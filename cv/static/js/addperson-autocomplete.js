

$(function() {

   // put all your jQuery goodness in here.
	   
	// Declare available tags for Autocomplete
	var techTags = [
		"ActionScript",
		"AppleScript",
		"Asp",
		"BASIC",
		"C",
		"C++",
		"Clojure",
		"COBOL",
		"ColdFusion",
		"Erlang",
		"Fortran",
		"Groovy",
		"Haskell",
		"Java",
		"JavaScript",
		"Lisp",
		"Perl",
		"PHP",
		"Python",
		"Ruby",
		"Scala",
		"Scheme",
		"Spring", "Hibernate", "Quartz", "OSWorkflow", "ActiveMQ", "Spring MVC", "JSF", "Struts-Tiles", "Acegi-Security", "EHCache", "DbMaintain", "JPox", "Toplink Essentials", "HttpClient", "JodaTime", "SQLite3", "JFreeChart", "Plexus", "XDoclet",
		"TestNG", "Unitils", "JUnit", "JMeter", " Mockito", "EasyMock", "GreenPepper",
		"Confluence", "Jira", "Apache http server", "PostgreSQL", "MySQL", "Oracle", "Tomcat", "Jetty", "MediaWiki", "IntelliJ IDEA", "vim", "LDAP"
	];
	
	function split( val ) {
		return val.split( /,\s*/ );
	}
	function extractLast( term ) {
		return split( term ).pop();
	}
	
	function techAutocomplete() {
		
		$( "#technology_set-group textarea" )
			// don't navigate away from the field on tab when selecting an item
			.bind( "keydown", function( event ) {
				if ( event.keyCode === $.ui.keyCode.TAB &&
						$( this ).data( "autocomplete" ).menu.active ) {
					event.preventDefault();
				}
			})
			.autocomplete({
				minLength: 2,
				source: function( request, response ) {
					// delegate back to autocomplete, but extract the last term
					response( $.ui.autocomplete.filter(
						techTags, extractLast( request.term ) ) );
				},
				focus: function() {
					// prevent value inserted on focus
					return false;
				},
				select: function( event, ui ) {
					var terms = split( this.value );
					// remove the current input
					terms.pop();
					// add the selected item
					terms.push( ui.item.value );
					// add placeholder to get the comma-and-space at the end
					terms.push( "" );
					this.value = terms.join( ", " );
					return false;
				}
			});
	}
	
	$("#technology_set-group").click(function() {
		techAutocomplete();
	});

});
 
	