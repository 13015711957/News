
from flask import Flask,session
from info import creat_app
app=creat_app("develop")


if __name__ == '__main__':
    app.run()