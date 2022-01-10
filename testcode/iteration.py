def plus(i):
    print("==1==")
    print(i)
    if i == 0:
        return 0
    print("==2==")
    return i + plus(i - 1)


a = plus(3)

print(a)
