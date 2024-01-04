window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_slider: function(click, data) {
            console.log("update tools");
            output = [0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];

            if (Object.is(data, null)) {
                console.log("data null");
            } else {
                console.log("data not null");
                df = data["MALA_DF"]["scatter"];
                let x_unique = [];
                for (i = 0; i < df.length; i++) {
                    console.log(df[i]["x"]);
                    x_unique[i] = df[i]["x"];
                }
                console.log(x_unique);



            }
            console.log(output);


            return output;
        }
    }
});