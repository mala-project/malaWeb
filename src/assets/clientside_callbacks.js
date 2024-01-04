window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        ext_function: function(val1) {
        console.log(val1);
        return "jup"
        }
    }
});