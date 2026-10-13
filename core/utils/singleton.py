class Singleton(object):
    """Реализует паттерн Singleton для классов-наследников.

    Повторное создание объекта возвращает существующий экземпляр.
    Инициализацию размещайте в init: метод вызывается при первом создании.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._initialized = False
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self.__class__._initialized:
            self.__class__._initialized = True  # set initial flag to True
            self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        pass
