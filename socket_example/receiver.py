import socket
from threading import Thread
from taipy.gui import Gui, State, invoke_callback, get_state_id

HOST = "127.0.0.1"
PORT = 65432

# Socket handler
def client_handler(gui: Gui, state_id_list: list):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    while True:
        if data := conn.recv(1024):
            print("Data received: ", data.decode())
            if hasattr(gui, "_server") and state_id_list:
                invoke_callback(gui, state_id_list[0], update_case_count, (int(data.decode()),))
        else:
            print("Connection closed")
            break


# Gui declaration
state_id_list = []

Gui.add_shared_variable("case_count")

def on_init(state: State):
    state_id = get_state_id(state)
    if (state_id := get_state_id(state)) is not None and state_id != "":
        state_id_list.append(state_id)

def update_case_count(state: State, val):
    state.case_count = val
    # state.broadcast("case_count", val)


case_count = 0

md = """
# Covid Tracker

Number of cases: <|{case_count}|>
"""
gui = Gui(page=md)

t = Thread(
    target=client_handler,
    args=(
        gui,
        state_id_list,
    ),
)
t.start()
gui.run(run_browser=False)
