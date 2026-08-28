from knowledge import KNOWLEDGE
from learning import (
    get_all_knowledge,
    add_topic,
    update_topic
)


print("================================")
print("       SCIENCE ASSISTANT")
print("================================")
print("Subjects: Mathematics, Physics,")
print("Computer Science, Chemistry,")
print("English Grammar")
print("Type 'exit' to stop.")
print()


# =================================================
# LOAD PERMANENTLY LEARNED KNOWLEDGE
# =================================================

LEARNED = get_all_knowledge()

for subject, concepts in LEARNED.items():

    if subject not in KNOWLEDGE:
        KNOWLEDGE[subject] = {}

    KNOWLEDGE[subject].update(concepts)


# =================================================
# CURRENT CONVERSATION CONTEXT
# =================================================

current_topic = None
current_subject = None
current_data = None


# =================================================
# FIND TOPIC
# =================================================

def find_topic(question):

    q = question.lower().strip()

    # Remove punctuation
    clean = q.replace("?", "")
    clean = clean.replace(".", "")
    clean = clean.replace("!", "")
    clean = clean.replace(",", "")

    matches = []

    for subject, concepts in KNOWLEDGE.items():

        for concept, data in concepts.items():

            concept_lower = concept.lower()

            # Exact topic
            if concept_lower == clean:

                matches.append(
                    (
                        len(concept_lower),
                        subject,
                        concept,
                        data
                    )
                )

            # Topic inside a question
            elif concept_lower in clean:

                matches.append(
                    (
                        len(concept_lower),
                        subject,
                        concept,
                        data
                    )
                )

    if matches:

        # Longest matching topic wins
        matches.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return matches[0]

    return None


# =================================================
# UNDERSTAND QUESTION TYPE
# =================================================

def get_request_type(question):

    q = question.lower().strip()

    # Remove punctuation
    q = q.replace("?", "")
    q = q.replace(".", "")
    q = q.replace("!", "")

    # ---------------------------------------------
    # FORMULA
    # ---------------------------------------------

    if (
        q == "formula"
        or "what is the formula" in q
        or "what is its formula" in q
        or "tell me the formula" in q
        or "give me the formula" in q
        or "show me the formula" in q
        or "what is the equation" in q
        or "tell me the equation" in q
    ):

        return "formula"


    # ---------------------------------------------
    # EXAMPLES
    # ---------------------------------------------

    if (
        q == "example"
        or q == "examples"
        or "for example" in q
        or "give an example" in q
        or "give me an example" in q
        or "give some examples" in q
        or "show an example" in q
        or "show me an example" in q
        or "show some examples" in q
        or "can you give an example" in q
        or "can you give me an example" in q
        or "can you show an example" in q
        or "can you show me an example" in q
    ):

        return "examples"


    # ---------------------------------------------
    # SIMPLE EXPLANATION
    # ---------------------------------------------

    if (
        q == "simple"
        or q == "simply"
        or q == "explain"
        or q == "explain simply"
        or q == "explain it simply"
        or "explain in simple words" in q
        or "explain in easy words" in q
        or "easy explanation" in q
        or "simple explanation" in q
        or "explain this" in q
        or "can you explain" in q
    ):

        return "simple"


    # ---------------------------------------------
    # PROPERTIES
    # ---------------------------------------------

    if (
        q == "property"
        or q == "properties"
        or q == "characteristic"
        or q == "characteristics"
        or "important properties" in q
        or "what are its properties" in q
        or "what are the properties" in q
        or "tell me its properties" in q
    ):

        return "properties"


    # ---------------------------------------------
    # APPLICATIONS / USES
    # ---------------------------------------------

    if (
        q == "use"
        or q == "uses"
        or q == "application"
        or q == "applications"
        or "what is it used for" in q
        or "what are its uses" in q
        or "where is it used" in q
        or "where is this used" in q
        or "tell me its uses" in q
        or "tell me the applications" in q
        or "applications of" in q
    ):

        return "applications"


    return None


# =================================================
# DISPLAY ANSWER
# =================================================

def display_answer(
    subject,
    topic,
    data,
    request_type=None
):

    print()
    print("Subject:", subject.title())
    print("Topic:", topic.title())

    if isinstance(data, dict):

        # Specific request
        if request_type:

            value = data.get(request_type)

            if value:

                if request_type == "formula":

                    print("Formula:", value)

                elif request_type == "examples":

                    print("Examples:", value)

                elif request_type == "properties":

                    print("Properties:", value)

                elif request_type == "applications":

                    print("Applications:", value)

                else:

                    print("Answer:", value)

                print()
                return True

        # Normal topic question
        if data.get("definition"):

            print(
                "Answer:",
                data["definition"]
            )

        elif data.get("answer"):

            print(
                "Answer:",
                data["answer"]
            )

        else:

            print(
                "I don't have an answer for this yet."
            )

    else:

        print("Answer:", data)

    print()

    return False


# =================================================
# TEACH MISSING PART OF EXISTING TOPIC
# =================================================

def teach_missing_part(
    subject,
    concept,
    field
):

    labels = {

        "simple":
            "Simple explanation",

        "formula":
            "Formula",

        "examples":
            "Examples",

        "properties":
            "Important properties",

        "applications":
            "Applications/uses"
    }

    label = labels[field]

    print()

    print(
        "I know the topic '" +
        concept.title() +
        "' but I don't have " +
        label.lower() +
        " yet."
    )

    teach = input(
        "Would you like to teach me? (yes/no): "
    ).strip().lower()

    if teach not in ("yes", "y"):

        print("Okay.")
        print()

        return


    value = input(
        label + ": "
    ).strip()

    if not value:

        print("Nothing was saved.")
        print()

        return


    success = update_topic(
        subject,
        concept,
        field,
        value,
        existing_topic=KNOWLEDGE[
            subject
        ][concept]
    )


    if success:

        KNOWLEDGE[
            subject
        ][concept][field] = value

        print()

        print(
            "✓ Added",
            field,
            "to",
            concept
        )

        print("✓ Saved permanently.")
        print()

    else:

        print()
        print("Could not update the topic.")
        print()


# =================================================
# TEACH A COMPLETELY NEW TOPIC
# =================================================

def teach_topic(concept):

    print()

    print(
        "Let's teach me about:",
        concept
    )

    print()


    definition = input(
        "1. Definition (What is it?): "
    ).strip()


    simple = input(
        "2. Simple explanation: "
    ).strip()


    formula = input(
        "3. Formula (or type 'none'): "
    ).strip()


    examples = input(
        "4. Examples: "
    ).strip()


    properties = input(
        "5. Important properties: "
    ).strip()


    applications = input(
        "6. Applications/uses: "
    ).strip()


    print()

    print("Choose the subject:")

    subject = input(
        "Subject: "
    ).strip().lower()


    topic = {

        "definition":
            definition,

        "simple":
            simple,

        "formula":
            (
                ""
                if formula.lower() == "none"
                else formula
            ),

        "examples":
            examples,

        "properties":
            properties,

        "applications":
            applications
    }


    if add_topic(
        subject,
        concept,
        topic
    ):

        KNOWLEDGE.setdefault(
            subject,
            {}
        )

        KNOWLEDGE[
            subject
        ][concept] = topic


        print()

        print(
            "✓ Topic learned:",
            concept
        )

        print(
            "✓ Structured knowledge saved permanently."
        )

        print()

    else:

        print()
        print("Invalid subject.")
        print()

        print(
            "Use one of:"
        )

        print("mathematics")
        print("physics")
        print("chemistry")
        print("computer science")
        print("english grammar")

        print()


# =================================================
# MAIN LOOP
# =================================================

while True:

    question = input(
        "You: "
    ).strip().lower()


    # ---------------------------------------------
    # EXIT
    # ---------------------------------------------

    if question == "exit":

        print("Goodbye!")

        break


    # ---------------------------------------------
    # QUESTION TYPE
    # ---------------------------------------------

    request_type = get_request_type(
        question
    )


    # ---------------------------------------------
    # FIND TOPIC IN THE QUESTION
    # ---------------------------------------------

    result = find_topic(
        question
    )


    # ---------------------------------------------
    # TOPIC + REQUEST IN SAME QUESTION
    # ---------------------------------------------

    if result and request_type:

        _, subject, concept, data = result

        current_subject = subject
        current_topic = concept
        current_data = data


        if isinstance(data, dict):

            if data.get(request_type):

                display_answer(
                    subject,
                    concept,
                    data,
                    request_type
                )

            else:

                teach_missing_part(
                    subject,
                    concept,
                    request_type
                )

                current_data = KNOWLEDGE[
                    subject
                ][concept]

        continue


    # ---------------------------------------------
    # SHORT QUESTION ABOUT CURRENT TOPIC
    # ---------------------------------------------

    if (
        current_topic
        and current_subject
        and current_data
        and request_type
        and not result
    ):

        if isinstance(
            current_data,
            dict
        ):

            if current_data.get(
                request_type
            ):

                display_answer(
                    current_subject,
                    current_topic,
                    current_data,
                    request_type
                )

            else:

                teach_missing_part(
                    current_subject,
                    current_topic,
                    request_type
                )

                current_data = KNOWLEDGE[
                    current_subject
                ][current_topic]

        continue


    # ---------------------------------------------
    # NORMAL TOPIC
    # ---------------------------------------------

    if result:

        _, subject, concept, data = result

        current_subject = subject
        current_topic = concept
        current_data = data


        display_answer(
            subject,
            concept,
            data
        )

        continue


    # ---------------------------------------------
    # UNKNOWN TOPIC
    # ---------------------------------------------

    print()

    print(
        "I don't know this topic yet."
    )


    teach = input(
        "Would you like to teach me? (yes/no): "
    ).strip().lower()


    if teach in ("yes", "y"):

        concept = input(
            "Topic name: "
        ).strip().lower()


        if concept == "cancel":

            print(
                "Learning cancelled."
            )

            print()

            continue


        if not concept:

            concept = question


        teach_topic(
            concept
        )


    else:

        print(
            "Okay. We can teach me later."
        )

        print()
