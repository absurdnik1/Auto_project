import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
from django.core.files.base import ContentFile
from .models import Auto, Engine, Transmission  # замените на своё приложение

# Маппинг значений Дром → Django
transmission_map = {"АКПП": "0", "механика": "1"}
drive_map = {"передний": "0", "задний": "1", "полный": "2"}
fuel_map = {"бензин": "бензин", "дизель": "дизель", "электро": "электро"}

def unique_slug(title, year):
    base_slug = slugify(f"{title}-{year}")
    slug = base_slug
    counter = 1
    while Auto.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def safe_int(value):
    value = ''.join(filter(str.isdigit, value))
    return int(value) if value else 0

def parse_ford_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    autos = []

    for item in soup.find_all("div", {"data-ftid": "bulls-list_bull"}):
        link_tag = item.find("a", {"data-ftid": "bull_title"})
        if not link_tag:
            continue
        auto_url = link_tag['href']

        if Auto.objects.filter(url=auto_url).exists():
            continue

        title_text = link_tag.text.strip()
        if ',' in title_text:
            title_name, year = title_text.rsplit(',', 1)
            year = safe_int(year)
        else:
            title_name = title_text
            year = 2000

        slug = unique_slug(title_name, year)

        # Фото
        img_tag = item.find("img")
        img_url = img_tag['src'] if img_tag else None

        # Характеристики
        specs = [span.text.strip() for span in item.find_all("span", {"data-ftid": "bull_description-item"})]
        engine_title = specs[0].split('(')[0].strip() if len(specs) > 0 else "Unknown"
        engine_power = 0
        if len(specs) > 0 and '(' in specs[0]:
            try:
                power_str = specs[0].split('(')[1].split('л.с.)')[0]
                engine_power = safe_int(power_str)
            except Exception:
                engine_power = 0

        fuel_type = fuel_map.get(specs[1], "бензин") if len(specs) > 1 else "бензин"
        transmission_type = transmission_map.get(specs[2], "0") if len(specs) > 2 else "0"
        raw_drive = specs[3].lower() if len(specs) > 3 else ""
        if "передн" in raw_drive:
            drive = "0"
        elif "задн" in raw_drive:
            drive = "1"
        elif "полн" in raw_drive or "4wd" in raw_drive or "awd" in raw_drive:
            drive = "2"
        else:
            drive = "0"  # дефолт
        #drive = drive_map.get(specs[3], "0") if len(specs) > 3 else "0"
        mileage = safe_int(specs[4]) if len(specs) > 4 else 0

        # Цена
        price_tag = item.find("span", {"data-ftid": "bull_price"})
        price = safe_int(price_tag.text) if price_tag else 0

        # Engine и Transmission
        engine, _ = Engine.objects.get_or_create(title=engine_title, defaults={"power": engine_power})
        transmission, _ = Transmission.objects.get_or_create(
            transmission_type=transmission_type,
            defaults={"title": specs[2] if len(specs) > 2 else "Unknown"}
        )

        # Создание авто без картинки сначала
        safety_rating_default = Auto.safety_ratings[0][0]
        auto = Auto(
            title=title_name,
            slug=slug,
            category=None,
            engine=engine,
            transmission=transmission,
            drive=drive,
            fuel_type=fuel_type,
            production_year=year,
            trunk_capacity=300,
            wheel_size=15,
            numbers_of_seats=5,
            fuel_tank_capacity=50,
            color="#000000",
            weight=1000,
            safety_rating=safety_rating_default,
            price=price,
            mileage=mileage,
            url=auto_url
        )

        # Скачиваем и сохраняем изображение
        if img_url:
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    auto.save()
                    auto.image.save(f"{slug}.jpg", ContentFile(response.content), save=True)
                    autos.append(auto)
            except Exception as e:
                print(f"Не удалось скачать изображение: {img_url}, ошибка: {e}")

    return autos

# Пример использования
# url = "https://auto.drom.ru/ford/"
# autos = parse_ford_page(url)
# print(f"Создано {len(autos)} автомобилей с фото, ценой, пробегом и URL")
