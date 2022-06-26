
import math
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from ttkthemes import ThemedTk
from tkinter import messagebox as mb
import os
import pygame
import json
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from io import BytesIO
import threading

import song_classification as sc



active_list = ""
active_song = ""
lists_dict = {}
playing = False
paused = False
song_time_in_seconds = 0
is_song_time_thread_active = False

def start_classification_thread():
    threading.Thread(target=classify_all_songs).start()

def show_about():
    mb.showinfo('About',""" 
    This app made to test song classification model created using tensorflow and GTZAN dataset.\n 
    Creator of this apllication is Halil Aydın.\n
    Github link : https://github.com/halilaydin242188.\n 
    Source materials: ...
    """)

def classify_all_songs():
    global lists_dict, listbox_lists, label_statusbar
    classified_songs = []

    # get the classified songs so you can pass them
    for list_name in lists_dict:
        if list_name == "All Songs":
            continue
        else:
            for song_name in lists_dict[list_name]:
                classified_songs.append(song_name)
    
    # loop the lists_dict, classify songs and update the lists_dic
    for song_name in lists_dict["All Songs"]:
        if song_name not in classified_songs:

            song_path = lists_dict["All Songs"][song_name]
            song_genre = sc.get_song_genre(song_path)

            print("CLASSIFIED : {} , GENRE : {}".format(song_name, song_genre))
            label_statusbar.configure(text="CLASSIFIED : {} , GENRE : {}".format(song_name, song_genre))

            if song_genre not in lists_dict.keys():
                lists_dict[song_genre] = {}

            lists_dict[song_genre][song_name] = song_path

    # update listbox_lists widget
    listbox_lists.delete(0, tk.END)
    for list_name in lists_dict:
        listbox_lists.insert(tk.END, list_name)

    # update the song_lists.json file with new lists_dict
    os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
    with open("song_lists.json", "w") as write_file:
        json.dump(lists_dict, write_file, indent=1)

    label_statusbar.configure(text="Classification is finished.")
    print("Classification is finished")
        
def get_album_cover(song_path):
    global label_song_cover, image_song_cover
    """
    try:
        music = ID3(song_path)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(pic.resize((250, 250)))
        label_song_cover.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
        label_song_cover.configure(image=image_song_cover)
    """
    label_song_cover.configure(image=image_song_cover)

def save_lists_as_json(folder_path, song_names):
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"): # if json file exist, get it
        os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)
    else:
        lists_dict = {"All Songs": {}}
    
    for song_name in song_names:
        lists_dict["All Songs"][song_name] = folder_path + "/" + song_name
    
    os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
    with open("song_lists.json", "w") as write_file:
        json.dump(lists_dict, write_file, indent=1)

def get_path_and_songnames():
    music_ex = ['mp3','wav','mpeg','m4a','wma','ogg']
    song_names = []
    
    folder_path = fd.askdirectory(title="Select The Song Folder")
    os.chdir(folder_path)
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        if file_name.split(".")[-1] in music_ex:
            song_names.append(file_name)

    return folder_path, song_names

def add_folder():
    global listbox_lists, listbox_songs, active_song, active_list, lists_dict, label_statusbar
    folder_path, song_names = get_path_and_songnames()

    if not ( "All Songs" in lists_dict.keys() ):
        lists_dict["All Songs"] = {}

    for song_name in song_names:
        lists_dict["All Songs"][song_name] = folder_path + "/" + song_name
    
    listbox_lists.delete(0, tk.END)
    listbox_songs.delete(0, tk.END)

    for list_name  in lists_dict:
        listbox_lists.insert(tk.END, list_name)
        for song_name in lists_dict[list_name].keys():
            listbox_songs.insert(tk.END, song_name)

    save_lists_as_json(folder_path, song_names)
    label_statusbar.configure(text="New Songs Were Added")

    active_list = "All Songs"

def play_pause():
    global listbox_songs, playing, paused, button_play_pause, active_list, scale_music_scroll, is_song_time_thread_active
    global image_play, image_pause, active_song, label_statusbar, lists_dict, song_time_in_seconds

    if playing: 
        paused = True
        playing = False
        button_play_pause.configure(image=image_play)
        label_statusbar.configure(text="PAUSED : {}".format(active_song))
        pygame.mixer.music.pause()

    else:
        if paused:
            paused = False
            playing = True
            button_play_pause.configure(image=image_pause)
            threading.Thread(target=song_time).start()
            label_statusbar.configure(text="PLAYING : {}".format(active_song))
            pygame.mixer.music.unpause()
            threading.Thread(target=song_time).start()
        else:
            song_name = listbox_songs.get(0)
            song_path = lists_dict[active_list][song_name]
            paused = False
            playing = True
            active_song = song_name
            label_statusbar.configure(text="PLAYING : {}".format(active_song))
            button_play_pause.configure(image=image_pause)
            get_album_cover(song_path)

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            set_audio_length_label()

            if is_song_time_thread_active:
                pass
            else:
                is_song_time_thread_active = True
                threading.Thread(target=song_time).start()
                
def play_next():
    global active_song, active_list, lists_dict, scale_music_scroll, song_time_in_seconds, is_song_time_thread_active
    global paused, playing, button_play_pause, label_song_cover, image_song_cover, label_statusbar

    songs = listbox_songs.get(0, tk.END)
    curr_song_index = songs.index(active_song)

    if curr_song_index == len(songs) - 1:
        active_song = songs[0]
    else:
        active_song = songs[curr_song_index+1]

    paused = False
    playing = True
    button_play_pause.configure(image=image_pause)
    song_path = lists_dict[active_list][active_song]
    
    get_album_cover(song_path)

    label_statusbar.configure(text="PLAYING : {}".format(active_song))
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

    set_audio_length_label()

    scale_music_scroll.configure(value=0)
    song_time_in_seconds = 0
    if is_song_time_thread_active:
        pass
    else:
        is_song_time_thread_active = True
        threading.Thread(target=song_time).start()

def play_previous():
    global active_song, active_list, active_song, lists_dict, scale_music_scroll, song_time_in_seconds
    global paused, playing, button_play_pause, label_song_cover, image_song_cover, label_statusbar, is_song_time_thread_active

    songs = listbox_songs.get(0, tk.END)
    curr_song_index = songs.index(active_song)
    paused = False
    playing = True
    button_play_pause.configure(image=image_pause)

    if curr_song_index == 0:
        active_song = songs[-1]
    else:
        active_song = songs[curr_song_index-1]

    song_path = lists_dict[active_list][active_song]

    get_album_cover(song_path)

    label_statusbar.configure(text="PLAYING : {}".format(active_song))
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

    set_audio_length_label()

    scale_music_scroll.configure(value=0)
    song_time_in_seconds = 0
    if is_song_time_thread_active:
        pass
    else:
        is_song_time_thread_active = True
        threading.Thread(target=song_time).start()

def select_song(event):
    global listbox_songs, label_statusbar, label_song_cover, image_song_cover, is_song_time_thread_active
    global image_pause, paused, playing, active_song, scale_music_scroll, song_time_in_seconds

    selected_index = listbox_songs.curselection()
    selected_song = listbox_songs.get(selected_index)

    active_song = selected_song
    paused = False
    playing = True
    button_play_pause.configure(image=image_pause)

    song_path = lists_dict[active_list][selected_song]
    get_album_cover(song_path)
    
    label_statusbar.configure(text="PLAYING : {}".format(active_song))
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

    set_audio_length_label()

    scale_music_scroll.configure(value=0)
    song_time_in_seconds = 0
    if is_song_time_thread_active:
        pass
    else:
        is_song_time_thread_active = True
        threading.Thread(target=song_time).start()

def select_list(event):
    global listbox_lists, listbox_songs, active_list, lists_dict

    selected_index = listbox_lists.curselection()
    selected_list = listbox_lists.get(selected_index)
    active_list = selected_list

    song_names = []
    for song_name in lists_dict[active_list].keys():
        song_names.append(song_name)
    song_names.sort(reverse=True)
    listbox_songs.delete(0, tk.END)
    for song_name in song_names:
        listbox_songs.insert(0, song_name)

def init():
    global lists_dict, listbox_lists, listbox_songs, active_list
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"):
        os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)
    
        for list_name  in lists_dict:
            listbox_lists.insert(tk.END, list_name)
            if list_name == "All Songs":
                for song_name in lists_dict[list_name].keys():
                    listbox_songs.insert(tk.END, song_name)

        active_list = "All Songs"
        play_pause()

def scale(value):
    audio_length = MP3(lists_dict["All Songs"][active_song]).info.length
    set_value = (audio_length * float(value)) / 100.0

    set_time(set_value)

    pygame.mixer.music.rewind()
    pygame.mixer.music.set_pos(set_value)

def set_time(time_in_seconds):
    global label_time, song_time_in_seconds, scale_music_scroll
    song_time_in_seconds = time_in_seconds

    audio_length = MP3(lists_dict["All Songs"][active_song]).info.length
    scale_value = song_time_in_seconds * 100 / audio_length
    scale_music_scroll.configure(value=scale_value)

    minutes = math.floor(song_time_in_seconds / 60)
    seconds = int(song_time_in_seconds % 60 )
    if minutes < 10:
        if seconds < 10:
            label_time.configure(text=f"0{minutes}:0{seconds}")
        else:
            label_time.configure(text=f"0{minutes}:{seconds}")

    else:
        if seconds < 10:
            label_time.configure(text=f"{minutes}:0{seconds}")
        else:
            label_time.configure(text=f"{minutes}:{seconds}")

def song_time():
    global song_time_in_seconds
    while pygame.mixer.music.get_busy():
        song_time_in_seconds += 0.99
        set_time(song_time_in_seconds)
        time.sleep(0.99)

def set_audio_length_label():
    global label_audio_length

    audio_length = MP3(lists_dict["All Songs"][active_song]).info.length
    audio_minutes_length = math.floor(audio_length / 60)
    audio_seconds_length = int(audio_length % 60 )

    if audio_minutes_length < 10:
        if audio_seconds_length < 10:
            label_audio_length.configure(text=f"0{audio_minutes_length}:0{audio_seconds_length}")
        else:
            label_audio_length.configure(text=f"0{audio_minutes_length}:{audio_seconds_length}")

    else:
        if audio_seconds_length < 10:
            label_audio_length.configure(text=f"{audio_minutes_length}:0{audio_seconds_length}")
        else:
            label_audio_length.configure(text=f"{audio_minutes_length}:{audio_seconds_length}")


# main app object
#root = tk.Tk()
#root = ThemedTk(theme="winxpblue")
#root = ThemedTk(theme="adapta")
root = ThemedTk(theme="breeze")

# app configurations
root.geometry("900x540+300+150")
root.resizable(0, 0)
root.title("Smart Music Player")
root.iconbitmap("./icons/icon2.ico")

# create icon images
image_play = ImageTk.PhotoImage(Image.open("./icons/play.png").resize((50, 50)))
image_pause = ImageTk.PhotoImage(Image.open("./icons/pause.png").resize((50, 50)))
image_previous = ImageTk.PhotoImage(Image.open("./icons/previous.png").resize((50, 50)))
image_next = ImageTk.PhotoImage(Image.open("./icons/next.png").resize((50, 50)))
image_song_cover = ImageTk.PhotoImage(Image.open("./icons/song_cover.png").resize((340, 340)))

# create widgets
menu = tk.Menu(root, tearoff=0)
tools = tk.Menu(menu, tearoff=0)
about = tk.Menu(menu, tearoff=0)

listbox_lists = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0, background="#9cefff", font="Courier 10 bold")
listbox_songs = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0, background="#9cefff", font="Courier 10")

label_lists = ttk.Label(root, text="LISTS", anchor=tk.CENTER, background="#ffa294", font="Times 15 roman bold")
label_songs = ttk.Label(root, text="SONGS", anchor=tk.CENTER, background="#ffa294", font="Times 15 roman bold")
label_statusbar = ttk.Label(root, text="Please click the 'Add Folder' from 'Tools' button to add songs...", anchor=tk.W, relief="sunken", background="#e2f29b", font="Times 11 italic bold")
label_song_cover = ttk.Label(root, image=image_song_cover)
label_time = ttk.Label(root, text="00:00")
label_audio_length = ttk.Label(root, text="00:00")

# button_add_folder = ttk.Button(root, text="Add Folder", command=add_folder)
button_play_pause = ttk.Button(root, image=image_play, command=play_pause)
button_next = ttk.Button(root, image=image_next, command=play_next)
button_previous = ttk.Button(root, image=image_previous, command=play_previous)

scale_music_scroll = ttk.Scale(root, command=scale, orient=tk.HORIZONTAL, from_=0.0, to=99.0)


# layouting
listbox_lists.place(x=0, y=40, width=200, height=340)
listbox_songs.place(x=550, y=40, width=350, height=340)

label_lists.place(x=0, y=5, width=200, height=30)
label_songs.place(x=550, y=5, width=350, height=30)
label_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

button_previous.place(x=220, y=430)
button_play_pause.place(x=350, y=430)
button_next.place(x=480, y=430)
label_song_cover.place(x=200, y=30, width=340, height=340)
label_time.place(x=110, y=400, width=40, height=20)
label_audio_length.place(x=600, y=400, width=40, height=20)

scale_music_scroll.place(x=150, y=400, width=450, height=20)

#widget configurations
root.configure(menu=menu)
menu.add_cascade(label="Tools", menu=tools)
menu.add_cascade(label="About", menu=about)

tools.add_command(label="Add Folder", command=add_folder)
tools.add_command(label="Classify The Songs", command=start_classification_thread)
about.add_command(label="About The App", command=show_about)

listbox_songs.bind("<Double-1>", select_song)
listbox_lists.bind("<Double-1>", select_list)


# initialize pygame and start the main loop
pygame.init()
pygame.mixer.init()
init()
root.mainloop()