import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import pygame
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


# Added descriptive class name.
class MusicPlayer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Instance attributes replace all global variables.
        self.playlist = []
        self.current_song_index = 0
        self.is_paused = False
        self.has_started_playback = False
        self.song_end_event = pygame.USEREVENT + 1

        # CHANGED: Track the scheduled check so it can be cancelled on exit.

        self.music_check_id = None

        pygame.mixer.music.set_endevent(self.song_end_event)

        self.create_widgets()

        # CHANGED: Close the application and clean up resources properly.

        self.master.protocol("WM_DELETE_WINDOW", self.close)

        # CHANGED: Schedule music checks through Tkinter.

        self.check_music()

    # Widget creation has its own method.
    def create_widgets(self):
        # CHANGED: Shared styling is defined once.
        button_options = {
            "bg": "AntiqueWhite1",
            "width": 50,
        }

        # CHANGED: Descriptive method names replace button1, button2, etc.
        add_button = tk.Button(
            self,
            text="ADD TO LIST",
            command=self.add_songs,
            **button_options,
        )
        add_button.grid(row=0, column=0, pady=3)

        play_button = tk.Button(
            self,
            text="PLAY SONG",
            command=self.play_song,
            **button_options,
        )
        play_button.grid(row=1, column=0, pady=3)

        pause_button = tk.Button(
            self,
            text="PAUSE/UNPAUSE",
            command=self.toggle_pause,
            **button_options,
        )
        pause_button.grid(row=2, column=0, pady=3)

        previous_button = tk.Button(
            self,
            text="PREVIOUS SONG",
            command=self.play_previous_song,
            **button_options,
        )
        previous_button.grid(row=3, column=0, pady=3)

        next_button = tk.Button(
            self,
            text="NEXT SONG",
            command=self.play_next_song,
            **button_options,
        )
        next_button.grid(row=4, column=0, pady=3)

        # Descriptive widget names and a valid font tuple.
        self.now_playing_label = tk.Label(
            self,
            text="No song playing",
            fg="black",
            font=("Helvetica", 10, "bold italic"),
            bg="ivory2",
            wraplength=450,
        )
        self.now_playing_label.grid(row=5, column=0, pady=10)

        self.playlist_text = tk.Text(
            self,
            wrap=tk.WORD,
            width=55,
            height=15,
            state=tk.DISABLED,
        )
        self.playlist_text.grid(row=6, column=0)

    def add_songs(self):
        # CHANGED: Correct file-dialog call and MP3 file filter.
        selected_files = filedialog.askopenfilenames(
            parent=self.master,
            title="Select songs",
            filetypes=[("MP3 files", "*.mp3")],
        )

        # CHANGED: Handle cancellation explicitly.
        if not selected_files:
            return

        self.playlist.extend(selected_files)
        self.refresh_playlist()

    # Reading metadata is separate from updating the interface.
    def get_song_description(self, song_path):
        fallback_title = Path(song_path).stem

        try:
            tags = EasyID3(song_path)
        except ID3NoHeaderError:
            # CHANGED: A song without ID3 tags uses its filename.
            return fallback_title
        except (MutagenError, OSError) as error:
            # CHANGED: Expected metadata errors are visible during development.
            print(f"Could not read metadata for {song_path}: {error}")
            return fallback_title

        # CHANGED: Missing or empty tags have sensible defaults.
        titles = tags.get("title") or [fallback_title]
        artists = tags.get("artist") or ["Unknown artist"]

        return f"{titles[0]} - {artists[0]}"

    # Playlist rendering has one responsibility.
    def refresh_playlist(self):
        self.playlist_text.config(state=tk.NORMAL)

        # CHANGED: Tkinter text indices start at "1.0".
        self.playlist_text.delete("1.0", tk.END)

        for number, song_path in enumerate(self.playlist, start=1):
            description = self.get_song_description(song_path)
            self.playlist_text.insert(
                tk.END,
                f"{number}: {description}\n",
            )

        # CHANGED: Prevent users from editing the displayed playlist.
        self.playlist_text.config(state=tk.DISABLED)

    def play_song(self):
        # CHANGED: Guard against an empty playlist.
        if not self.playlist:
            return

        song_path = self.playlist[self.current_song_index]

        # CHANGED: Stop previous playback and discard stale end events.
        pygame.mixer.music.stop()
        pygame.event.clear(self.song_end_event)

        self.has_started_playback = False
        self.is_paused = False

        try:
            pygame.mixer.music.load(song_path)

            # CHANGED: Play once; play(1) would repeat the song.
            pygame.mixer.music.play()
        except (pygame.error, OSError) as error:
            # CHANGED: Report specific errors instead of silently ignoring them.
            self.now_playing_label.config(text="Playback failed")
            messagebox.showerror(
                "Playback error",
                f"Could not play:\n{song_path}\n\n{error}",
                parent=self.master,
            )
            return

        self.has_started_playback = True

        description = self.get_song_description(song_path)

        # CHANGED: Reuse the same metadata formatting as the playlist.
        self.now_playing_label.config(
            text=(
                f"Now playing: {self.current_song_index + 1}. "
                f"{description}"
            )
        )

    def toggle_pause(self):
        # CHANGED: Do not change pause state before playback starts.
        if not self.has_started_playback:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        # CHANGED: Toggle the Boolean in one place.
        self.is_paused = not self.is_paused

    def play_next_song(self):
        if not self.playlist:
            return

        # CHANGED: Modulo wraps the last index back to the first.
        self.current_song_index = (
            self.current_song_index + 1
        ) % len(self.playlist)

        self.play_song()

    def play_previous_song(self):
        if not self.playlist:
            return

        # CHANGED: Modulo also wraps backwards.
        self.current_song_index = (
            self.current_song_index - 1
        ) % len(self.playlist)

        self.play_song()

    def check_music(self):
        # CHANGED: Read song-end events without a manual infinite loop.
        for event in pygame.event.get():
            if event.type == self.song_end_event:
                self.has_started_playback = False
                self.play_next_song()
                break

        self.music_check_id = self.after(100, self.check_music)

    # Cancel pending callbacks before destroying the window.
    def close(self):
        if self.music_check_id is not None:
            self.after_cancel(self.music_check_id)
            self.music_check_id = None

        self.master.destroy()


# Application startup is separate from the player class.
def main():
    window = tk.Tk()
    window.geometry("500x500")
    window.title("MP3 Music Player")

    try:
        pygame.init()

        # CHANGED: Explicitly initialize audio so failure is reported here.
        pygame.mixer.init()

        app = MusicPlayer(window)
        app.grid(padx=15, pady=15)

        # CHANGED: Use Tkinter's normal event loop.
        window.mainloop()
    finally:
        # CHANGED: Release Pygame resources even if an error occurs.
        pygame.quit()


# CHANGED: Importing this module does not launch the application.
if __name__ == "__main__":
    main()