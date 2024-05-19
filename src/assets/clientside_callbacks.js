window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        slider_x_func: function (slider_val, data) {
            let low = slider_val[0];
            let high = slider_val[1];
            x_array = [];
            y_array = [];
            z_array = [];
            val_array = [];

            filtered_data = data.filter(d => d["x"] < low)
            console.log(filtered_data)
            filtered_data.forEach((arr)=>{x_array.push(arr["x"])});

            filtered_data.forEach((arr)=>{y_array.push(arr["y"])});
            filtered_data.forEach((arr)=>{z_array.push(arr["z"])});
            filtered_data.forEach((arr)=>{val_array.push(arr["val"])});

            return {
                'data': [{
                    x: x_array,
                    y: y_array,
                    z: z_array,
                    mode: "markers",
                    type: 'scatter3d',
                    marker: [{
                        color: val_array,
                        coloraxis: 'coloraxis',
                        symbol: 'circle'
                    }]
                }],
                'layout': {'coloraxis': {'colorbar': {'title': {'text': 'color'}},
                        'colorscale': [[0.0, '#0d0887'], [0.1111111111111111,
                            '#46039f'], [0.2222222222222222,
                            '#7201a8'], [0.3333333333333333,
                            '#9c179e'], [0.4444444444444444,
                            '#bd3786'], [0.5555555555555556,
                            '#d8576b'], [0.6666666666666666,
                            '#ed7953'], [0.7777777777777778,
                            '#fb9f3a'], [0.8888888888888888,
                            '#fdca26'], [1.0, '#f0f921']]},
                    'legend': {'tracegroupgap': 0},
                    'margin': {'t': 60},
                    'scene': {'domain': {'x': [0.0, 1.0], 'y': [0.0, 1.0]},
                        'xaxis': {'title': {'text': 'x'}},
                        'yaxis': {'title': {'text': 'y'}},
                        'zaxis': {'title': {'text': 'z'}}},
                    'template': '...'}
            }
        }
    }
});
