import os
import sys
import re
import random

# ============================================================
# ANDROID SPEECH RECOGNITION
# ============================================================

from android import activity
from jnius import autoclass, PythonJavaClass, java_method

# ============================================================
# SCIENCE ASSISTANT UI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# EXISTING KNOWLEDGE ENGINE
# ============================================================

from knowledge import KNOWLEDGE
from learning import (
    get_all_knowledge,
    add_topic,
    update_topic,
    normalize_subject
)


# ============================================================
# LOAD PERMANENT KNOWLEDGE
# ============================================================

def refresh_knowledge():
    """Reload dynamic knowledge from storage into KNOWLEDGE memory."""
    try:
        learned = get_all_knowledge()
        for subject, concepts in learned.items():
            if subject not in KNOWLEDGE:
                KNOWLEDGE[subject] = {}
            if isinstance(concepts, dict):
                KNOWLEDGE[subject].update(concepts)
    except Exception:
        pass


refresh_knowledge()


# ============================================================
# FEATURE 3: FORMULA & UNIT CONVERTER TOOL
# ============================================================

def convert_units(value, unit_from, unit_to):
    """Converts common science units offline."""
    unit_from, unit_to = unit_from.lower().strip(), unit_to.lower().strip()
    if unit_from == "c" and unit_to == "f":
        return (value * 9/5) + 32
    if unit_from == "f" and unit_to == "c":
        return (value - 32) * 5/9
    if unit_from == "km" and unit_to == "m":
        return value * 1000
    if unit_from == "m" and unit_to == "km":
        return value / 1000
    return None


# ============================================================
# FEATURE 2: INTERACTIVE QUIZ ENGINE
# ============================================================

class QuizEngine:
    """Handles interactive quiz generation from KNOWLEDGE."""
    def __init__(self):
        self.active_quiz = None

    def get_question(self):
        subjects = [s for s in KNOWLEDGE.keys() if isinstance(KNOWLEDGE[s], dict)]
        if not subjects:
            return "No subjects available for quiz."
        subj = random.choice(subjects)
        concepts = list(KNOWLEDGE[subj].keys())
        if not concepts:
            return "No topics available."
        topic = random.choice(concepts)
        data = KNOWLEDGE[subj][topic]
        
        if isinstance(data, dict) and "formula" in data:
            self.active_quiz = {"ans": str(data["formula"]).strip().lower()}
            return f"QUIZ TIME!\nSubject: {subj.title()}\nWhat is the formula for '{topic.title()}'?"
        elif isinstance(data, dict) and ("answer" in data or "definition" in data):
            ans = data.get("answer") or data.get("definition")
            self.active_quiz = {"ans": str(ans).strip().lower()}
            return f"QUIZ TIME!\nSubject: {subj.title()}\nDefine/Explain: '{topic.title()}'"
        return "Try tapping QUIZ again!"

    def check(self, user_ans):
        if not self.active_quiz:
            return None
        target = self.active_quiz["ans"]
        self.active_quiz = None
        if user_ans.lower().strip() in target or target in user_ans.lower().strip():
            return "✓ Correct! Great job!"
        return f"✗ Not quite. The correct answer was:\n{target}"

quiz_tool = QuizEngine()


# ============================================================
# SAFE ANDROID-COMPATIBLE TTS (TEXT TO SPEECH)
# ============================================================

def speak_text(text):
    """Speaks text safely on Android using Plyer's native TTS bridge."""
    import threading
    from plyer import tts

    # Remove Kivy/UI tags
    clean_text = re.sub(r'\[.*?\]', '', str(text)).strip()
    if not clean_text:
        return

    def _speak():
        try:
            tts.speak(message=clean_text)
        except Exception as e:
            print("Plyer TTS error:", e)

    threading.Thread(target=_speak, daemon=True).start()
    

# ============================================================
# AUTO MARKUP PARSER (CHEMISTRY & MATH)
# ============================================================

def format_science_markup(text):
    """
    Cleans raw unicode subscripts/superscripts and applies clean Kivy markup tags.
    """
    if not isinstance(text, str):
        return str(text)

    # 1. Clean unicode characters into standard ASCII numbers first
    unicode_map = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
        '⁰': '^0', '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4',
        '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9'
    }
    for uni_char, ascii_char in unicode_map.items():
        text = text.replace(uni_char, ascii_char)
    
    # 2. Superscript converter (e.g., x^2 -> x[sup]2[/sup])
    text = re.sub(r'\^([0-9a-zA-Z\+\-]+)', r'[sup]\1[/sup]', text)
  
    # 3. Chemical subscript converter
    text = re.sub(r'([A-Z][a-z]?)([0-9]+)', r'\1[sub]\2[/sub]', text)

    # 4. Math variable/index subscript converter (x2, x1, y2, y1, a1, etc.)
    text = re.sub(r'\b([a-zA-Z])([0-9]+)\b', r'\1[sub]\2[/sub]', text)

    # 5. Ionic charge converter (e.g., Fe3+ -> Fe[sup]3+[/sup])
    text = re.sub(r'([A-Z][a-z]?)([0-9]*[\+\-])', r'\1[sup]\2[/sup]', text)

    return text


# ============================================================
# KIVY
# ============================================================

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
# ============================================================
# ANDROID SPEECH RECOGNITION
# ============================================================

try:
    from jnius import autoclass, PythonJavaClass, java_method

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Intent = autoclass("android.content.Intent")
    RecognizerIntent = autoclass("android.speech.RecognizerIntent")

    ANDROID_SPEECH_AVAILABLE = True

except Exception as e:
    print("Android speech unavailable:", e)
    ANDROID_SPEECH_AVAILABLE = False


# ============================================================
# ANDROID KEYBOARD FIX
# ============================================================

Window.softinput_mode = "below_target"


# ============================================================
# THEME PALETTES
# ============================================================

LIGHT_THEME = {
    "bg": (0.95, 0.97, 1.0, 1),
    "card": (1.0, 1.0, 1.0, 1),
    "user_bg": (0.88, 0.93, 1.0, 1),
    "text": (0.08, 0.10, 0.15, 1),
    "primary": (0.12, 0.35, 0.75, 1),
    "primary_dark": (0.07, 0.25, 0.58, 1)
}

DARK_THEME = {
    "bg": (0.10, 0.11, 0.15, 1),
    "card": (0.18, 0.20, 0.26, 1),
    "user_bg": (0.15, 0.30, 0.50, 1),
    "text": (0.92, 0.94, 0.96, 1),
    "primary": (0.25, 0.50, 0.90, 1),
    "primary_dark": (0.45, 0.65, 0.95, 1)
}


# ============================================================
# CLEAN QUESTION
# ============================================================

def clean_question(question):
    q = question.lower().strip()
    for char in ["?", "!", ".", ","]:
        q = q.replace(char, "")
    return q


# ============================================================
# FIND TOPIC (WITH STOP-WORD & WORD BOUNDARY FIX)
# ============================================================

STOP_WORDS = {"the", "a", "an", "is", "of", "in", "to", "what", "tell", "me", "show"}

def find_topic(question):
    clean = clean_question(question)
    matches = []

    for subject, concepts in KNOWLEDGE.items():
        if not isinstance(concepts, dict):
            continue

        for concept, data in concepts.items():
            concept_lower = str(concept).lower().strip()

            if not concept_lower or concept_lower in STOP_WORDS:
                continue

            if concept_lower == clean:
                matches.append((1000 + len(concept_lower), subject, concept, data))
                continue

            pattern = r'\b' + re.escape(concept_lower) + r'\b'
            if re.search(pattern, clean):
                matches.append((len(concept_lower), subject, concept, data))

    if not matches:
        return None

    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[0]


# ============================================================
# QUESTION TYPE
# ============================================================

def get_request_type(question):
    q = clean_question(question)

    formula_phrases = [
        "formula", "what is the formula", "what is its formula",
        "tell me the formula", "give me the formula", "show me the formula",
        "what is the equation", "tell me the equation", "give me the equation"
    ]
    if any(phrase in q for phrase in formula_phrases):
        return "formula"

    example_phrases = [
        "example", "examples", "for example", "give an example",
        "give me an example", "give some examples", "show an example",
        "show me an example", "show some examples"
    ]
    if any(phrase in q for phrase in example_phrases):
        return "examples"

    simple_phrases = [
        "explain simply", "explain simple", "explain in simple words",
        "explain in easy words", "simple explanation", "explain this simply"
    ]
    if any(phrase in q for phrase in simple_phrases):
        return "simple"

    property_phrases = [
        "property", "properties", "characteristic", "characteristics",
        "what are its properties", "what are the properties"
    ]
    if any(phrase in q for phrase in property_phrases):
        return "properties"

    application_phrases = [
        "use", "uses", "application", "applications",
        "what is it used for", "what are its uses", "where is it used"
    ]
    if any(phrase in q for phrase in application_phrases):
        return "applications"

    return None


# ============================================================
# CHAT MESSAGE CARD WITH LISTEN BUTTON
# ============================================================

class ChatCard(BoxLayout):

    def __init__(self, sender, message, user=False, theme=LIGHT_THEME, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(5),
            **kwargs
        )

        self.user = user
        self.theme = theme
        self.raw_message = message
        formatted_message = format_science_markup(str(message))

        background = theme["user_bg"] if user else theme["card"]

        with self.canvas.before:
            self.bg_color = Color(*background)
            self.rectangle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(pos=self.update_background, size=self.update_background)

        # Header Row
        header_row = BoxLayout(size_hint_y=None, height=dp(20))

        self.sender_label = Label(
            text="[b]" + sender + "[/b]",
            markup=True,
            font_size=dp(14),
            color=theme["primary_dark"],
            halign="left",
            valign="middle"
        )
        self.sender_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        header_row.add_widget(self.sender_label)

        if not user:
            self.speak_btn = Button(
                text="[LISTEN]",
                size_hint=(None, None),
                size=(dp(60), dp(20)),
                font_size=dp(10),
                color=theme["primary_dark"],
                background_normal="",
                background_color=(0, 0, 0, 0)
            )
            self.speak_btn.bind(on_press=lambda inst: speak_text(self.raw_message))
            header_row.add_widget(self.speak_btn)

        self.add_widget(header_row)

        self.message_label = Label(
            text=formatted_message,
            markup=True,
            font_size=dp(15),
            color=theme["text"],
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        self.add_widget(self.message_label)

        self.bind(width=self.update_width)
        self.message_label.bind(texture_size=self.update_height)
        self.update_width(self, self.width)

    def update_background(self, instance, value):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size

    def update_width(self, instance, width):
        self.message_label.text_size = (max(dp(50), width - dp(28)), None)

    def update_height(self, instance, texture_size):
        self.message_label.height = texture_size[1]
        self.height = texture_size[1] + dp(52)

    def update_theme(self, theme):
        self.theme = theme
        self.bg_color.rgba = theme["user_bg"] if self.user else theme["card"]
        self.sender_label.color = theme["primary_dark"]
        self.message_label.color = theme["text"]
        if hasattr(self, 'speak_btn'):
            self.speak_btn.color = theme["primary_dark"]
        
# ============================================================
# MAIN UI
# ============================================================

# ============================================================
# ANDROID SPEECH CALLBACK
# ============================================================

# ============================================================
# ANDROID MAIN THREAD RUNNER
# ============================================================

class MainThreadRunnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']

    def __init__(self, function):
        super().__init__()
        self.function = function

    @java_method('()V')
    def run(self):
        self.function()

class SpeechListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/RecognitionListener']

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    @java_method('(Landroid/os/Bundle;)V')
    def onReadyForSpeech(self, params):
        pass

    @java_method('()V')
    def onBeginningOfSpeech(self):
        pass

    @java_method('(F)V')
    def onRmsChanged(self, rmsdB):
        pass

    @java_method('([B)V')
    def onBufferReceived(self, buffer):
        pass

    @java_method('()V')
    def onEndOfSpeech(self):
        pass

    @java_method('(I)V')
    def onError(self, error):
        Clock.schedule_once(
            lambda dt: self.ui.add_message(
                "Assistant",
                "Sorry, I couldn't understand the voice."
            ),
            0
        )

    @java_method('(Landroid/os/Bundle;)V')
    def onResults(self, results):
        matches = results.getStringArrayList(
            "results_recognition"
        )

        if matches and matches.size() > 0:
            text = str(matches.get(0))

            Clock.schedule_once(
                lambda dt: self.ui.set_voice_text(text),
                0
            )

    @java_method('(Landroid/os/Bundle;)V')
    def onPartialResults(self, partial_results):
        pass

    @java_method('(ILandroid/os/Bundle;)V')
    def onEvent(self, event_type, params):
        pass

class ScienceAssistantUI(BoxLayout):

# ========================================================
    # VOICE INPUT
    # ========================================================

    def start_voice_input(self, *args):
        def start_recognition():
            try:
                SpeechRecognizer = autoclass(
                    'android.speech.SpeechRecognizer'
                )
                Intent = autoclass(
                    'android.content.Intent'
                )

                self.speech_listener = SpeechListener(self)

                activity = self.get_android_activity()

                self.speech_recognizer = (
                    SpeechRecognizer.createSpeechRecognizer(activity)
                )

                self.speech_recognizer.setRecognitionListener(
                    self.speech_listener
                )

                intent = Intent(
                    'android.speech.action.RECOGNIZE_SPEECH'
                )

                intent.putExtra(
                    'android.speech.extra.LANGUAGE_MODEL',
                    'free_form'
                )

                intent.putExtra(
                    'android.speech.extra.PROMPT',
                    'Speak your question'
                )

                self.speech_recognizer.startListening(intent)

                Clock.schedule_once(
                    lambda dt: self.add_message(
                        "Assistant",
                        "🎤 Listening... Please speak."
                    ),
                    0
                )

            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.add_message(
                        "Assistant",
                        "Voice input could not start:\n" + str(e)
                    ),
                    0
                )

        MainActivity = autoclass(
            'org.kivy.android.PythonActivity'
        )

        MainActivity.mActivity.runOnUiThread(
            MainThreadRunnable(start_recognition)
        )


    # --------------------------------------------------------
    # THEME TOGGLE METHOD (Must be defined before __init__)
    # --------------------------------------------------------
    def toggle_theme(self, *args):
        """Switches between light and dark UI themes."""
        self.is_dark = not self.is_dark
        self.current_theme = DARK_THEME if self.is_dark else LIGHT_THEME

        # Update window canvas background
        Window.clearcolor = self.current_theme["bg"]

        # Update header & main control buttons
        self.title_label.color = self.current_theme["primary"]
        self.theme_btn.text = "LIGHT" if self.is_dark else "DARK"
        self.theme_btn.background_color = self.current_theme["primary"]
        self.send_button.background_color = self.current_theme["primary"]
        self.search_btn.background_color = self.current_theme["primary"]
        self.quiz_btn.background_color = self.current_theme["primary_dark"]

        # Update subject grid buttons
        for btn in self.subject_buttons:
            btn.background_color = self.current_theme["primary"]

        # Update text inputs
        self.input_box.foreground_color = self.current_theme["text"]
        self.input_box.cursor_color = self.current_theme["primary"]
        self.input_box.background_color = self.current_theme["card"]
        
        self.search_input.foreground_color = self.current_theme["text"]
        self.search_input.background_color = self.current_theme["card"]

        # Redraw existing message cards in chat scroll view
        for card in self.chat.children:
            if isinstance(card, ChatCard):
                card.update_theme(self.current_theme)

    # --------------------------------------------------------
    # CONSTRUCTOR (__init__)
    # --------------------------------------------------------
    def __init__(self, **kwargs):
        self.current_theme = LIGHT_THEME
        self.is_dark = False

        self.current_topic = None
        self.current_subject = None
        self.current_data = None
        self.learning_mode = None
        self.learning_topic = None
        self.learning_subject = None
        self.learning_field = None
        self.learning_data = {}

        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(10), dp(8), dp(10), dp(8)],
            **kwargs
        )

        # Header Section
        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[dp(2), dp(2)],
            spacing=dp(5)
        )

        self.title_label = Label(
            text="[b]SCIENCE ASSISTANT[/b]",
            markup=True,
            font_size=dp(17),
            color=self.current_theme["primary"],
            size_hint_x=0.65,
            halign="left",
            valign="middle"
        )
        self.title_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        header.add_widget(self.title_label)

        self.theme_btn = Button(
            text="DARK",
            size_hint_x=0.35,
            font_size=dp(13),
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=self.current_theme["primary"]
        )
        self.theme_btn.bind(on_press=self.toggle_theme)
        header.add_widget(self.theme_btn)

        self.add_widget(header)

        # Subjects Grid
        self.subjects_grid = GridLayout(
            cols=2,
            spacing=dp(6),
            size_hint_y=None,
            height=dp(105)
        )

        self.subject_buttons = []
        subject_names = ["Mathematics", "Physics", "Chemistry", "Computer Science", "English Grammar"]

        for subject in subject_names:
            button = Button(
                text=subject,
                font_size=dp(14),
                color=(1, 1, 1, 1),
                background_normal="",
                background_color=self.current_theme["primary"]
            )
            button.bind(on_press=lambda instance, s=subject: self.select_subject(s))
            self.subject_buttons.append(button)
            self.subjects_grid.add_widget(button)

        self.add_widget(self.subjects_grid)

        # Quick Search & Quiz Action Bar
        tools_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )

        self.search_input = TextInput(
            hint_text="Search topic or unit...",
            multiline=False,
            font_size=dp(13),
            padding=[dp(8), dp(10)],
            size_hint_x=0.55
        )

        self.search_btn = Button(
            text="SEARCH",
            size_hint_x=0.22,
            font_size=dp(11),
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=self.current_theme["primary"]
        )
        self.search_btn.bind(on_press=self.run_search)

        self.quiz_btn = Button(
            text="QUIZ",
            size_hint_x=0.23,
            font_size=dp(11),
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=self.current_theme["primary_dark"]
        )
        self.quiz_btn.bind(on_press=self.start_quiz)

        tools_layout.add_widget(self.search_input)
        tools_layout.add_widget(self.search_btn)
        tools_layout.add_widget(self.quiz_btn)

        self.add_widget(tools_layout)

        # Scroll Area (Chat Cards Container)
        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
            scroll_type=["content"]
        )

        self.chat = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(4), dp(10), dp(4), dp(15)],
            size_hint_y=None
        )
        self.chat.bind(minimum_height=self.chat.setter("height"))

        self.scroll.add_widget(self.chat)
        self.add_widget(self.scroll)

        # Bottom Question Input Bar
        self.input_area = BoxLayout(
            size_hint_y=None,
            height=dp(65),
            spacing=dp(6)
        )

        self.input_box = TextInput(
            hint_text="Ask anything...",
            multiline=True,
            font_size=dp(16),
            padding=[dp(12), dp(13)],
            background_color=(1, 1, 1, 1),
            foreground_color=self.current_theme["text"],
            cursor_color=self.current_theme["primary"]
        )

        self.send_button = Button(
            text="SEND",
            size_hint_x=None,
            width=dp(95),
            font_size=dp(16),
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=self.current_theme["primary"]
        )
        
        self.send_button.bind(on_press=self.ask)

        self.mic_button = Button(
            text="🎤",
            size_hint_x=None,
            width=dp(55),
            font_size=dp(20),
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=self.current_theme["primary_dark"]
        )
        self.mic_button.bind(on_press=self.start_voice_input)

        self.input_area.add_widget(self.input_box)
        self.input_area.add_widget(self.mic_button)
        self.input_area.add_widget(self.send_button)
        self.add_widget(self.input_area)

        # Welcome Card Initialization
        self.add_message(
            "Assistant",
            "Hello!\n\n"
            "I'm your Science Assistant.\n"
            "Ask questions or try formulas like H2O or x^2 + y^3.\n\n"
            "Tap [LISTEN] on any message to read it aloud."
        )

    # ============================================================
    # FEATURE 2: QUIZ START HANDLER
    # ============================================================
    def start_quiz(self, *args):
        q_text = quiz_tool.get_question()
        self.add_message("Assistant", q_text)

    def toggle_theme(self, *args):
        self.is_dark = not self.is_dark
        self.current_theme = DARK_THEME if self.is_dark else LIGHT_THEME

        Window.clearcolor = self.current_theme["bg"]

        self.title_label.color = self.current_theme["primary"]
        self.theme_btn.text = "LIGHT" if self.is_dark else "DARK"
        self.theme_btn.background_color = self.current_theme["primary"]
        self.send_button.background_color = self.current_theme["primary"]
        self.search_btn.background_color = self.current_theme["primary"]
        self.quiz_btn.background_color = self.current_theme["primary_dark"]

        for btn in self.subject_buttons:
            btn.background_color = self.current_theme["primary"]

        self.input_box.foreground_color = self.current_theme["text"]
        self.input_box.cursor_color = self.current_theme["primary"]
        self.input_box.background_color = self.current_theme["card"]
        
        self.search_input.foreground_color = self.current_theme["text"]
        self.search_input.background_color = self.current_theme["card"]

        for card in self.chat.children:
            if isinstance(card, ChatCard):
                card.update_theme(self.current_theme)

    def add_message(self, sender, message):
        card = ChatCard(
            sender,
            message,
            user=(sender.lower() == "you"),
            theme=self.current_theme
        )
        self.chat.add_widget(card)
        Clock.schedule_once(self.scroll_to_bottom, 0.15)

    def scroll_to_bottom(self, *args):
        self.scroll.scroll_y = 0

    def select_subject(self, subject):
        self.current_subject = subject.lower()
        self.add_message("Assistant", "Subject selected: " + subject + "\n\nNow ask your question.")

    def teach_me(self, question):
        answer = question.strip().lower()

        if self.learning_mode == "field_confirm":
            if answer == "yes":
                self.learning_mode = "field_value"
                self.add_message(
                    "Assistant",
                    "Please provide the " + str(self.learning_field) + " for '" + str(self.current_topic).title() + "':"
                )
                return True
            else:
                self.learning_mode = None
                self.learning_field = None
                self.add_message("Assistant", "Okay, no problem!")
                return True

        if self.learning_mode == "field_value":
            success = update_topic(
                self.current_subject,
                self.current_topic,
                {self.learning_field: question.strip()}
            )
            if success:
                refresh_knowledge()
                if isinstance(self.current_data, dict):
                    self.current_data[self.learning_field] = question.strip()
                self.add_message("Assistant", "✓ Updated '" + str(self.current_topic).title() + "' with new " + str(self.learning_field) + "!")
            else:
                self.add_message("Assistant", "I couldn't update the topic.")

            self.learning_mode = None
            self.learning_field = None
            return True

        if self.learning_mode == "confirm":
            if answer == "yes":
                self.learning_mode = "topic_name"
                self.add_message("Assistant", "Great!\nWhat is the topic name?")
                return True
            if answer == "no":
                self.learning_mode = None
                self.add_message("Assistant", "Okay. We can teach me later.")
                return True
            self.add_message("Assistant", "Please type yes or no.")
            return True

        if self.learning_mode == "topic_name":
            self.learning_topic = question.strip().lower()
            self.learning_mode = "answer"
            self.add_message("Assistant", "Topic: " + self.learning_topic + "\n\nWhat is the answer or definition?")
            return True

        if self.learning_mode == "answer":
            self.learning_data = {"answer": question.strip()}
            self.learning_mode = "subject"
            self.add_message(
                "Assistant",
                "Now tell me the subject:\n\nmathematics\nphysics\nchemistry\ncomputer science\nenglish grammar"
            )
            return True

        if self.learning_mode == "subject":
            subject = normalize_subject(question)
            if not subject:
                self.add_message("Assistant", "I don't recognize that subject.\nPlease type one of the five subjects.")
                return True

            success = add_topic(subject, self.learning_topic, self.learning_data)
            if success:
                refresh_knowledge()
                self.current_subject = subject
                self.current_topic = self.learning_topic
                self.current_data = self.learning_data
                self.add_message("Assistant", "✓ I learned: " + self.learning_topic.title() + "\n✓ Saved permanently.")
            else:
                self.add_message("Assistant", "I couldn't update the topic.")

            self.learning_mode = None
            self.learning_subject = None
            return True

        return False

    def ask(self, *args):
        question = self.input_box.text.strip()
        if not question:
            return

        self.input_box.text = ""
        self.input_box.focus = False
        self.add_message("You", question)

        self.answer_question(question)

    def answer_question(self, question):
        # Active Quiz Check
        if quiz_tool.active_quiz:
            result = quiz_tool.check(question)
            if result:
                self.add_message("Assistant", result)
                return

        if self.learning_mode:
            if self.teach_me(question):
                return

        request_type = get_request_type(question)
        result = find_topic(question)

        if result:
            _, subject, concept, data = result
            self.current_subject = subject
            self.current_topic = concept
            self.current_data = data
            self.show_data(subject, concept, data, request_type)
            return

        if self.current_topic and request_type and isinstance(self.current_data, dict):
            value = self.current_data.get(request_type)
            if value:
                self.show_data(self.current_subject, self.current_topic, self.current_data, request_type)
                return

            self.learning_field = request_type
            self.learning_mode = "field_confirm"
            self.add_message(
                "Assistant",
                "I know the topic '" + self.current_topic.title() + "' but I don't have " + request_type + " yet.\n\nWould you like to teach me? (yes/no)"
            )
            return

        self.learning_mode = "confirm"
        self.add_message("Assistant", "I don't know this topic yet.\n\nWould you like to teach me about it? (yes/no)")

    def show_data(self, subject, concept, data, request_type=None):
        if not isinstance(data, dict):
            self.add_message("Assistant", str(data))
            return

        if request_type:
            value = data.get(request_type)
            if value:
                title = request_type.title()
                message = "Subject: " + subject.title() + "\n\nTopic: " + concept.title() + "\n\n" + title + ":\n" + str(value)
                self.add_message("Assistant", message)
                return

        answer = data.get("answer") or data.get("definition")
        message = "Subject: " + subject.title() + "\n\nTopic: " + concept.title()

        if answer:
            message += "\n\nAnswer:\n" + str(answer)

        formula = data.get("formula")
        if formula:
            message += "\n\nFormula:\n" + str(formula)

        examples = data.get("examples")
        if examples:
            message += "\n\nExamples:\n" + str(examples)

        self.add_message("Assistant", message)
        
        
        # ============================================================
    # FEATURE 1 & 3: SEARCH AND UNIT CONVERTER HANDLER
    # ============================================================
    def run_search(self, *args):
        query = self.search_input.text.strip().lower()
        if not query:
            return

        # Check Unit Conversion format: "convert 100 c to f"
        if "convert" in query:
            parts = query.split()
            try:
                val = float(parts[1])
                u_from = parts[2]
                u_to = parts[4]
                res = convert_units(val, u_from, u_to)
                if res is not None:
                    self.add_message("Assistant", f"Conversion Result:\n{val} {u_from.upper()} = {res:.2f} {u_to.upper()}")
                    self.search_input.text = ""
                    return
            except Exception:
                pass

        # Topic Keyword Search
        matches = []
        for subject, concepts in KNOWLEDGE.items():
            if isinstance(concepts, dict):
                for concept in concepts.keys():
                    if query in concept.lower():
                        matches.append(f"• {concept.title()} ({subject.title()})")

        if matches:
            results = "\n".join(matches[:5])
            self.add_message("Assistant", f"Matching Topics Found:\n{results}")
        else:
            self.add_message("Assistant", f"No topics matching '{query}'.")

        self.search_input.text = ""

# ============================================================
# APP
# ============================================================

class ScienceAssistantApp(App):
    title = "Science Assistant"

    def build(self):
        Window.clearcolor = LIGHT_THEME["bg"]
        return ScienceAssistantUI()


if __name__ == "__main__":
    ScienceAssistantApp().run()
