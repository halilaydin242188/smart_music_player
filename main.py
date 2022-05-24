
"""
to do: 
    classification is so slow, fix it
    classification accuracy is not good enough, try to make a better model
    implement widgets for player and audio levels
    finding music's album cover not working well, check the try chatch blog
    download nice icons from internet , https://icon-icons.com/

"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import os
import pygame
import json
from PIL import Image, ImageTk
from mutagen.id3 import ID3
from io import BytesIO

import song_classification as sc


active_list = ""
active_song = ""
lists_dict = {}
playing = False
paused = False

def classify_songs():
    global lists_dict, lists_listbox
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

            if song_genre not in lists_dict.keys():
                lists_dict[song_genre] = {}

            lists_dict[song_genre][song_name] = song_path
            print("--- {} IS CLASSIFIED ---".format(song_name))

    # update lists_listbox widget
    lists_listbox.delete(0, tk.END)
    for list_name in lists_dict:
        lists_listbox.insert(tk.END, list_name)

    # update the song_lists.json file with new lists_dict
    os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
    with open("song_lists.json", "w") as write_file:
        json.dump(lists_dict, write_file)
        
def get_album_cover(song_path):
    global song_cover_label, song_cover_image

    try:
        music = ID3(song_path)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(pic.resize((250, 250)))
        song_cover_label.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
        song_cover_label.configure(image=song_cover_image)

def add_song_to_json(folder_path, song_names):
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
        json.dump(lists_dict, write_file)

def get_path_and_songnames():
    music_ex = ['mp3','wav','mpeg','m4a','wma','ogg']
    song_names = []
    
    folder_path = fd.askdirectory(title="Select The Song Folder")
    os.chdir(folder_path)
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        if file_name.split(".")[-1] in music_ex:
            song_names.append(file_name)
    
    add_song_to_json(folder_path, song_names)

    return folder_path, song_names

def add_folder():
    global lists_listbox, songs_listbox, active_song, active_list, lists_dict
    folder_path, song_names = get_path_and_songnames()

    if not ( "All Songs" in lists_dict.keys() ):
        lists_dict["All Songs"] = {}

    for song_name in song_names:
        lists_dict["All Songs"][song_name] = folder_path + "/" + song_name
    
    for list_name  in lists_dict:
        lists_listbox.insert(tk.END, list_name)
        for song_name in lists_dict[list_name].keys():
            songs_listbox.insert(tk.END, song_name)

    active_list = "All Songs"

def play_pause():
    global songs_listbox, playing, paused, play_pause_button, active_list
    global play_image, pause_image, active_song, status_bar, lists_dict

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
            try:
                song_name = songs_listbox.get(0)
                song_path = lists_dict[active_list][song_name]
                paused = False
                playing = True
                active_song = song_name
                status_bar.configure(text=song_name)
                play_pause_button.configure(image=pause_image)
                get_album_cover(song_path)
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(e)
                
def play_next():
    global active_song, active_list, lists_dict, active_song_label
    global paused, playing, play_pause_button, song_cover_label, song_cover_image, status_bar

    songs = songs_listbox.get(0, tk.END)
    curr_song_index = songs.index(active_song)
    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    if curr_song_index == len(songs) - 1:
        active_song = songs[0]
    else:
        active_song = songs[curr_song_index+1]

    song_path = lists_dict[active_list][active_song]
    
    get_album_cover(song_path)

    status_bar.configure(text=active_song)
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def play_previous():
    global active_song, active_list, active_song, lists_dict, active_song_label
    global paused, playing, play_pause_button, song_cover_label, song_cover_image, status_bar

    songs = songs_listbox.get(0, tk.END)
    curr_song_index = songs.index(active_song)
    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    if curr_song_index == 0:
        active_song = songs[-1]
    else:
        active_song = songs[curr_song_index-1]

    song_path = lists_dict[active_list][active_song]

    get_album_cover(song_path)

    status_bar.configure(text=active_song)
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def select_song(event):
    global songs_listbox, status_bar, song_cover_label, song_cover_image
    global pause_image, paused, playing, active_song

    selected_index = songs_listbox.curselection()
    selected_song = songs_listbox.get(selected_index)

    active_song = selected_song
    paused = False
    playing = True
    play_pause_button.configure(image=pause_image)

    song_path = lists_dict[active_list][selected_song]
    get_album_cover(song_path)
    
    status_bar.configure(text=selected_song)
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def select_list(event): # wasn't completed
    global lists_listbox, songs_listbox, active_list, lists_dict

    selected_index = lists_listbox.curselection()
    selected_list = lists_listbox.get(selected_index)
    active_list = selected_list

    song_names = []
    for song_name in lists_dict[active_list].keys():
        song_names.append(song_name)
    song_names.sort(reverse=True)
    songs_listbox.delete(0, tk.END)
    for song_name in song_names:
        songs_listbox.insert(0, song_name)

def init(): # wasn't completed
    global lists_dict, lists_listbox, songs_listbox, active_list
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"):
        os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)
    
        for list_name  in lists_dict:
            lists_listbox.insert(tk.END, list_name)
            for song_name in lists_dict[list_name].keys():
                songs_listbox.insert(tk.END, song_name)

        active_list = "All Songs"
        play_pause()

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
tools.add_command(label="Classify The Songs", command=classify_songs)

songs_listbox.bind("<Double-1>", select_song)
lists_listbox.bind("<Double-1>", select_list)


# initialize pygame and start the main loop
pygame.init()
pygame.mixer.init()
init()
root.mainloop()