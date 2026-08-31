import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# LEARNED KNOWLEDGE STORAGE
# ============================================================

# Get the folder where this Python file is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# ANDROID WRITABLE STORAGE
# ------------------------------------------------------------
# On Android, the APK's bundled files should not be used
# for saving new data.
#
# Kivy provides user_data_dir as a writable app directory.
# When running outside an active Kivy app, we use the project
# folder instead.
# ------------------------------------------------------------

try:
    from kivy.app import App

    if App.get_running_app():

        # Android: use Kivy's writable application directory.
        LEARNED_FILE = os.path.join(
            App.get_running_app().user_data_dir,
            "learned_knowledge.json"
        )

    else:

        # Normal Python/desktop testing.
        LEARNED_FILE = os.path.join(
            BASE_DIR,
            "learned_knowledge.json"
        )

except Exception:

    # If Kivy is unavailable, use the project directory.
    LEARNED_FILE = os.path.join(
        BASE_DIR,
        "learned_knowledge.json"
    )

# ============================================================
# FIRST-LAUNCH INITIALIZATION
# ============================================================

def initialize_learned_file():
    """
    Creates the writable learned-knowledge file on first launch.

    The original learned_knowledge.json bundled with the project
    is used as the initial data. After that, new knowledge is
    saved in the writable Android application directory.
    """

    # If the writable file already exists, don't overwrite it.
    if os.path.exists(LEARNED_FILE):
        return

    # Location of the original JSON included with the project.
    source_file = os.path.join(
        BASE_DIR,
        "learned_knowledge.json"
    )

    # If the original file exists, copy its data.
    if os.path.exists(source_file):

        try:

            with open(
                source_file,
                "r",
                encoding="utf-8"
            ) as source:

                data = json.load(source)

            # Save the initial data to the writable location.
            save_learned(data)

        except (json.JSONDecodeError, OSError):

            # If the original file cannot be read,
            # start with an empty knowledge database.
            save_learned({})

    else:

        # No initial file exists, so start empty.
        save_learned({})

VALID_SUBJECTS = {
    "mathematics": "mathematics",
    "math": "mathematics",

    "physics": "physics",

    "chemistry": "chemistry",

    "computer science": "computer science",
    "computer": "computer science",

    "english grammar": "english grammar",
    "english": "english grammar"
}


def load_learned():
    if not os.path.exists(LEARNED_FILE):
        return {}

    try:
        with open(
            LEARNED_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_learned(data):

    with open(
        LEARNED_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def normalize_subject(subject):

    subject = subject.strip().lower()

    return VALID_SUBJECTS.get(subject)


def add_topic(subject, concept, topic):

    data = load_learned()

    subject = normalize_subject(subject)

    if not subject:
        return False

    concept = concept.strip().lower()

    data.setdefault(subject, {})

    data[subject][concept] = topic

    save_learned(data)

    return True


def update_topic(
    subject,
    concept,
    field,
    value,
    existing_topic=None
):

    data = load_learned()

    subject = normalize_subject(subject)

    if not subject:
        return False

    concept = concept.strip().lower()

    # Create the subject if it does not exist
    if subject not in data:
        data[subject] = {}

    # If the topic isn't in learned knowledge yet,
    # copy the existing built-in topic first.
    if concept not in data[subject]:

        if existing_topic is not None:

            if isinstance(existing_topic, dict):

                data[subject][concept] = dict(
                    existing_topic
                )

            else:

                data[subject][concept] = {
                    "definition": existing_topic
                }

        else:
            return False

    # Make sure the topic is a dictionary
    if not isinstance(
        data[subject][concept],
        dict
    ):

        data[subject][concept] = {
            "definition": data[subject][concept]
        }

    # Add or update the requested information
    data[subject][concept][field] = value

    # Save permanently
    save_learned(data)

    return True


def get_all_knowledge():

    return load_learned()
