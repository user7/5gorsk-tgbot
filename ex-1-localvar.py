def go():
    with open('token.txt') as f:
        token = f.readline().rstrip()
    print("token = " + token + "\n")

go()
