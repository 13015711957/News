
from info import creat_app,db,models
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app=creat_app("develop")

#创建manager对象，管理APP
manager=Manager(app)

#使用Migrate管理app,db
Migrate(app,db)

#给manager添加一条操作命令
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()