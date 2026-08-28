import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEARNED_FILE = os.path.join(BASE_DIR, "learned_knowledge.json")


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
