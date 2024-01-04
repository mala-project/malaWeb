
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_slider: function(click, data) {
            console.log("update tools");
            let output = [0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];

            if (Object.is(data, null)) {
                console.log("data null");
            } else {
                console.log("data not null");




            }


            return output;
        }
    }
});