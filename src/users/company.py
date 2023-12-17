from src.connections import RedisConnection


class CompanyMetrics:
    def __init__(self, metrics_ref: str):        
        self._metrics_ref = metrics_ref
        self._employees_ref = f"{metrics_ref}:employees"
        self._vacancies_ref = f"{metrics_ref}:vacancies"
        self.num_employees: (int | None) = None
        self.num_vacancies: (int | None) = None


    # Returns True if update was successful, False if failed to query any of the metrics 
    def update(self, redis_connection: RedisConnection) -> bool:
        try:
            self.num_employees = int(redis_connection.get(self._employees_ref))
            self.num_vacancies = int(redis_connection.get(self._vacancies_ref))
        except TypeError:
            return False
        return True


    def create_metrics(self, redis_connection: RedisConnection, employees_count: int, vacancies_count: int) -> None:
        redis_connection.set(self._employees_ref, employees_count)
        redis_connection.set(self._vacancies_ref, vacancies_count)
        self.update(redis_connection)


class Company:
    def __init__(self, company_id: int, name: str):
        self._id: int = company_id
        self._redis_metrics_ref = f"company:{company_id}"
        self.metrics = CompanyMetrics(self._redis_metrics_ref)
        self.name = name


    def get_id(self) -> int:
        return self._id


    def update_metrics(self, redis_connection: RedisConnection):
        assert self.metrics is not None
        self.metrics.update(redis_connection)