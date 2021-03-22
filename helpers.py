# Возвращает список дней за последнюю неделю с заданного дня
def weekdays(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    i = days.index(day) + 1
    d1 = list(reversed(days[:i]))
    d1.extend(list(reversed(days[i:])))
    return d1
