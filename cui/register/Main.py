#!python3
#encoding:utf-8
import cui.register.command.Inserter
import cui.register.command.Deleter
import cui.register.command.Updater
class Main:
    def __init__(self, path_dir_db):
        self.path_dir_db = path_dir_db

    def Insert(self, args):
        inserter = cui.register.command.Inserter.Inserter()
        return inserter.Insert(args)

    def Update(self, args):
        updater = cui.register.command.Updater.Updater()
        return updater.Update(args)

    def Delete(self, args):
        deleter = cui.register.command.Deleter.Deleter()
        deleter.Delete(args)

