import socket
import pickle
import math
from threading import Thread
from taipy.gui import Gui, State, invoke_callback, get_state_id
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

HOST = "127.0.0.1"
PORT = 65432

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

options = {
    "opacity": 0.8,
    "colorscale": "Bluered",
    "zmin": 0,
    "zmax": 140,
    "colorbar": {"title": "AQI"},
    "hoverinfo": "none",
}

config = {"scrollZoom": False, "displayModeBar": False}


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

data_province_displayed = pd.DataFrame(
    {
        "Latitude": lats,
        "Longitude": longs,
        "Pollution": pollutions,
    }
)

max_pollution = data_province_displayed["Pollution"].max()


# Socket handler
def client_handler(gui: Gui, state_id_list: list):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn, _ = s.accept()
    while True:
        if data := conn.recv(1024 * 1024):
            pollutions = pickle.loads(data)
            print(f"Data received: {pollutions[:5]}")
            if hasattr(gui, "_server") and state_id_list:
                invoke_callback(
                    gui,
                    state_id_list[0],
                    update_pollutions,
                    [pollutions],
                )
        else:
            print("Connection closed")
            break


# Gui declaration
state_id_list = []

Gui.add_shared_variable("pollutions")


def on_init(state: State):
    state_id = get_state_id(state)
    if (state_id := get_state_id(state)) is not None and state_id != "":
        state_id_list.append(state_id)
    update_pollutions(state, pollutions)


def update_pollutions(state: State, val):
    state.pollutions = val
    state.data_province_displayed = pd.DataFrame(
        {
            "Latitude": lats,
            "Longitude": longs,
            "Pollution": state.pollutions,
        }
    )
    # Add an hour to the time
    state.periods = state.periods + 1
    state.max_pollutions = state.max_pollutions + [max(state.pollutions)]
    state.times = pd.date_range(
        "2020-11-04", periods=len(state.max_pollutions), freq="H"
    )
    state.line_data = pd.DataFrame(
        {
            "Time": state.times,
            "Max AQI": state.max_pollutions,
        }
    )


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
gui = Gui(page=page)

t = Thread(
    target=client_handler,
    args=(
        gui,
        state_id_list,
    ),
)
t.start()
gui.run(run_browser=False)
