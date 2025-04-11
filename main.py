import customtkinter as ctk
import time
import threading
from plyer import notification
import pygame
import os
from datetime import datetime
from PIL import Image, ImageTk

class BeMindful(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ustawienia aplikacji
        self.title("BeMindful")
        self.geometry("400x500")
        self.resizable(False, False)

        # Zmienne
        self.focus_time = 25  # czas nauki w minutach
        self.break_time = 5  # czas przerwy w minutach
        self.is_running = False
        self.timer_thread = None
        self.paused = False
        self.remaining_time = 0

        # Kolory - jasny błękit i pochodne
        self.main_color = "#ADD8E6"  # Jasny błękit
        self.accent_color = "#87CEEB"  # Nieco ciemniejszy błękit
        self.highlight_color = "#B0E0E6"  # Pudrowy niebieski
        self.text_color = "#4682B4"  # Stalowy niebieski

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        ico_file = "BeMindful.ico"
        png_file = "BeMindful.png"

        if os.path.exists(ico_file):
            self.iconbitmap(ico_file)
        elif os.path.exists(png_file):
            # Alternatywne podejście dla systemów, które mogą obsługiwać PNG jako ikony
            # (może nie działać we wszystkich wersjach Windows)
            icon = ImageTk.PhotoImage(file=png_file)
            self.iconphoto(True, icon)

        # Inicjalizacja pygame do odtwarzania dźwięków
        pygame.mixer.init()

        # Tworzenie interfejsu
        self.create_ui()

    def create_ui(self):
        # Główny kontener
        self.main_frame = ctk.CTkFrame(self, fg_color=self.main_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tytuł
        self.label_title = ctk.CTkLabel(
            self.main_frame,
            text="BeMindful",
            font=("Arial", 24, "bold"),
            text_color=self.text_color
        )
        self.label_title.pack(pady=(10, 20))

        # Status
        self.label_status = ctk.CTkLabel(
            self.main_frame,
            text="Gotowy do rozpoczęcia...",
            font=("Arial", 16),
            text_color=self.text_color
        )
        self.label_status.pack(pady=10)

        # Timer
        self.label_timer = ctk.CTkLabel(
            self.main_frame,
            text="25:00",
            font=("Arial", 48, "bold"),
            text_color=self.text_color
        )
        self.label_timer.pack(pady=20)

        # Ramka na przyciski
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(pady=20)

        # Przyciski kontrolne
        self.btn_start = ctk.CTkButton(
            self.button_frame,
            text="Start",
            font=("Arial", 16),
            width=100,
            height=40,
            fg_color=self.accent_color,
            hover_color=self.highlight_color,
            text_color="white",
            command=self.start_timer
        )
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_pause = ctk.CTkButton(
            self.button_frame,
            text="Pauza",
            font=("Arial", 16),
            width=100,
            height=40,
            fg_color=self.accent_color,
            hover_color=self.highlight_color,
            text_color="white",
            command=self.pause_timer,
            state="disabled"
        )
        self.btn_pause.grid(row=0, column=1, padx=10)

        self.btn_reset = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            font=("Arial", 16),
            width=100,
            height=40,
            fg_color=self.accent_color,
            hover_color=self.highlight_color,
            text_color="white",
            command=self.reset_timer,
            state="disabled"
        )
        self.btn_reset.grid(row=0, column=2, padx=10)

        # Ustawienia czasu
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.pack(pady=20)

        # Czas nauki
        self.label_focus = ctk.CTkLabel(
            self.settings_frame,
            text="Czas nauki (min):",
            font=("Arial", 14),
            text_color=self.text_color
        )
        self.label_focus.grid(row=0, column=0, padx=10, pady=5)

        self.focus_slider = ctk.CTkSlider(
            self.settings_frame,
            from_=5,
            to=60,
            number_of_steps=11,
            width=200,
            progress_color=self.accent_color,
            button_color=self.accent_color,
            button_hover_color=self.highlight_color,
            command=self.update_focus_time
        )
        self.focus_slider.grid(row=0, column=1, padx=10, pady=5)
        self.focus_slider.set(self.focus_time)

        self.label_focus_value = ctk.CTkLabel(
            self.settings_frame,
            text=f"{self.focus_time} min",
            font=("Arial", 14),
            text_color=self.text_color,
            width=50
        )
        self.label_focus_value.grid(row=0, column=2, padx=10, pady=5)

        # Czas przerwy
        self.label_break = ctk.CTkLabel(
            self.settings_frame,
            text="Czas przerwy (min):",
            font=("Arial", 14),
            text_color=self.text_color
        )
        self.label_break.grid(row=1, column=0, padx=10, pady=5)

        self.break_slider = ctk.CTkSlider(
            self.settings_frame,
            from_=1,
            to=15,
            number_of_steps=14,
            width=200,
            progress_color=self.accent_color,
            button_color=self.accent_color,
            button_hover_color=self.highlight_color,
            command=self.update_break_time
        )
        self.break_slider.grid(row=1, column=1, padx=10, pady=5)
        self.break_slider.set(self.break_time)

        self.label_break_value = ctk.CTkLabel(
            self.settings_frame,
            text=f"{self.break_time} min",
            font=("Arial", 14),
            text_color=self.text_color,
            width=50
        )
        self.label_break_value.grid(row=1, column=2, padx=10, pady=5)

        # Status na dole
        self.label_session_info = ctk.CTkLabel(
            self.main_frame,
            text="Dzisiaj: 0 sesji nauki",
            font=("Arial", 14),
            text_color=self.text_color
        )
        self.label_session_info.pack(pady=(20, 0))

        # Statystyki
        self.total_sessions = 0
        self.today_sessions = 0
        self.today_date = datetime.now().date()
        self.update_session_info()

    def update_focus_time(self, value):
        self.focus_time = int(value)
        self.label_focus_value.configure(text=f"{self.focus_time} min")
        if not self.is_running:
            self.label_timer.configure(text=f"{self.focus_time:02d}:00")
            self.remaining_time = self.focus_time * 60

    def update_break_time(self, value):
        self.break_time = int(value)
        self.label_break_value.configure(text=f"{self.break_time} min")

    def update_session_info(self):
        # Sprawdź czy to nowy dzień
        current_date = datetime.now().date()
        if current_date != self.today_date:
            self.today_date = current_date
            self.today_sessions = 0

        self.label_session_info.configure(text=f"Dzisiaj: {self.today_sessions} sesji nauki")

    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="BeMindful",
            timeout=5
        )
        # Odtwarzanie łagodnego dźwięku
        try:
            pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "gentle_sound.mp3"))
            pygame.mixer.music.play()
        except:
            print(
                "Nie można znaleźć pliku dźwiękowego. Upewnij się, że gentle_sound.mp3 znajduje się w folderze aplikacji.")

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def start_timer(self):
        if self.paused:
            self.paused = False
            self.label_status.configure(text="Kontynuacja nauki...")
        else:
            self.remaining_time = self.focus_time * 60
            self.label_status.configure(text="Czas na naukę!")
            self.send_notification("BeMindful", "Gotowy do nauki?")

        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_reset.configure(state="normal")
        self.focus_slider.configure(state="disabled")
        self.break_slider.configure(state="disabled")

        # Uruchom timer w osobnym wątku
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def pause_timer(self):
        if not self.paused:
            self.paused = True
            self.btn_pause.configure(text="Wznów")
            self.label_status.configure(text="Pauza")
        else:
            self.paused = False
            self.btn_pause.configure(text="Pauza")
            self.label_status.configure(text="Kontynuacja...")

    def reset_timer(self):
        self.is_running = False
        self.paused = False
        if self.timer_thread:
            # Poczekaj na zakończenie wątku
            self.timer_thread.join(0.1)

        self.remaining_time = self.focus_time * 60
        self.label_timer.configure(text=self.format_time(self.remaining_time))
        self.label_status.configure(text="Gotowy do rozpoczęcia...")

        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled", text="Pauza")
        self.btn_reset.configure(state="disabled")
        self.focus_slider.configure(state="normal")
        self.break_slider.configure(state="normal")

    def run_timer(self):
        session_type = "focus"  # "focus" lub "break"
        notifications = {
            "focus": [
                (0.1, "Włącz ambient do nauki"),
                (0.3, "Sprawdź listę zadań"),
                (0.5, "Wybierz jedno z zadań")
            ],
            "break": [
                (0.1, "Czas na przerwę"),
                (0.9, "Dobra robota")
            ]
        }

        while self.is_running and self.remaining_time >= 0:
            if not self.paused:
                # Aktualizuj timer na głównym wątku
                self.after(10, lambda: self.label_timer.configure(text=self.format_time(self.remaining_time)))

                # Sprawdź czy trzeba wysłać powiadomienie
                for relative_time, message in notifications[session_type]:
                    time_to_check = 0
                    if session_type == "focus":
                        time_to_check = self.focus_time * 60 * (1 - relative_time)
                    else:
                        time_to_check = self.break_time * 60 * (1 - relative_time)

                    if abs(self.remaining_time - time_to_check) < 1:  # W granicach 1 sekundy
                        self.send_notification("BeMindful", message)

                # Odejmij sekundę i poczekaj
                self.remaining_time -= 1
                time.sleep(1)

                # Sprawdź czy czas minął
                if self.remaining_time < 0:
                    if session_type == "focus":
                        # Przełącz na przerwę
                        session_type = "break"
                        self.after(10, lambda: self.label_status.configure(text="Czas na przerwę!"))
                        self.send_notification("BeMindful", "Czas na przerwę!")
                        self.remaining_time = self.break_time * 60
                        self.today_sessions += 1
                        self.update_session_info()
                    else:
                        # Przełącz z powrotem na naukę
                        session_type = "focus"
                        self.after(10, lambda: self.label_status.configure(text="Wracamy do nauki!"))
                        self.send_notification("BeMindful", "Wracamy do nauki!")
                        self.remaining_time = self.focus_time * 60
            else:
                # W pauzie
                time.sleep(0.1)

        # Zresetuj timer po zakończeniu
        if not self.paused and self.is_running:
            self.after(10, self.reset_timer)


if __name__ == "__main__":
    app = BeMindful()
    app.mainloop()