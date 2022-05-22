import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import os
import pygame
import json
from PIL import Image, ImageTk
from mutagen.id3 import ID3
from io import BytesIO


folder_path = ""
lists = {}
playing = False
paused = False
active_song = ""
active_list = ""

def add_song_to_json(folder_path, song_names):
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"):
        os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)
    else:
        lists_dict = {}
    song_and_path = [[]]
    
    lists_dict.update({"All Songs" : folder_path:song_names})
    os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
    with open("song_lists.json", "w") as write_file:
        json.dump(songs_dict, write_file)

def get_songnames():
    global folder_path
    music_ex = ['mp3','wav','mpeg','m4a','wma','ogg']
    song_names = []
    
    folder_path = fd.askdirectory(title="Select The Song Folder")
    os.chdir(folder_path)
    # foldername = os.getcwd().split("\\")[-1]
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        if file_name.split(".")[-1] in music_ex:
            song_names.append(file_name)
    
    add_song_to_json(folder_path, song_names)

    return song_names

def add_folder():
    global lists, lists_listbox, songs_listbox, active_song, active_list
    songs = get_songnames()
    lists["All Songs"] = songs
    active_list = "All Songs"
    active_song = songs[0]

    lists_listbox.delete(0, tk.END)
    songs_listbox.delete(0, tk.END)

    for key in lists.keys():
        lists_listbox.insert(tk.END, key)
        for song in lists[key]:
            songs_listbox.insert(tk.END, song)

def play_pause():
    global songs_listbox, playing, paused, folder_path, play_pause_button
    global play_image, pause_image, active_song, status_bar
    if playing: 
        paused = True
        playing = False
        play_pause_button.configure(image=play_image)
        pygame.mixer.music.pause()

    else:
        if paused:
            paused = False
            playing = True
            play_pause_button.configure(image=pause_image)
            pygame.mixer.music.unpause()
        else:
            song_name = songs_listbox.get(0)
            pygame.mixer.music.load(folder_path + "/" + song_name)
            paused = False
            playing = True
            active_song = song_name
            status_bar.configure(text=song_name)
            play_pause_button.configure(image=pause_image)
            pygame.mixer.music.play()

def play_next():
    global lists, active_song, active_list, folder_path, active_song_label
    global paused, playing, play_pause_button, song_cover_label, song_cover_image, status_bar

    list = lists[active_list]
    curr_song_index = list.index(active_song)
    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    if curr_song_index == len(list) - 1:
        active_song = list[0]
    else:
        active_song = list[curr_song_index+1]

    try:
        music = ID3(folder_path + "/" + active_song)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(Image.open(BytesIO(pic_bytes)).resize((250, 250)))
        song_cover_label.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
        song_cover_label.configure(image=song_cover_image)

    status_bar.configure(text=active_song)
    pygame.mixer.music.load(folder_path + "/" + active_song)
    pygame.mixer.music.play()

def play_previous():
    global lists, active_song, active_list, active_song, folder_path, active_song_label
    global paused, playing, play_pause_button, song_cover_label, song_cover_image, status_bar
    list = lists[active_list]
    curr_song_index = list.index(active_song)
    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    if curr_song_index == 0:
        active_song = list[-1]
    else:
        active_song = list[curr_song_index-1]

    try:
        music = ID3(folder_path + "/" + active_song)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(Image.open(BytesIO(pic_bytes)).resize((250, 250)))
        song_cover_label.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
        song_cover_label.configure(image=song_cover_image)

    status_bar.configure(text=active_song)
    pygame.mixer.music.load(folder_path + "/" + active_song)
    pygame.mixer.music.play()

def select_song(event):
    global songs_listbox, lists, status_bar, song_cover_label, song_cover_image
    global pause_image, paused, playing

    selected_index = songs_listbox.curselection()
    selected_song = songs_listbox.get(selected_index)

    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    try:
        music = ID3(folder_path + "/" + selected_song)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(Image.open(BytesIO(pic_bytes)).resize((250, 250)))
        song_cover_label.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
        song_cover_label.configure(image=song_cover_image)
    
    status_bar.configure(text=selected_song)
    pygame.mixer.music.load(folder_path + "/" + selected_song)
    pygame.mixer.music.play()

def select_list(event): # wasn't completed
    print("a list selected")

def init(): # wasn't completed
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"):
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)

# main app object
root = tk.Tk()

# app configurations
root.geometry("900x540+300+150")
root.resizable(0, 0)
root.title("Smart Music Player")
root.iconbitmap("./icons/icon.ico")

# create icon images
play_image = ImageTk.PhotoImage(Image.open("./icons/play.png").resize((50, 50)))
pause_image = ImageTk.PhotoImage(Image.open("./icons/pause.png").resize((50, 50)))
previous_image = ImageTk.PhotoImage(Image.open("./icons/previous.png").resize((50, 50)))
next_image = ImageTk.PhotoImage(Image.open("./icons/next.png").resize((50, 50)))
song_cover_image = ImageTk.PhotoImage(Image.open("./icons/cover_art.png").resize((250, 250)))

# create widgets
menu = tk.Menu(root, tearoff=0)
tools = tk.Menu(menu, tearoff=0)
about = tk.Menu(menu, tearoff=0)

lists_listbox = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0)
songs_listbox = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0)

lists_label = ttk.Label(root, text="LISTS", anchor=tk.CENTER, background="#97c728")
songs_label = ttk.Label(root, text="SONGS", anchor=tk.CENTER, background="#97c728")
status_bar = ttk.Label(root, text="Please click the 'Add Folder' button to add songs...", anchor=tk.W, relief="sunken", background="#97c728")

add_folder_button = ttk.Button(root, text="Add Folder", command=add_folder)
song_cover_label = ttk.Label(root, image=song_cover_image)
play_pause_button = ttk.Button(root, image=play_image, command=play_pause)
next_button = ttk.Button(root, image=next_image, command=play_next)
previous_button = ttk.Button(root, image=previous_image, command=play_previous)


# layouting
lists_listbox.place(x=0, y=60, width=200, height=360)
songs_listbox.place(x=550, y=30, width=350, height=390)

lists_label.place(x=0, y=0, width=200, height=30)
songs_label.place(x=550, y=0, width=350, height=30)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

add_folder_button.place(x=0, y=30, width=200, height=30)
song_cover_label.place(x=250, y=100, width=250, height=250)
previous_button.place(x=220, y=430)
play_pause_button.place(x=350, y=430)
next_button.place(x=480, y=430)

#widget configurations
root.configure(menu=menu)
menu.add_cascade(label="Tools", menu=tools)
menu.add_cascade(label="About", menu=about)

tools.add_command(label="Add Folder", command=add_folder)

songs_listbox.bind("<Double-1>", select_song)
lists_listbox.bind("<<ListboxSelect>>", select_list)


# initialize pygame and start the main loop
init()
pygame.init()
pygame.mixer.init()
root.mainloop()