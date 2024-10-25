import asyncio
from kasa import SmartPlug
import tkinter as tk
from pygame import mixer

# Replace these file paths with your sound files
START_SOUND = "sonicendofbegin.mp3"  # Start sound
LOOP_SOUND = "sonic.mp3"  # Loop sound
STOP_SOUND = "sonicendofbegin.mp3"  # Stop sound

# Initialize mixer for sounds
mixer.init()

# Define global variables
plug_ip = None
plug_state = None  # Keep track of plug state (on or off)
is_playing_loop = False  # To track if loop sound is playing

async def toggle_plug():
    global plug_state
    plug = SmartPlug(plug_ip)
    await plug.update()  # Update the plug state
    if plug.is_on:
        await plug.turn_off()
        plug_state = False
        print("Plug turned off")
    else:
        await plug.turn_on()
        plug_state = True
        print("Plug turned on")

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
        asyncio.run(toggle_plug())  # Toggle the plug when action ends
        is_playing_loop = False

def submit_ip(event=None):
    global plug_ip
    plug_ip = entry.get()
    
    if plug_ip:
        # Clear the initial window and move to the action screen
        entry.destroy()
        label.destroy()
        create_action_screen()

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

def return_to_ip_chooser(event=None):
    global plug_ip
    plug_ip = None
    # Clear the action screen
    canvas.destroy()  # Destroy the current canvas
    create_ip_chooser_screen()  # Create the IP chooser screen

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
root.title("Kasa Plug Console")
root.configure(bg="black")
root.attributes('-fullscreen', True)  # Makes it look like a console/command prompt

# Create the initial IP chooser screen
create_ip_chooser_screen()

root.mainloop()
