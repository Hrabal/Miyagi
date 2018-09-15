// Main Miyagi js, included in every page.
// Provides the method to bind page-specific code to the DOM:
// define a function with custom code and call bindMiyagi on it:
// bindMiyagi('POST', function() {  <- use bindMiyagi  instead of document ready
//         ...code...
// });
// Base ready function, Miyagi loads here all the useful stuff
readyFn = function() { };
var fnc_list = [readyFn, ]
bindMiyagi = function(when, fnc) {
    if (when == 'PRE') { fnc_list.unshift(fnc) } else { fnc_list.push(fnc) }
};

$( document ).ready( function() {
    // Call tall the added functions
    fnc_list.forEach(Function.prototype.call, Function.prototype.call);
});
