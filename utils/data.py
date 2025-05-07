import json


def get_films(
   file_path: str = "data.json", film_id: int | None = None
) -> list[dict] | dict:
   with open(file_path, "r") as fp:
       films = json.load(fp)
       if film_id != None and film_id < len(films):
           return films[film_id]
       return films


def add_film(
   film: dict,
   file_path: str = "data.json",
):
   films = get_films(file_path=file_path, film_id=None)
   if films:
       films.append(film)
       with open(file_path, "w") as fp:
           json.dump(
               films,
               fp,
               indent=4,
               ensure_ascii=False,
           )

def delete_film_by_name(name: str, file_path: str = "data.json") -> bool:
    films = get_films(file_path=file_path)
    updated_films = [film for film in films if film.get("name") != name]
    
    if len(films) == len(updated_films):
        return False  # нічого не видалено, бо не знайдено
    
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(updated_films, fp, indent=4, ensure_ascii=False)
    
    return True  # фільм було видалено

def update_film_description(name: str, new_description: str, file_path: str = "data.json") -> bool:
    films = get_films(file_path=file_path)
    found = False

    for film in films:
        if film.get("name") == name:
            film["description"] = new_description
            found = True
            break

    if not found:
        return False  # фільм не знайдено

    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(films, fp, indent=4, ensure_ascii=False)

    return True  # опис оновлено

def update_film_rating(name: str, new_rating: float, file_path: str = "data.json") -> bool:
    films = get_films(file_path=file_path)
    found = False

    for film in films:
        if film.get("name") == name:
            film["rating"] = new_rating
            found = True
            break

    if not found:
        return False  # фільм не знайдено

    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(films, fp, indent=4, ensure_ascii=False)

    return True  # опис оновлено