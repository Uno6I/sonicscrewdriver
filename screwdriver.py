import asyncio
from kasa import SmartPlug, SmartDeviceException
import tkinter as tk
from pygame import mixer

# Replace these file paths with your sound files
START_SOUND = "sonicendofbegin.mp3"  # Start sound
LOOP_SOUND = "sonic.mp3"  # Loop sound
STOP_SOUND = "sonicendofbegin.mp3"  # Stop sound
BELL_SOUND = "bell.mp3"  # Bypass screen sound

# Initialize mixer for sounds
mixer.init()

# Define global variables
plug_ip = None
plug_state = None  # Keep track of plug state (on or off)
is_playing_loop = False  # To track if loop sound is playing
bypass_mode = False  # Track if we're in bypass mode

async def toggle_plug():
    global plug_state
    try:
        plug = SmartPlug(plug_ip)
        await plug.update()  # Attempt to update plug state
        if plug.is_on:
            await plug.turn_off()
            plug_state = False
            print("Plug turned off")
        else:
            await plug.turn_on()
            plug_state = True
            print("Plug turned on")
    except SmartDeviceException:
        print("Failed to connect to plug; entering bypass mode.")
        enter_bypass_screen()  # Trigger bypass if connection fails

def play_sound(sound_file, loop=False):
    mixer.music.load(sound_file)
    if loop:
        mixer.music.play(-1)  # Play in loop (-1 means infinite loop)
    else:
        mixer.music.play()

def stop_sound():
    mixer.music.stop()

def start_action(event=None):
    global is_playing_loop
    if not is_playing_loop:
        root.after(250, begin_action)  # Add a 0.25-second buffer before starting the action

def begin_action():
    global is_playing_loop
    canvas.config(bg="green")  # Make the screen green
    play_sound(START_SOUND)  # Play the start sound (sonicendofbegin.mp3)
    root.after(75, lambda: play_sound(LOOP_SOUND, loop=True))  # Start looping the sound after 75 milliseconds
    is_playing_loop = True

def stop_action(event=None):
    global is_playing_loop
    if is_playing_loop:
        stop_sound()  # Stop looping sound
        play_sound(STOP_SOUND)  # Play stop sound (sonicendofbegin.mp3)
        canvas.config(bg="black")  # Reset screen to black
        asyncio.run(toggle_plug())  # Try toggling the plug; if it fails, enter bypass mode
        is_playing_loop = False

def submit_ip(event=None):
    global plug_ip, bypass_mode
    plug_ip = entry.get()
    
    if plug_ip == "bypass":
        bypass_mode = True
        entry.destroy()
        label.destroy()
        create_bypass_screen()
    elif plug_ip:
        # Clear the initial window and move to the action screen
        entry.destroy()
        label.destroy()
        create_action_screen()

def create_bypass_screen():
    global canvas, bypass_mode
    # Configure the canvas for full-screen red flashing effect
    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    bypass_mode = True  # Activate bypass mode
    root.bind("<Triple-Button-1>", return_to_ip_chooser)  # Bind triple-click to return to IP chooser screen
    start_bypass_loop()

def start_bypass_loop():
    if bypass_mode:
        # Flash red and play bell sound
        canvas.config(bg="red")
        play_sound(BELL_SOUND)
        root.after(1000, reset_bypass_flash)  # Flash red for 1 second

def reset_bypass_flash():
    if bypass_mode:
        # Reset to black
        canvas.config(bg="black")
        root.after(1500, start_bypass_loop)  # Wait 1.5 more seconds, then repeat flash and sound every 2.5 seconds

def create_action_screen():
    global canvas
    # Configure the canvas for full-screen green effect
    canvas = tk.Canvas(root, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Bind mouse click and spacebar to start/stop the action
    root.bind("<ButtonPress-1>", start_action)
    root.bind("<ButtonRelease-1>", stop_action)
    root.bind("<space>", start_action)
    root.bind("<KeyRelease-space>", stop_action)

    # Bind double click and double tap on spacebar to return to IP chooser
    root.bind("<Double-Button-1>", return_to_ip_chooser)  # Mouse double-click
    root.bind("<Double-Press-space>", return_to_ip_chooser)  # Spacebar double-tap

def enter_bypass_screen():
    global bypass_mode
    bypass_mode = True
    stop_sound()  # Stop any current sounds
    canvas.destroy()  # Destroy current screen
    create_bypass_screen()  # Enter bypass mode with flashing red screen and bell sound

def return_to_ip_chooser(event=None):
    global plug_ip, bypass_mode
    plug_ip = None
    bypass_mode = False  # Exit bypass mode
    stop_sound()  # Stop any sounds playing
    
    # Destroy any existing canvases or widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create the IP chooser screen again
    create_ip_chooser_screen()

def create_ip_chooser_screen():
    global label, entry
    # Reinitialize the entry field for IP input
    label = tk.Label(root, text="Enter the Internet Protocol Address", font=('Consolas', 24), bg="black", fg="white")
    label.pack(pady=20)

    entry = tk.Entry(root, font=('Consolas', 24), bg="black", fg="white", insertbackground="white")
    entry.pack(padx=10, pady=20, expand=True, fill='both')
    entry.focus()  # Set focus to the entry field
    entry.bind('<Return>', submit_ip)  # Bind Enter key to submit_ip function

# Set up initial GUI
root = tk.Tk()
root.title("Sonic Screwdriver")
root.configure(bg="black")
root.attributes('-fullscreen', False)  # Makes it look like a console/command prompt

# Create the initial IP chooser screen
create_ip_chooser_screen()

root.mainloop()
