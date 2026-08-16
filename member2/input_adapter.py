import json


REQUIRED_FIELDS = [
    "job_id",
    "topic",
    "domain",
    "domain_confidence"
]


def load_member1_input(filename: str):

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    for field in REQUIRED_FIELDS:

        if field not in data:

            raise ValueError(
                f"Missing required field: {field}"
            )

    if not data["topic"].strip():

        raise ValueError(
            "Topic cannot be empty"
        )

    if not data["domain"].strip():

        raise ValueError(
            "Domain cannot be empty"
        )

    confidence = data["domain_confidence"]

    if not 0 <= confidence <= 1:

        raise ValueError(
            "Domain confidence must be between 0 and 1"
        )

    return data