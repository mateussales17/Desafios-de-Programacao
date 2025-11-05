
class computed_property:
    def __init__(self, *dependencies):
        self.dependencies = dependencies
        self.func_get = None
        self.func_set = None
        self.func_del = None

    def __call__(self, func):
        self.func_get = func
        self.cached = f'cached_{func.__name__}'
        self.dependencies_name = f'dependencies_{func.__name__}'
        return self

    def __get__(self, instance, owner=None):
        # Se nao tem cache, calcula e salva os valores das dependencias
        if not hasattr(instance, self.cached):
            value = self.func_get(instance)
            setattr(instance, self.cached, value)
            # Ignora dependencias que nao existem
            setattr(instance, self.dependencies_name, {
                d: getattr(instance, d) for d in self.dependencies if hasattr(instance, d)
            })
            return value

        # Verifica se alguma dependencia mudou
        cached_dependencies = getattr(instance, self.dependencies_name)
        for dep in self.dependencies:
            # Ignora dependencias que nao existem
            if hasattr(instance, dep):
                if getattr(instance, dep) != cached_dependencies[dep]:
                    value = self.func_get(instance)
                    setattr(instance, self.cached, value)
                    setattr(instance, self.dependencies_name, {
                        d: getattr(instance, d) for d in self.dependencies if hasattr(instance, d)
                    })
                    return value

        return getattr(instance, self.cached)

    def setter(self, func):
        self.func_set = func
        return self

    def deleter(self, func):
        self.func_del = func
        return self

    def __set__(self, instance, value):
        self.func_set(instance, value)
        if hasattr(instance, self.cached):
            delattr(instance, self.cached)
        if hasattr(instance, self.dependencies_name):
            delattr(instance, self.dependencies_name)

    def __delete__(self, instance):
        self.func_del(instance)
        if hasattr(instance, self.cached):
            delattr(instance, self.cached)
        if hasattr(instance, self.dependencies_name):
            delattr(instance, self.dependencies_name)
