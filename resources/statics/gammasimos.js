var urlParams;
(window.onpopstate = function () {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);

    urlParams = {};
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
})();

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    cache: false,
    crossDomain: false, // Avoid cross-domain forgery
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
        
    }
});

$.fn.hasAttr = function(attributeName) {
    var attribute = $(this).attr(attributeName);
    if (typeof attribute !== typeof undefined && attribute !== false) {
        return true;
    } else {
        return false;
    }
}


$.fn.serializeJSON = function () {
    var result = {};
    var as_array = this.serializeArray();
    $.each(as_array, function () {
        if (result[this.name] !== undefined) {
            if (!result[this.name].push) {
                result[this.name] = [result[this.name]];
            }
            result[this.name].push(this.value || '');
        } else {
            result[this.name] = this.value || '';
        }
    });
    return result;
};

String.prototype.replaceAll = function(search, replace) {
    if (replace === undefined) {
        return this.toString();
    }
    return this.split(search).join(replace);
}

function getPropertyFromString(object, propertyField) {
    var fields = propertyField.split(".");
    while(fields.length && (object = object[fields.shift()]));
    return object;
}