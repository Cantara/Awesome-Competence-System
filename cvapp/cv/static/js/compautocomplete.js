$(function() {

  var competenceData = [
    {
      "exTitle": "List of technologies or tools you know",
      "description": "List technologies that you use professionally, such as programming languages, tools, methodologies, hardware, etc.",
      "title": "Programming languages",
      "data": "Java, C, .NET, Python, Ruby"
    },
    {
      "exTitle": "Description of a skill or knowledge",
      "description": "Describe how you know a certain skillset, such as Test-driven development, Project management, etc.",
      "title": "Test-driven development",
      "data": "I am well versed in testing and the like, having worked with it for more than 15 years. In 2009 I received the award 'Best Tester'."
    }
  ];

  function compAutocomplete() {
    $( ".field-title input" )
    .autocomplete({
      minLength: 0,
      source: function( request, response ){
        response( competenceData );
      },
      focus: function( event, ui ) {
        return false;
      },
      select: function( event, ui ) {
        var comp = ui.item;
        this.value = comp.title;
        var textareaid = '#'+this.id.replace('-title','')+'-data';
        var $ta = $(textareaid);
        $ta.val( comp.data ); 
        return false;
      }, 
      open: function() { 
        var $this = $(this)
        $this.autocomplete("widget").width( $this.width() );
      },
      create: function() {
        $(this).data('uiAutocomplete')._renderItem = function(ul, item) {
          return $( "<li>" )
            .attr( "data-value", item.title )
            .append( $( "<a>" ).html( 
                '<strong>Example: '+item.exTitle + '</strong><br>' +
                '<i>' + item.description + '</i><br><br>' +
                '<strong>'+item.title + '</strong><br>' + item.data
              ) 
            )
            .appendTo( ul );
        }
      }
    })
    .focus(function(){
      $(this).autocomplete('search', '');
    });
  }

  $("#technology_set-group").click(function() {
    compAutocomplete();
  });

});