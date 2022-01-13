import callback
def func(t,tp):
    print("call back func")
    print(t,tp)

callback.temp=100
callback.func_call(func)
