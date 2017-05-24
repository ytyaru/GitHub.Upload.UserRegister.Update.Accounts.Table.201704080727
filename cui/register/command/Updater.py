#!python3
#encoding:utf-8
import os.path
import subprocess
import shlex
import re
import datetime
import traceback
import copy
import dataset
import database.src.Database
import web.service.github.api.v3.CurrentUser
import cui.register.github.api.v3.authorizations.Authorizations
import cui.register.github.api.v3.users.SshKeys
import cui.register.github.api.v3.users.Emails
import cui.register.github.api.v3.users.Users
import web.sqlite.Json2Sqlite
import cui.register.SshConfigurator
class Updater:
    def __init__(self):
        self.__j2s = web.sqlite.Json2Sqlite.Json2Sqlite()
        self.__db = None

    def Update(self, args):
        print('Account.Update')
        print(args)
        print('-u: {0}'.format(args.username))
        print('-rn: {0}'.format(args.rename))
        print('-p: {0}'.format(args.password))
        print('-m: {0}'.format(args.mailaddress))
        print('-s: {0}'.format(args.ssh_host))
        print('-t: {0}'.format(args.two_factor_secret_key))
        print('-r: {0}'.format(args.two_factor_recovery_code_file_path))
        print('--auto: {0}'.format(args.auto))

        self.__db = database.src.Database.Database()
        self.__db.Initialize()
        
        account = self.__db.account['Accounts'].find_one(Username=args.username)
        print(account)
        
        if None is account:
            print('指定したユーザ {0} がDBに存在しません。更新を中止します。'.format(args.username))
            return
        
        # Accountsテーブルを更新する（ユーザ名、パスワード、メールアドレス）
        self.__UpdateAccounts(args, account)
        
        # D. SSH鍵を更新する(APIの削除と新規作成で。ローカルで更新し~/.ssh/configで設定済みとする)
        
        # 未実装は以下。
        # E. 2FA-Secret
        # F. 2FA-Recovery-Code
        
        # 作成したアカウントのリポジトリDB作成や、作成にTokenが必要なライセンスDBの作成
        self.__db.Initialize()
        return self.__db

    def __UpdateAccounts(self, args, account):
        new_account = copy.deepcopy(account)
        # ユーザ名とパスワードを変更する
        if None is not args.rename or None is not args.password:
            j_user = self.__IsValidUsernameAndPassword(args, account)
            if None is not args.rename:
                new_account['Username'] = args.rename
            if None is not args.password:
                new_account['Password'] = args.password
            new_account['CreatedAt'] = j_user['created_at']
            new_account['UpdatedAt'] = j_user['updated_at']
        # メールアドレスを更新する
        if args.mailaddress:
            user = web.service.github.api.v3.CurrentUser.CurrentUser(self.__db, account['Username'])
            token = user.GetAccessToken(scopes=['user', 'user:email'])
            mail = self.__GetPrimaryMail(token)
            if mail != account['MailAddress']:
                new_account['MailAddress'] = self.__GetPrimaryMail(token)
            else:
                print('MailAddressはDBと同一でした。: {0}'.format(mail))
        # DBを更新する
        self.__db.account['Accounts'].update(new_account, ['Id'])
    
    def __IsValidUsernameAndPassword(self, args, account):
        if None is args.password:
            password = account['Password']
        else:
            password = args.password
        print('password: ' + password)
        users = cui.register.github.api.v3.users.Users.Users(args.username, password)
        try:
            j = users.Get()
            account['CreatedAt'] = j['created_at']
        except:
            raise Exception('指定したユーザ名とパスワードでAPI実行しましたがエラーです。有効なユーザ名とパスワードではない可能性があります。')
            return None
        return j

    def __GetPrimaryMail(self, token):
        emails = cui.register.github.api.v3.users.Emails.Emails()
        mails = emails.Gets(token)
        print(mails)
        for mail in mails:
            if mail['primary']:
                return mail['email']

