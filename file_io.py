
class Environment:
    def __init__(self, f, env):
        self.f = f
        self.env = env

    def __enter__(self):
        self.f.write('\\begin{{{}}}\n'.format(self.env))

    def __exit__(self, exc_type, exc_value, tb):
        self.f.write('\\end{{{}}}\n'.format(self.env))


def get_writer(f):
    return lambda s='', end='\n': print(s, file=f, end=end)


def write_ingredients(ingredients, f):
    write = get_writer(f)

    if ingredients['name'] or ingredients['name']:
        write('\\ingredientpart{{{}}}'.format(ingredients['name']))

    with Environment(f, 'ingredients') as e:
        for ingredient in ingredients['list']:
            write('\t\\ingredient {}'.format(ingredient))

    write()


def write_steps(steps, f):
    write = get_writer(f)

    if steps['name'] or steps['name']:
        write('\\steppart{{{}}}'.format(steps['name']))

    with Environment(f, 'steps') as e:
        for step in steps['list']:
            write('\t\\step {}'.format(step))

    write()
