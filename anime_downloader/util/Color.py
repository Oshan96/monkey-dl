class Color:
    BLACK = lambda x: '\u001b[30m' + str(x)
    RED = lambda x: '\u001b[91m' + str(x)
    GREEN = lambda x: '\u001b[92m' + str(x)
    YELLOW = lambda x: '\u001b[93m' + str(x)
    BLUE = lambda x: '\u001b[94m' + str(x)
    MAGENTA = lambda x: '\u001b[95m' + str(x)
    CYAN = lambda x: '\u001b[96m' + str(x)
    WHITE = lambda x: '\u001b[37m' + str(x)
    UNDERLINE = lambda x: '\u001b[4m' + str(x)
    RESET = lambda x: '\u001b[0m' + str(x)


def printer(msg_type, msg, gui=None):
    if gui:
        gui.gui_queue.put("[" + msg_type + "] : " + str(msg))

    if msg_type == "INFO":
        print(Color.YELLOW("[INFO!] : " + msg) + Color.RESET(" "))
    elif msg_type == "ERROR":
        print(Color.RED("[ERROR!] : " + str(msg)) + Color.RESET(" "))
    elif msg_type == "BANNER":
        print(Color.CYAN(msg) + Color.RESET(" "))
