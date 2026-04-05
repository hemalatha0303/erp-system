from datetime import date


def year_from_batch(batch: str) -> int:
    try:
        if batch and "-" in str(batch):
            start_year = int(str(batch).split("-")[0])
            current_year = date.today().year
            year = min(current_year - start_year + 1, 4)
            return max(year, 1)
    except Exception:
        pass
    return 1


def year_from_semester(semester: int) -> int:
    try:
        sem = int(semester)
        year = (sem + 1) // 2
        if year < 1:
            return 1
        if year > 4:
            return 4
        return year
    except Exception:
        return 1


def resolve_year(batch: str = None, semester: int = None, year: int = None) -> int:
    if year is not None:
        try:
            return int(year)
        except Exception:
            pass
    if batch:
        return year_from_batch(batch)
    if semester is not None:
        return year_from_semester(semester)
    return 1
