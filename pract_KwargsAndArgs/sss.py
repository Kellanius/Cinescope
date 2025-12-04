"""def greet(**kwargs):
    print(f"Hello, {kwargs['name']}! You are {kwargs['age']} years old")

greet(name="Ilya", age=27)


def create_dict(**kwargs):
    return kwargs

sas1 = create_dict(s=1,s2=2,s3=3,s4=4,s5=5)

print(sas1)


def update_settings(default_settings, **kwargs):
    for i in kwargs:
        if i in default_settings:
            default_settings[i] = kwargs[i]
        else:
            default_settings[i] = kwargs[i]
    return default_settings



default_settings = {"theme": "light", "notifications": True}
print(update_settings(default_settings, theme="dark", volume=80))
# Вывод: {'theme': 'dark', 'notifications': True, 'volume': 80}



def filter_kwargs(**kwargs):
    filter = {}
    for i in kwargs:
        if kwargs[i] > 10:
            filter[i] = kwargs[i]
    return filter

print(filter_kwargs(s1=2,s2=16,s3=11,s4=100))


# Декоратор
def log_kwargs(func):
    def wrapper(*args, **kwargs):
        print(f'Called with kwargs: {kwargs}')
        return func(*args, **kwargs)
    return wrapper


@log_kwargs
def my_function(a, b, **kwargs):
    return a + b

my_function(5, 10, debug=True, verbose=False)
# Вывод:
# Called with kwargs: {'debug': True, 'verbose': False}"""




def add_numbers(*args):
    total = 0
    for i in args:
        total += i
    return total

print(add_numbers(1,2,3,4,5,1,1,1,2,4,5,))



def create_list(*args):
    list = []
    for i in args:
        list.append(i)
    return list

print(create_list(1,5,"rwr","sas",42))


def print_arg(arg):
    print(arg)

def pass_arguments(*args):
    for arg in args:
        print_arg(arg)

pass_arguments(1,2,3,4,5)


def find_max(*args):
    print(max(args))
find_max(1,-5,52,100,-24213)


def join_strings(*args):
    return " ".join(str(arg) for arg in args)

print(join_strings(1,"Hello", "World", 222))


