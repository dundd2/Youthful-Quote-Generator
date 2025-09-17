from pathlib import Path
from textwrap import dedent

path = Path('youthful-quote-generator.py')
text = path.read_text(encoding='utf-8')

old_block = dedent('''
def configure_voice():
    if not VOICE_SUPPORTED:
        messagebox.showinfo("Voice unavailable", VOICE_UNSUPPORTED_MESSAGE)
        return

    voice_window = tk.Toplevel(root)
    voice_window.title("Voice Settings")
    voice_window.geometry("300x200")
    update_widget_colors(voice_window, get_theme_colors())

    voice_engine = ensure_voice_engine()

    speed_scale = ttk.Scale(voice_window, from_=0, to=200, orient="horizontal")
    speed_scale.set(voice_engine.getProperty('rate'))
    speed_scale.pack(pady=10)

    volume_scale = ttk.Scale(voice_window, from_=0, to=1, orient="horizontal")
    volume_scale.set(voice_engine.getProperty('volume'))
    volume_scale.pack(pady=10)

    def apply_settings():
        current_engine = ensure_voice_engine()
        current_engine.setProperty('rate', speed_scale.get())
        current_engine.setProperty('volume', volume_scale.get())
        voice_window.destroy()

    ttk.Button(voice_window, text="Apply", command=apply_settings).pack(pady=10)
''')

new_block = dedent('''
def configure_voice():
    if not VOICE_SUPPORTED:
        messagebox.showinfo("Voice unavailable", VOICE_UNSUPPORTED_MESSAGE)
        return
    if VOICE_BACKEND != "pyttsx3":
        messagebox.showinfo(
            "Voice settings",
            "Voice settings are available only when the pyttsx3 voice engine is active."
        )
        return

    voice_engine = ensure_voice_engine()
    if voice_engine is None:
        messagebox.showwarning(
            "Voice unavailable",
            "We couldn't load the voice engine. Try again after restarting the app."
        )
        return

    voice_window = tk.Toplevel(root)
    voice_window.title("Voice Settings")
    voice_window.geometry("300x200")
    update_widget_colors(voice_window, get_theme_colors())

    speed_scale = ttk.Scale(voice_window, from_=0, to=200, orient="horizontal")
    speed_scale.set(voice_engine.getProperty('rate'))
    speed_scale.pack(pady=10)

    volume_scale = ttk.Scale(voice_window, from_=0, to=1, orient="horizontal")
    volume_scale.set(voice_engine.getProperty('volume'))
    volume_scale.pack(pady=10)

    def apply_settings():
        current_engine = ensure_voice_engine()
        if current_engine is None:
            messagebox.showwarning(
                "Voice unavailable",
                "We couldn't load the voice engine. Please try again later."
            )
            return
        current_engine.setProperty('rate', speed_scale.get())
        current_engine.setProperty('volume', volume_scale.get())
        voice_window.destroy()

    ttk.Button(voice_window, text="Apply", command=apply_settings).pack(pady=10)
''')

if old_block not in text:
    raise SystemExit('Original configure_voice block not found')

text = text.replace(old_block, new_block, 1)

path.write_text(text, encoding='utf-8')
