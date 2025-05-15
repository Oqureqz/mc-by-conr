# Automatyczna instalacja potrzebnych bibliotek
import subprocess
import sys
import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
import ctypes

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import minecraft_launcher_lib
except ImportError:
    print("Instalowanie potrzebnych bibliotek... 1/2")
    install("minecraft-launcher-lib")
    import minecraft_launcher_lib

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Instalowanie potrzebnych bibliotek... 2/2")
    install("Pillow")
    from PIL import Image, ImageTk

# Tworzenie okna
root = tk.Tk()
root.title("Minecraft by Conr")
root.geometry("800x400")
root.resizable(False, False)

# RAM domyślnie
ram_value = tk.StringVar(value="2G")

# Rejestracja czcionki
font_path = os.path.abspath("font.ttf")
try:
    if os.path.exists(font_path):
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
        custom_font = ("Minecraft Seven V2", 12)
    else:
        raise FileNotFoundError("Nie znaleziono czcionki.")
except Exception as e:
    print(f"Nie udało się załadować czcionki z pliku: {e}")
    custom_font = ("Arial", 12)

# Ścieżka do katalogu z wersjami Minecrafta
minecraft_directory = os.path.expanduser("minecraft")
versions_path = os.path.join(minecraft_directory, "versions")

# Mapowanie wersji: wyświetlana nazwa → prawdziwa nazwa
def get_installed_versions():
    if not os.path.exists(versions_path):
        return {}, ["Brak wersji"]

    all_versions = [v for v in os.listdir(versions_path) if os.path.isdir(os.path.join(versions_path, v))]
    display_to_real = {}
    display_names = []

    for version in all_versions:
        if version == "1.12.2":
            continue  # Ukryj tę wersję

        if "forge" in version:
            short_name = version.split("-forge")[0]
        else:
            short_name = version

        counter = 2
        base_name = short_name
        while short_name in display_to_real:
            short_name = f"{base_name} #{counter}"
            counter += 1

        display_to_real[short_name] = version
        display_names.append(short_name)

    if not display_names:
        display_to_real["Brak wersji"] = "none"
        display_names.append("Brak wersji")

    display_names.append("Więcej wersji już wkrótce!")

    return display_to_real, display_names

# Funkcja uruchamiająca grę
def launch_game():
    username = username_entry.get()
    ram = ram_value.get()
    selected_display_name = selected_version.get()
    version = version_map.get(selected_display_name, "none")

    if selected_display_name == "Więcej wersji już wkrótce!":
        messagebox.showinfo("Srakinszon", "Mordko, poczekaj, jescze nie teraz :)")
        return

    if not username:
        messagebox.showerror("Błąd", "Nie możesz mieć pustego nicku!")
        return

    if version == "none":
        messagebox.showerror("Błąd", "Brak zainstalowanych wersji Minecrafta.")
        return

    if not (ram.endswith('G') or ram.endswith('M')):
        messagebox.showerror("Błąd", "Wartość RAM musi kończyć się na 'G' lub 'M'!")
        return

    options = {
        "username": username,
        "uuid": "7905dc3e-919b-4559-af51-c0394c915800",
        "token": "null"
    }

    minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_directory)
    command = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_directory, options)
    java_args = [command[0], f"-Xmx{ram}", f"-Xms{ram}"] + command[1:]

    subprocess.Popen(java_args, creationflags=subprocess.CREATE_NO_WINDOW)
    root.destroy()

# Funkcja otwierająca okno zaawansowane
def open_advanced():
    adv = tk.Toplevel(root)
    adv.title("Ustawienia zaawansowane")
    adv.geometry("300x150")
    adv.resizable(False, False)

    tk.Label(adv, text="Ilość RAM (np. 2G lub 2048M):", font=custom_font).pack(pady=10)
    ram_entry = tk.Entry(adv, font=custom_font, textvariable=ram_value)
    ram_entry.pack(pady=5)

    def save_and_close():
        if not ram_value.get().endswith("G") and not ram_value.get().endswith("M"):
            messagebox.showerror("Błąd", "RAM musi kończyć się na 'G' lub 'M'")
            return
        adv.destroy()

    tk.Button(adv, text="Zapisz", font=custom_font, command=save_and_close).pack(pady=10)

# Tło
try:
    background_img = Image.open("background.png").resize((800, 400))
    background_photo = ImageTk.PhotoImage(background_img)
    background_label = tk.Label(root, image=background_photo)
    background_label.image = background_photo
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError:
    print("Brak background.png — tło nie zostanie ustawione.")

# Ikona
try:
    img = Image.open("logo.jpg").resize((32, 32))
    photo = ImageTk.PhotoImage(img)
    root.iconphoto(False, photo)
except FileNotFoundError:
    print("Brak ikony, używana jest domyślna.")

# Logo
try:
    img = Image.open("logo.jpg").resize((150, 150))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(root, image=photo, bg="white")
    label_img.image = photo
    label_img.place(x=10, y=10)
except FileNotFoundError:
    tk.Label(root, text="(Brak logo.jpg — LOL)", font=custom_font, bg="white").place(x=10, y=10)

# === UI Elementy ===
bottom_y = 360
nick_x = 10
entry_x = 60
start_x = 220
adv_x = 360

# Nick
tk.Label(root, text="Nick", font=custom_font, bg="white").place(x=nick_x, y=bottom_y)
username_entry = tk.Entry(root, font=custom_font)
username_entry.place(x=entry_x, y=bottom_y, width=150, height=25)

# Lista wersji Minecrafta
selected_version = tk.StringVar()

version_map, version_list = get_installed_versions()
if version_list:
    selected_version.set(version_list[0])
else:
    version_list = ["Brak wersji"]
    version_map = {"Brak wersji": "none"}
    selected_version.set("Brak wersji")

version_menu = ttk.Combobox(root, values=version_list, textvariable=selected_version, state="readonly", font=custom_font)
version_menu.place(x=560, y=bottom_y, width=220, height=25)

# Przycisk start
try:
    start_img = Image.open("start.png").resize((120, 40))
    start_photo = ImageTk.PhotoImage(start_img)
    start_button = tk.Button(root, image=start_photo, command=launch_game, borderwidth=0)
    start_button.image = start_photo
    start_button.place(x=start_x, y=bottom_y - 7)
except FileNotFoundError:
    tk.Button(root, text="Start", font=custom_font, command=launch_game).place(x=start_x, y=bottom_y)

# Przycisk Zaawansowane
tk.Button(root, text="Zaawansowane", font=custom_font, command=open_advanced).place(x=adv_x, y=bottom_y)

# Uruchomienie GUI
root.mainloop()
