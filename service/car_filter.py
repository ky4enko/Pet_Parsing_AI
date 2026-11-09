from app.models import CombustionCar, ElectricCar


class CarFilter:
    """Фільтри для вже отриманих оголошень.

    Загальні критерії (рік і пробіг) застосовуються до обох типів.
    Фільтри пального, об'єму двигуна, КПП та приводу застосовуються
    лише до CombustionCar. ElectricCar ці фільтри пропускає.

    Важливо: цей клас фільтрує локально вже завантажені об'єкти.
    Серверні параметри пошуку формуються в main.py / ria_client.py.
    """

    def __init__(self, cars):
        self.cars = list(cars)

    def _apply_filter(self, check):
        self.cars = [car for car in self.cars if check(car)]
        return self

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return None
        return " ".join(str(value).strip().casefold().replace("ё", "е").split())

    @staticmethod
    def _in_range(value, minimum, maximum):
        return value is not None and minimum <= value <= maximum

    # Загальні фільтри: застосовуються і до ДВС, і до електромобілів.
    def filter_by_year(self, target_year, year_range=3):
        minimum = target_year - year_range
        maximum = target_year + year_range
        return self._apply_filter(
            lambda car: self._in_range(car.year, minimum, maximum)
        )

    def filter_by_mileage(self, target_mileage, mileage_range=50_000):
        minimum = max(0, target_mileage - mileage_range)
        maximum = target_mileage + mileage_range
        return self._apply_filter(
            lambda car: self._in_range(car.mileage_km, minimum, maximum)
        )

    # Наступні фільтри стосуються лише ДВС/дизеля/гібридів.
    # Електромобілі залишаються у вибірці без перевірки цих полів.
    def filter_by_fuel(self, target_fuel):
        target = self._normalize_text(target_fuel)

        def check(car):
            if isinstance(car, ElectricCar):
                return True
            if not isinstance(car, CombustionCar) or not car.fuel_name:
                return False
            actual = self._normalize_text(car.fuel_name.split(",")[0])
            return actual == target

        return self._apply_filter(check)

    def filter_by_engine_volume(self, target_volume, volume_range=0.5):
        minimum = max(0, target_volume - volume_range)
        maximum = target_volume + volume_range

        def check(car):
            if isinstance(car, ElectricCar):
                return True
            if not isinstance(car, CombustionCar):
                return False
            return self._in_range(car.engine_volume_l, minimum, maximum)

        return self._apply_filter(check)

    def filter_by_gearbox(self, target_gearbox):
        target = self._normalize_text(target_gearbox)

        def check(car):
            if isinstance(car, ElectricCar):
                return True
            if not isinstance(car, CombustionCar):
                return False
            return self._normalize_text(car.gearbox) == target

        return self._apply_filter(check)

    def filter_by_drive_type(self, target_drive_type):
        target = self._normalize_text(target_drive_type)

        def check(car):
            if isinstance(car, ElectricCar):
                return True
            if not isinstance(car, CombustionCar):
                return False
            return self._normalize_text(car.drive_type) == target

        return self._apply_filter(check)

    def get_results(self):
        return self.cars

    # Залишаємо сумісність з кодом, де метод називався get_result().
    def get_result(self):
        return self.get_results()
