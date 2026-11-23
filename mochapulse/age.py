"""Render the account age shown in the card's "Uptime" row."""
import datetime

from dateutil import relativedelta


def plural_suffix(quantity):
    """Return ``"s"`` when *quantity* is not exactly one, else ``""``.

    :param int quantity: The count a unit noun describes.
    :return: Plural suffix for the unit noun.
    :rtype: str
    """
    return "s" if quantity != 1 else ""


def format_age(birthday):
    """Build a years/months/days age string relative to today.

    Appends a birthday cake emoji when today is the anniversary of *birthday*
    (same month and day).

    :param datetime.datetime birthday: The reference birth date.
    :return: e.g. ``"24 years, 3 months, 14 days"`` (optionally with cake).
    :rtype: str
    """
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    is_anniversary = diff.months == 0 and diff.days == 0
    return "{} {}, {} {}, {} {}{}".format(
        diff.years, "year" + plural_suffix(diff.years),
        diff.months, "month" + plural_suffix(diff.months),
        diff.days, "day" + plural_suffix(diff.days),
        " 🎂" if is_anniversary else "")
