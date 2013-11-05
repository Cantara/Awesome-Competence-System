$(function() {

  function expAutocomplete() {
    $( ".field-company input" ).autocomplete({
      minLength: 3,
      source: '/cv/expautocomplete/',
      focus: function( event, ui ) {
        return false;
      },
      select: function( event, ui ) {
        var exp = ui.item.fields;
        this.value = exp.company;
        var textareaid = '#'+this.id.replace('-company','')+'-description';
        var $ta = $(textareaid);
        var co = confirm('Do you want to replace your current description with ' + exp.person[0] + '\'s description?\n\nYour current description:\n"' + $ta.val() + '"\n\n' + exp.person[0] + '\'s description:\n"'+exp.description+'"');
        if(co){
          $ta.val( exp.description ); 
        }
        return false;
      }, 
      open: function() { 
        var $this = $(this)
        $this.autocomplete("widget").width( $this.width() );
      },
      create: function() {
        $(this).data('uiAutocomplete')._renderItem = function(ul, item) {
          return $( "<li>" )
            .attr( "data-value", item.fields.company )
            .append( $( "<a>" ).html( item.fields.company + '<br>' + item.fields.description) )
            .appendTo( ul );
        }
      }
    });
  }

  $("#experience_set-group").click(function() {
    expAutocomplete();
  });

});