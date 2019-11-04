import traceback as tb

try:
    with open('DB') as f:
        DB = yaml.load(f, Loader=yaml.FullLoader)
except Exception as e:
    print(e)
    tb.print_exc()
    DB = {'pool': []}