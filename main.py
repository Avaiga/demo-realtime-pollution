import math
import time
from taipy import Gui
from taipy.gui import invoke_long_callback
import numpy as np
import pandas as pd

init_lat = 49.247
init_long = 1.377

factory_lat = 49.246
factory_long = 1.369

diff_lat = abs(init_lat - factory_lat) * 15
diff_long = abs(init_long - factory_long) * 15

lats_unique = np.arange(init_lat - diff_lat, init_lat + diff_lat, 0.001)
longs_unique = np.arange(init_long - diff_long, init_long + diff_long, 0.001)

countdown = 20
periods = 0
line_data = pd.DataFrame({"Time": [], "Max AQI": []})

drone_data = pd.DataFrame(
    {
        "Drone ID": [43, 234, 32, 23, 5, 323, 12, 238, 21, 84],
        "Battery Level": [
            "86%",
            "56%",
            "45%",
            "12%",
            "85%",
            "67%",
            "34%",
            "78%",
            "90%",
            "100%",
        ],
        "AQI": [40, 34, 24, 22, 33, 45, 23, 34, 23, 34],
        "Status": [
            "Moving",
            "Measuring",
            "Measuring",
            "Stopped",
            "Measuring",
            "Moving",
            "Moving",
            "Measuring",
            "Measuring",
            "Measuring",
        ],
    }
)


def pollution(lat: float, long: float):
    """
    Return pollution level in percentage
    Pollution should be centered around the factory
    Pollution should decrease with distance to factory
    Pollution should have an added random component

    Args:
        - lat: latitude
        - long: longitude

    Returns:
        - pollution level
    """
    global countdown
    return 80 * (0.5 + 0.5 * math.sin(countdown / 20)) * math.exp(
        -(0.8 * (lat - factory_lat) ** 2 + 0.2 * (long - factory_long) ** 2) / 0.00005
    ) + np.random.randint(0, 50)


layout_map = {
    "mapbox": {
        "style": "open-street-map",
        "center": {"lat": init_lat, "lon": init_long},
        "zoom": 13,
    },
    "dragmode": "false",
    "margin": {"l": 0, "r": 0, "b": 0, "t": 0},
}

layout_line = {
    "title": "Max Measured AQI over Time",
    "yaxis": {"range": [0, 150]},
}

lats = []
longs = []
pollutions = []
times = []
max_pollutions = []

for lat in lats_unique:
    for long in longs_unique:
        lats.append(lat)
        longs.append(long)
        pollutions.append(pollution(lat, long))


def iddle():
    """
    Only call an update every 3 seconds
    """
    global countdown
    while True:
        time.sleep(3)
        countdown += 5


def on_init(state):
    """
    Start the update loop
    """
    invoke_long_callback(state, iddle, [], update, [], 2000)


def update(state):
    """
    Update the pollution levels
    """
    for i in range(len(pollutions)):
        pollutions[i] = pollution(lats[i], longs[i])
    state.data_province_displayed = pd.DataFrame(
        {
            "Latitude": lats,
            "Longitude": longs,
            "Pollution": pollutions,
        }
    )
    state.pollutions = pollutions
    # Add an hour to the time
    state.periods = state.periods + 1
    state.max_pollutions = state.max_pollutions + [max(pollutions)]
    state.times = pd.date_range(
        "2020-11-04", periods=len(state.max_pollutions), freq="H"
    )
    state.line_data = pd.DataFrame(
        {
            "Time": state.times,
            "Max AQI": state.max_pollutions,
        }
    )


data_province_displayed = pd.DataFrame(
    {
        "Latitude": lats,
        "Longitude": longs,
        "Pollution": pollutions,
    }
)

options = {
    "opacity": 0.8,
    "colorscale": "Bluered",
    "zmin": 0,
    "zmax": 140,
    "colorbar": {"title": "AQI"},
    "hoverinfo": "none",
}
config = {"scrollZoom": False, "displayModeBar": False}

max_pollution = data_province_displayed["Pollution"].max()

page = """
<|{data_province_displayed}|chart|type=densitymapbox|plot_config={config}|options={options}|lat=Latitude|lon=Longitude|layout={layout_map}|z=Pollution|mode=markers|class_name=map|height=40vh|>
<|layout|columns=1 2 2|
<|part|class_name=card|
**Max Measured AQI:**<br/><br/><br/>
<|{int(data_province_displayed["Pollution"].max())}|indicator|value={int(data_province_displayed["Pollution"].max())}|min=140|max=0|>
<br/><br/>
**Average Measured AQI:**<br/><br/><br/>
<|{int(data_province_displayed["Pollution"].mean())}|indicator|value={int(data_province_displayed["Pollution"].mean())}|min=140|max=0|>
|>

<|part|class_name=card|
<|{drone_data}|table|show_all=True|>
|>

<|part|class_name=card|
<|{line_data[-30:]}|chart|type=lines|x=Time|y=Max AQI|layout={layout_line}|height=40vh|>
|>
|>
"""

Gui(page).run(use_reloader=True)
