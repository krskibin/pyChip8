import os.path
import platform
import tkinter as tk
import tkinter.messagebox as msg_box
import tkinter.filedialog as filedialog

# I/O default variables
DEFAULT_RESOLUTION: str = "640x320"
DEFAULT_SCALE: int = 10
DEFAULT_FREQUENCY: int = 1

KEYMAP = {
    '1': 1, '2': 2, '3': 3, '4': 12,
    'q': 4, 'w': 5, 'e': 6, 'r': 13,
    'a': 7, 's': 8, 'd': 9, 'f': 14,
    'z': 10, 'x': 0, 'c': 11, 'v': 15,
}

# Screen variables
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 320

BLACK_COLOR: str = 'black'
WHITE_COLOR: str = 'white'

BUFFER_WIDTH: int = 64
BUFFER_HEIGHT: int = 32
VERSION: str = "0.5.0"

# Setup configuration
DEFAULT_ROM_PATH: str = 'roms/.'


class Window(tk.Tk):

    def __init__(self):
        super().__init__()

        self.file_name = None
        self.proc = None
        self.res = None

        self.is_sound = tk.IntVar()
        self.is_sound.set(1)

    def config_window(self):
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.createcommand('tkAboutDialog', self.__about)
        self.createcommand('exit', self.quit)

    def set_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file_window)
        file_menu.add_separator()
        file_menu.add_command(label="Reset", command=self.reset_emulator)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        option_menu = tk.Menu(menubar, tearoff=0)
        resolution_menu = tk.Menu(option_menu, tearoff=0)

        resolution_menu.add_command(label="64x32", command=self.change_resolution("64x32"))
        resolution_menu.add_command(label="640x320", command=self.change_resolution("640x320"))
        resolution_menu.add_command(label="1080x640", command=self.change_resolution("1280x640"))

        option_menu.add_cascade(label="Screen size", menu=resolution_menu)
        option_menu.add_checkbutton(label='Sound', variable=self.is_sound, command=self.turn_sound)

        menubar.add_cascade(label="Options", menu=option_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="PyChip8 Help", command=self.__informations)
        help_menu.add_separator()
        help_menu.add_command(label="What's new", command=self.__informations)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def turn_sound(self, *args):
        return

    def change_resolution(self, resolution):
        that = self

        def wrapper(res=resolution):
            that.res = res

        return wrapper

    def reset_emulator(self):
        self.proc.reset()

    def open_file_window(self):
        system = platform.system()
        file_types = [('All files', '*'), ('CHIP-8 binary files ', '.c8 .c8h .ch8')]

        if system == 'Darwin':
            filepath = filedialog.askopenfilename(initialdir="../roms/.")
        elif system == 'Linux':
            filepath = filedialog.askopenfilename(initialdir="../roms/.", filetypes=file_types)
        else:
            filepath = filedialog.askopenfilename(filetypes=file_types)

        if filepath:
            extension = os.path.splitext(filepath)[1]

            if extension not in ['', '.c8', '.ch8', 'c8h']:
                msg_box.showerror(message="Cannot read file!")
                return

            self.file_name = filepath
            self.proc.memory_controller.clean_ram()
            self.proc.memory_controller.load_rom(filepath)
            self.proc.memory = self.proc.memory_controller.ram
            self.proc.reset()
        else:
            self.no_file()

    def quit(self):
        self.destroy()

    @staticmethod
    def __about():
        message = f"""
            Python CHIP-8 Emulator
            version: {VERSION}\n
            for more information visit:
            github.com/krskibin/pychip8
        """
        msg_box.showinfo(message=message)

    @staticmethod
    def __informations():
        message = """
        More informations can be found at:\n
        https://github.com/krskibin/pyChip8
        """
        msg_box.showinfo(message=message)

    @staticmethod
    def no_file():
        message = "no ROM file, please select one using file dialog 'file> open'"
        msg_box.showinfo(message=message)

    def sound_warming(self):
        message = "To play sound, install simplesound package."
        msg_box.showinfo(message=message)


class Screen:

    def __init__(self):
        self.proc = None
        self.canvas = None
        self.window = Window()

        self.res = DEFAULT_RESOLUTION
        self.height = SCREEN_HEIGHT
        self.width = SCREEN_WIDTH
        self.scale = DEFAULT_SCALE

        self.sound_obj = None

        self.window.bind("<KeyPress>", self.key_down)
        self.window.bind("<KeyRelease>", self.key_up)

    def calculate_resolution(self, res):
        res_list = res.split('x')
        if len(res_list) != 2:
            msg_box.showerror(message="Unsupported resolution")
            return
        else:
            self.res = res
            self.width = int(res_list[0])
            self.height = int(res_list[1])
            self.scale = self.width/BUFFER_WIDTH if self.width > BUFFER_WIDTH else DEFAULT_SCALE

    def init_display(self, proc, res=DEFAULT_RESOLUTION):
        self.calculate_resolution(res)
        self.window.geometry(self.res)
        self.window.resizable()
        self.window.proc = proc
        self.proc = proc
        self.window.config_window()
        self.window.set_menu()
        self.window.title("Chip 8 emulator")
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, borderwidth=0, highlightthickness=0,
                                background="black", xscrollincrement=1, yscrollincrement=1)

        self.canvas.pack()
        self.configure_sound()
        if not self.sound_obj:
            system = platform.system()
            if system != "Darwin":
                self.window.sound_warming()

    def key_down(self, key):
        self.proc.key_pressed = KEYMAP.get(key.keysym, 0)

    def key_up(self, *args):
        self.proc.key_pressed = 15

    def draw_pixel(self):
        if self.proc.refresh_screen:
            self.clear()
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill=BLACK_COLOR)

            for y in range(BUFFER_HEIGHT):
                y_coord = self.scale * (y % self.height)

                for x in range(BUFFER_WIDTH):
                    x_coord = self.scale * (x % self.width)

                    if self.proc.buffer[y][x] == 1:
                        self.canvas.create_rectangle(x_coord, y_coord, x_coord + self.scale,
                                                     y_coord + self.scale, fill=WHITE_COLOR,
                                                     outline=WHITE_COLOR)
            self.proc.refresh_screen = False
        self.canvas.update()

    def configure_sound(self):
        try:
            import simpleaudio
            self.sound_obj = simpleaudio.WaveObject.from_wave_file("beep.wav")
        except:
            self.sound_obj = False

    def play_sound(self):
        if self.sound_obj:
            if self.proc.timers['sound'] > 0:
                self.sound_obj.play()

    def clear(self):
        self.canvas.delete("all")
