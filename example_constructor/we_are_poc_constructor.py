from random import randrange, randint
from datetime import date, timedelta

DATE_URI = "<http://www.w3.org/2001/XMLSchema#date>"
XSD_URI = "<http://www.w3.org/2001/XMLSchema#>"


def _generate_random_date(
    start_date: date, end_date: date
) -> date:
    time_between = end_date - start_date
    all_days = time_between.days

    random_day = randrange(all_days)
    return start_date + timedelta(days=random_day)


def generate_random_ratings(
    given_uri: str,
    amount_of_triples: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
) -> str:
    """Generates a random amount of ratings for a hospital.

    Args:
        given_uri (str): Given URI to put as base.
        amount_of_triples (int): Amount of triples to generate.
        hospital_amount (int): Amount of possible hospitals.
        rating_interval (tuple[int, int]): Interval of the ratings.
        dates (tuple[date, date]): Interval of possible dates.

    Returns:
        str: RDF string in Turtle format to use.
    """
    return_str: str = (
        f"PREFIX : {given_uri}\n"
        + f"PREFIX xsd: {XSD_URI}\n\n"
    )

    for i in range(amount_of_triples):
        random_hospital_id = randint(1, hospital_amount)
        random_rating = randint(
            rating_interval[0], rating_interval[1]
        )

        return_str += (
            f":rating{i+1} :date "
            + _generate_random_date(
                dates[0], dates[1]
            ).strftime("%Y-%m-%d")
            + f"^^{DATE_URI} ;\n\t"
        )
        return_str += f":hospital_id hospital_{random_hospital_id} ;\n\t"
        return_str += f':rating "{random_rating}"^^{XSD_URI}:integer .\n\n'

    return return_str[:-2]


if __name__ == "__main__":
    result = generate_random_ratings(
        "http://example/org/we_are/",
        10,
        3,
        (0, 10),
        (date(2025, 12, 1), date(2026, 1, 31)),
    )
    print(result)
