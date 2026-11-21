"""Kenyan calendar features. APPROXIMATE: verify against the official gazette and ministry term dates, then edit here.
Movable Islamic holidays (Idd) are not listed; add them when confirmed."""
import datetime as dt
D = dt.date
HOLIDAYS = {D(2025, 1, 1), D(2025, 3, 31), D(2025, 4, 18), D(2025, 4, 21), D(2025, 5, 1), D(2025, 6, 2), D(2025, 10, 10),
            D(2025, 10, 20), D(2025, 12, 12), D(2025, 12, 25), D(2025, 12, 26), D(2026, 1, 1), D(2026, 4, 3), D(2026, 4, 6),
            D(2026, 5, 1), D(2026, 6, 1), D(2026, 10, 20), D(2026, 12, 25)}
TERMS = [(D(2025, 1, 6), D(2025, 4, 4)), (D(2025, 4, 28), D(2025, 8, 1)), (D(2025, 8, 25), D(2025, 10, 31)),
         (D(2026, 1, 5), D(2026, 4, 3)), (D(2026, 4, 27), D(2026, 8, 7)), (D(2026, 8, 31), D(2026, 10, 30))]
is_holiday = lambda d: d in HOLIDAYS
school_open = lambda d: d.weekday() < 5 and any(a <= d <= b for a, b in TERMS)

def day_context(date=None, dow=None, rain=0, holiday=None, school=None):
    """Turn a date (or a day number, Sun=0..Sat=6) into the model's day features."""
    if date is not None:
        dow = (date.weekday() + 1) % 7
        holiday = is_holiday(date) if holiday is None else holiday
        school = school_open(date) if school is None else school
    dow = 5 if dow is None else dow
    if dow not in range(7): raise ValueError("dow must be 0 (Sunday) to 6 (Saturday)")
    return dict(dow=int(dow), rain=int(bool(rain)), holiday=int(bool(holiday)), school=int(True if school is None else school))
