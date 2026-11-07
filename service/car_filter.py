class CarFilter:
    def __init__(self, cars):
        self.cars = cars

    def filter_by_year(self, target_year, year_range=3):
        min_year = target_year - year_range
        max_year = target_year + year_range
        self.cars = [car for car in self.cars
                if car.year is not None and min_year <= car.year <= max_year]
        return self

    def filter_by_mileage(self, target_mileage, mileage_range=50_000):
        min_mileage = target_mileage - mileage_range
        max_mileage = target_mileage + mileage_range
        self.cars = [car for car in self.cars
                if car.mileage_km is not None and min_mileage <= car.mileage_km <= max_mileage]
        return self

    def filter_by_fuel(self, target_fuel):
        self.cars = [car for car in self.cars
                if car.fuel_name is not None and car.fuel_name.split(",")[0].strip().lower()
                == target_fuel.lower()]
        return self

    def filter_by_engine_volume(self, target_volume, volume_range=0.5):
        min_engine_volume = target_volume - volume_range
        max_engine_volume = target_volume + volume_range
        self.cars = [car for car in self.cars
                if car.engine_volume_l is not None and min_engine_volume <= car.engine_volume_l <= max_engine_volume]
        return self

    def filter_by_gearbox(self, target_gearbox):
        self.cars = [car for car in self.cars
                if car.gearbox is not None and car.gearbox.strip().lower() == target_gearbox.strip().lower()]
        return self

    def filter_by_drive_type(self, target_drive_type):
        self.cars = [car for car in self.cars
                if car.drive_type is not None and car.drive_type.strip().lower() == target_drive_type.strip().lower()]
        return self

    def filter_by_battery(self, target_battery, battery_range=10):
        min_battery = target_battery - battery_range
        max_battery = target_battery + battery_range
        self.cars = [car for car in self.cars
                if car.battery_capacity_kwh is not None and min_battery <= car.battery_capacity_kwh <= max_battery]
        return self

    def filter_by_modification(self, target_modification):
        self.cars = [car for car in self.cars
                if car.modification_name is not None and car.modification_name.strip().lower()
                     == target_modification.strip().lower()]
        return self

    def get_results(self):
        return self.cars