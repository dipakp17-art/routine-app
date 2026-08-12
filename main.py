from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import json
import os
from datetime import date

Window.clearcolor = (1, 0.97, 0.85, 1)

SAVE_FILE = "progress.json"

ROUTINES = {
    "Morning": [
        ("Wake Up", (1, 0.6, 0.2, 1)),
        ("Brush Teeth", (0.3, 0.8, 1, 1)),
        ("Get Dressed", (0.6, 0.4, 1, 1)),
        ("Eat Breakfast", (1, 0.4, 0.4, 1)),
        ("Wear Shoes", (0.3, 0.8, 0.4, 1)),
    ],
    "Bedtime": [
        ("Bath Time", (0.3, 0.8, 1, 1)),
        ("Put on Pyjamas", (0.6, 0.4, 1, 1)),
        ("Brush Teeth", (1, 0.6, 0.2, 1)),
        ("Read a Story", (1, 0.4, 0.4, 1)),
        ("Go to Sleep", (0.3, 0.8, 0.4, 1)),
    ],
}

def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") == str(date.today()):
            return data.get("status", {})
    return {}

def save_progress(status):
    with open(SAVE_FILE, "w") as f:
        json.dump({"date": str(date.today()), "status": status}, f)

class RoutineApp(App):
    def build(self):
        self.status = load_progress()
        self.completed = set()
        self.current = "Morning"
        self.root_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.render()
        return self.root_layout

    def render(self):
        self.root_layout.clear_widgets()
        self.completed = set()

        switch_row = BoxLayout(size_hint=(1, 0.15), spacing=10)
        for name in ROUTINES:
            b = Button(text=name, font_size=20, bold=True)
            b.bind(on_press=self.switch_routine)
            switch_row.add_widget(b)
        reset_btn = Button(text="Reset", font_size=20, bold=True,
                            background_color=(1, 0.3, 0.3, 1), background_normal='')
        reset_btn.bind(on_press=self.reset_routine)
        switch_row.add_widget(reset_btn)
        self.root_layout.add_widget(switch_row)

        self.title_label = Label(text=f"{self.current} Routine", font_size=28, size_hint=(1, 0.2), color=(0.2, 0.2, 0.6, 1), bold=True)
        self.root_layout.add_widget(self.title_label)

        self.steps = ROUTINES[self.current]
        saved_state = self.status.get(self.current, {})

        for label, color in self.steps:
            row = BoxLayout(orientation='horizontal', spacing=8, size_hint=(1, None), height=70)

            btn = Button(text=label, font_size=24, bold=True,
                         background_color=color, background_normal='',
                         size_hint=(0.8, 1))
            btn.step_key = label
            btn.bind(on_press=self.mark_done)
            row.add_widget(btn)

            skip_btn = Button(text="Skip", font_size=16, bold=True,
                               background_color=(0.6, 0.6, 0.6, 1), background_normal='',
                               size_hint=(0.2, 1))
            skip_btn.step_button = btn
            skip_btn.bind(on_press=self.skip_step)
            row.add_widget(skip_btn)

            self.root_layout.add_widget(row)

            saved = saved_state.get(label)
            if saved == "DONE":
                self.completed.add(label)
                btn.text = f"{label}  DONE!"
                btn.background_color = (0.2, 0.9, 0.2, 1)
            elif saved == "SKIPPED":
                self.completed.add(label)
                btn.text = f"{label}  SKIPPED"
                btn.background_color = (0.7, 0.7, 0.7, 1)

        self.check_all_done()

    def switch_routine(self, instance):
        self.current = instance.text
        self.render()

    def reset_routine(self, instance):
        self.status[self.current] = {}
        save_progress(self.status)
        self.render()

    def mark_done(self, instance):
        if "DONE" not in instance.text and "SKIPPED" not in instance.text:
            self.completed.add(instance.step_key)
            instance.text = instance.text + "  DONE!"
            instance.background_color = (0.2, 0.9, 0.2, 1)
            self.status.setdefault(self.current, {})[instance.step_key] = "DONE"
            save_progress(self.status)
        self.check_all_done()

    def skip_step(self, instance):
        btn = instance.step_button
        if "DONE" not in btn.text and "SKIPPED" not in btn.text:
            self.completed.add(btn.step_key)
            btn.text = btn.text + "  SKIPPED"
            btn.background_color = (0.7, 0.7, 0.7, 1)
            self.status.setdefault(self.current, {})[btn.step_key] = "SKIPPED"
            save_progress(self.status)
        self.check_all_done()

    def check_all_done(self):
        if len(self.completed) == len(self.steps):
            self.title_label.text = "GREAT JOB! All Done!"
            self.title_label.color = (1, 0.6, 0, 1)

RoutineApp().run()
