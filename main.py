
"""
to do: 
    classification accuracy is not good enough, try to make a better model
        // # test_data = (10, 130, 13) , should be (1, 130, 13)
    while classifying add a window to show which song is classifying and the result
    implement widgets for player and audio levels
    finding music's album cover not working well, check the try chatch blog
    download nice icons from internet , https://icon-icons.com/

"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from ttkthemes import ThemedTk
from tkinter import messagebox as mb
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

    label_statusbar.configure(text="Classification is finished. You can continue listening to music")
        
def get_album_cover(song_path):
    global label_song_cover, image_song_cover

    try:
        music = ID3(song_path)
        pic_bytes = music.getall("APIC")[0].data
        pic = Image.open(BytesIO(pic_bytes))
        song_own_cover_image = ImageTk.PhotoImage(pic.resize((250, 250)))
        label_song_cover.configure(image=song_own_cover_image)
    except Exception as e:
        print(e)
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
    label_statusbar.configure(text="Click \'Play\' button to play")

    active_list = "All Songs"

def play_pause():
    global listbox_songs, playing, paused, button_play_pause, active_list
    global image_play, image_pause, active_song, label_statusbar, lists_dict

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
            label_statusbar.configure(text="PLAYING : {}".format(active_song))
            pygame.mixer.music.unpause()
        else:
            try:
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
            except Exception as e:
                print(e)
                
def play_next():
    global active_song, active_list, lists_dict, active_song_label
    global paused, playing, button_play_pause, label_song_cover, image_song_cover, label_statusbar

    songs = listbox_songs.get(0, tk.END)
    curr_song_index = songs.index(active_song)
    paused = False
    playing = True
    button_play_pause.configure(image=image_pause)

    if curr_song_index == len(songs) - 1:
        active_song = songs[0]
    else:
        active_song = songs[curr_song_index+1]

    song_path = lists_dict[active_list][active_song]
    
    get_album_cover(song_path)

    label_statusbar.configure(text="PLAYING : {}".format(active_song))
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def play_previous():
    global active_song, active_list, active_song, lists_dict, active_song_label
    global paused, playing, button_play_pause, label_song_cover, image_song_cover, label_statusbar

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

def select_song(event):
    global listbox_songs, label_statusbar, label_song_cover, image_song_cover
    global image_pause, paused, playing, active_song

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

def select_list(event): # wasn't completed
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

def init(): # wasn't completed
    global lists_dict, listbox_lists, listbox_songs, active_list
    if os.path.exists(r"C:\Users\halil\Desktop\smart_music_player\song_lists.json"):
        os.chdir(r"C:\Users\halil\Desktop\smart_music_player")
        with open("song_lists.json", "r") as read_file:
            lists_dict = json.load(read_file)
    
        for list_name  in lists_dict:
            listbox_lists.insert(tk.END, list_name)
            for song_name in lists_dict[list_name].keys():
                listbox_songs.insert(tk.END, song_name)

        active_list = "All Songs"
        play_pause()

# main app object
#root = tk.Tk()
#root = ThemedTk(theme="breeze")
#root = ThemedTk(theme="winxpblue")
root = ThemedTk(theme="adapta")

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
image_song_cover = ImageTk.PhotoImage(Image.open("./icons/cover_art.png").resize((350, 350)))

# create widgets
menu = tk.Menu(root, tearoff=0)
tools = tk.Menu(menu, tearoff=0)
about = tk.Menu(menu, tearoff=0)

listbox_lists = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0, background="#fcdf8d")
listbox_songs = tk.Listbox(root, selectmode=tk.SINGLE, borderwidth=0, highlightthickness=0, background="#fcdf8d")

label_lists = ttk.Label(root, text="LISTS", anchor=tk.CENTER, background="#9ab4fc")
label_songs = ttk.Label(root, text="SONGS", anchor=tk.CENTER, background="#9ab4fc")
label_statusbar = ttk.Label(root, text="Please click the 'Add Folder' from 'Tools' button to add songs...", anchor=tk.W, relief="sunken", background="#e2f29b")
label_song_cover = ttk.Label(root, image=image_song_cover, background="#9ab4fc")

# button_add_folder = ttk.Button(root, text="Add Folder", command=add_folder)
button_play_pause = ttk.Button(root, image=image_play, command=play_pause)
button_next = ttk.Button(root, image=image_next, command=play_next)
button_previous = ttk.Button(root, image=image_previous, command=play_previous)


# layouting
listbox_lists.place(x=0, y=30, width=200, height=390)
listbox_songs.place(x=550, y=30, width=350, height=390)

label_lists.place(x=0, y=0, width=200, height=30)
label_songs.place(x=550, y=0, width=350, height=30)
label_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

# button_add_folder.place(x=0, y=30, width=200, height=30)
button_previous.place(x=220, y=430)
button_play_pause.place(x=350, y=430)
button_next.place(x=480, y=430)
label_song_cover.place(x=200, y=50, width=350, height=350)

#widget configurations
root.configure(menu=menu)
menu.add_cascade(label="Tools", menu=tools)
menu.add_cascade(label="About", menu=about)

tools.add_command(label="Add Folder", command=add_folder)
tools.add_command(label="Classify The Songs", command=classify_all_songs)
about.add_command(label="About The App", command=show_about)

listbox_songs.bind("<Double-1>", select_song)
listbox_lists.bind("<Double-1>", select_list)


# initialize pygame and start the main loop
pygame.init()
pygame.mixer.init()
init()
root.mainloop()