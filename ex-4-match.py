# only in python 3.10
import sys

text = "hello"

if len(sys.argv) > 1:
    text = sys.argv[1]

match text:
    case "hello":
        print("try supplying arguemnts")
    case _:
        print("argument {text}")
