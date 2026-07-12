from random import randrange, randint, sample, seed
from datetime import date, timedelta

DATE_URI = "<http://www.w3.org/2001/XMLSchema#date>"
XSD_URI = "http://www.w3.org/2001/XMLSchema#"


def _generate_random_date(start_date: date, end_date: date) -> date:
    time_between = end_date - start_date
    all_days = time_between.days

    random_day = randrange(all_days)
    return start_date + timedelta(days=random_day)


def _generate_rating_triples(
    curr_rating: str,
    generated_date: str,
    random_hospital_id: int,
    random_rating: int,
) -> str:
    return_str = f'{curr_rating}\n\t:date "{generated_date}"^^{DATE_URI} ;\n\t'
    return_str += f':hospital_id "hospital_{random_hospital_id}" ;\n\t'
    return_str += f':rating "{random_rating}"^^xsd:integer .\n\n'
    return return_str


def _generate_random_values(
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    count: int | None = None,
) -> tuple[int, int, str | None, str]:
    random_hospital_id = randint(1, hospital_amount)
    random_rating = randint(rating_interval[0], rating_interval[1])
    if count is not None:
        curr_rating = f":rating{count+1}"
    else:
        curr_rating = None
    generated_date = _generate_random_date(dates[0], dates[1]).strftime("%Y-%m-%d")
    return (
        random_hospital_id,
        random_rating,
        curr_rating,
        generated_date,
    )


def generate_random_ratings(
    given_uri: str,
    amount_of_triples: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    delta_amount: int,
) -> tuple[str, str, str, str]:
    """Generates a random amount of ratings for a hospital.

    Args:
        given_uri (str): Given URI to put as base.
        amount_of_triples (int): Amount of triples to generate.
        hospital_amount (int): Amount of possible hospitals.
        rating_interval (tuple[int, int]): Interval of the ratings.
        dates (tuple[date, date]): Interval of possible dates.

    Returns:
        str: RDF string in Turtle format to use.
            First: represents G
            Second: Represents delta_G inserts
            Third: Represents delta_G deletes
    """
    start_str: str = f"PREFIX : <{given_uri}>\n" + f"PREFIX xsd: <{XSD_URI}>\n\n"

    # Build the normal G
    triples_gen: dict[str, tuple[str, int, int]] = {}
    return_str = start_str
    for i in range(amount_of_triples):
        (
            random_hospital_id,
            random_rating,
            curr_rating,
            generated_date,
        ) = _generate_random_values(
            hospital_amount,
            rating_interval,
            dates,
            i,
        )

        if curr_rating is None:
            raise ValueError("Curr_rating can be None.")

        return_str += _generate_rating_triples(
            curr_rating,
            generated_date,
            random_hospital_id,
            random_rating,
        )

        triples_gen[curr_rating] = (
            generated_date,
            random_hospital_id,
            random_rating,
        )

    # Build the deltas
    delta_keys = sample(list(triples_gen.keys()), delta_amount // 2)
    delete_str = start_str
    insert_str = start_str
    for key in delta_keys:
        delete_str += _generate_rating_triples(
            key,
            triples_gen[key][0],
            triples_gen[key][1],
            triples_gen[key][2],
        )
        new_insert_triple_values = _generate_random_values(
            hospital_amount, rating_interval, dates
        )
        insert_str += _generate_rating_triples(
            key,
            new_insert_triple_values[3],
            new_insert_triple_values[0],
            new_insert_triple_values[1],
        )

    # Build nu G
    nu_str = start_str
    for key, item in triples_gen.items():
        if key in delta_keys:
            continue
        nu_str += _generate_rating_triples(
            key,
            item[0],
            item[1],
            item[2],
        )
    for key in delta_keys:
        nu_str += _generate_rating_triples(
            key,
            triples_gen[key][0],
            triples_gen[key][1],
            triples_gen[key][2],
        )

    return (return_str[:-2], delete_str, insert_str, nu_str)


if __name__ == "__main__":
    # seed(13)
    result = generate_random_ratings(
        "http://example/org/we_are/",
        10,
        3,
        (0, 10),
        (date(2025, 12, 1), date(2026, 1, 31)),
        5,
    )
    print(result)
