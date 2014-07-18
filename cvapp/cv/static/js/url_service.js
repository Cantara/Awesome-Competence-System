AcsApp.service('Url', function(){

  this.getParams = function() {
    var vars = {};
    if(location.href.indexOf('?')>-1) {
      var hash;
      var hashes = location.href.slice(location.href.indexOf('?') + 1).split('&');
      for(var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        var key = decodeURIComponent(hash[0]);
        var value = decodeURIComponent(hash[1]);
        if( vars[hash[0]] ) {
          vars[key].push(value);
        } else {
          vars[key] = [value];
        }
      }
    }
    return vars;
  }

  this.setParams = function(newParams) {
    // Update Window Location
    if( window.history.replaceState && newParams ) {
      var l = window.location;
      var newurl = l.protocol + '//' + l.host + l.pathname + "?" + newParams;
      window.history.pushState({}, "title", newurl);
    }
  }

});