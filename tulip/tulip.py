# -*- encoding: utf-8 -*-

"""
reach to author : mima@fiftypercent-magazine.org
git : https://github.com/fiftypercent-mima/tulip

Copyright (c) 2020 Mima Kang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import sqlite3
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import json
from datetime import datetime
from shutil import copyfile

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_JSON = ROOT_PATH + '/config.json'

# Font colors (v = violet, b = blue, g = green, y = yellow, r = red, e = end)
colors = {'v': f'\033[95m', 'b': f'\033[94m', 'g': f'\033[92m',
          'y': f'\033[93m', 'r': f'\033[91m', 'B': f'\033[1m',
          'u': f'\033[4m', 'e': '\033[0m'}

fmt = {'ls_title': colors['b'] + '|{0:_^30}|' + colors['e'],
       'ls_content': '|{0:^30}|',

       'ov_title': colors['v'] + '|{0:_^62}|' + colors['e'],
       'ov_row_0': colors['v'] + colors['u']
                   + '|{0:^20}|{1:^25}|{2:^7}|{3:^7}|' + colors['e'],
       'ov_content_u': colors['u'] + '|{0:<20}|{1:>25}|{2:>7}|{3:^7}|'
                       + colors['e'],
       'ov_content': '|{0:<20}|{1:<25.25}|{2:<7}|{3:^7}|',

       'ok': colors['b'] + '[*]{}' + colors['e'],
       'fail': colors['r'] + '[!]{}' + colors['e'],
       'q': colors['y'] + '[?]{}' + colors['e'],
       'debug': colors['b'] + '[DEBUG]' + '{}' + colors['e'], }


def set_configure(item):
    path = ''
    json_key = ''

    if item == 'template':
        json_key = 'template_dir'
    elif item == 'database':
        json_key = 'db_path'

    msg = (u'\U0001F337' '-----Configure %s\n'
           'By default your %s will be stored in %s\n'
           'Do you want to store %s in a different directory?\n'
           ' enter [y] to store %s to the custom directory\n'
           ' enter [n] to store %s to the default directory\n -->'
           ) % (item.title(), item, ROOT_PATH[:-5]+item+'s', item, item, item)
    choice_1 = input(fmt['q'].format(msg))

    # Set db_path in config.json
    if 'y' in choice_1.strip().lower():     # custom path to store db
        msg = 'Please enter the full path(!absolute path!) of directory\n -->'
        path = input(fmt['q'].format(msg)).strip()

        # (MacOs) path should end with / to get right path for db
        if not path.endswith('/'):
            path = path + '/'
    else:
        # make db directory
        path = ROOT_PATH[:-5] + item + 's/'

    # check if directory is exists, if not mkdir
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as error:
            msg = ('Error cused while try to mkdir'
                   'Please check if %s is the right path\n'
                   'If wrong path was given write right path in %s'
                   ) % (path, CONFIG_JSON)
            print(fmt['fail'].format(msg))
            print(fmt['fail'].foramt('---------Error'))
            print(fmt['fail'].format(error))
            sys.exit()

    # Update config.json
    with open(CONFIG_JSON, 'r') as cfg_file:
        config_data = json.load(cfg_file)

    config_data[json_key] = path

    with open(CONFIG_JSON, 'w', encoding='utf-8') as cfg_file:
        json.dump(config_data, cfg_file, indent=4)

    # print success message
    msg = ('Your configuration is sucessfully done.\n'
           'If you want to change the configuration\n'
           'open %s and edit it') % CONFIG_JSON
    print(fmt['ok'].format(msg))


def config(full_path=True, only_db_name=False):
    with open(CONFIG_JSON) as cfg_file:
        config_data = json.load(cfg_file)

    if config_data['db_path'] == '':
        set_configure(item='database')
        # Get updated config_data
        with open(CONFIG_JSON) as cfg_file:
            config_data = json.load(cfg_file)

    if full_path:
        return config_data['db_path'] + config_data['db_name']
    if only_db_name:
        return config_data['db_name']
    else:
        return config_data


class Database:
    def __init__(self):
        self.path = config()

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.path)
        except sqlite3.OperationalError:
            msg = ('Error cused while try to connect to database\n'
                   'Please check config.json file in %s' % CONFIG_JSON)
            print(fmt['fail'].format(msg))
            sys.exit()

        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, value, traceback):
        if traceback is None:
            self.conn.commit()
        else:
            self.conn.rollback()

            if exc_type == SystemExit:
                print(fmt['fail'].format('Exiting tp...'))
                self.conn.close()
                sys.exit()

            msg = 'An error has occurred.\n'
            msg += '[!] Error: %s | %s' % (exc_type, value)
            print(fmt['fail'].format(msg))

            self.cursor.close()
            self.conn.close()
            sys.exit()

        self.cursor.close()
        self.conn.close()


def create_db(args, secret=False):
    db_name = args.DB_NAME[0]

    path = config(full_path=False)['db_path']   # config
    db = db_name.replace(' ', '') + '.db'

    # Check if same dabase name already exsist.
    dbs = subprocess.getstatusoutput('ls %s' % path)[1]
    if db in dbs:
        msg = ('[!] The database name(%s) exists already, '
               'please choose a diffrent name.') % (db)
        print(fmt['fail'].format(msg))
        sys.exit()
    else:
        db_path = path + db
        try:
            sqlite3.connect(db_path)
            msg = ('Your database(%s) is created in %s') % (db, path)
            print(fmt['ok'].format(msg))
        except (Exception, sqlite3.Error) as error:
            msg = 'An error has occurred while creating the database.'
            msg += ' Please check your database path'
            print(fmt['fail'].format(msg))
            print(colors['r'] + '[!] Error: ' + str(error) + colors['e'])

    # Update config.json
    with open(CONFIG_JSON, 'r') as json_data_file:
        config_data = json.load(json_data_file)

    config_data['db_name'] = db

    with open(CONFIG_JSON, 'w') as f:
        json.dump(config_data, f, indent=4)


def print_data(table_name, data, detail=False):
    rows = data

    if detail:  # when user called read TABLE...
        row_fmt = colors['v'] + '|{}|' + colors['e'] + ' {}'  # columng | value
        print(fmt['ov_title'].format(table_name))
        for i in range(0, len(rows)):
            for k, v in dict(rows[i]).items():
                if type(v) == str and '{"' in v:
                    jv = json.loads(v)
                    print(row_fmt.format(k, json.dumps(jv, indent=4)))
                else:
                    print(row_fmt.format(k, v))

            print('{:_^100}'.format(''))

    else:   # when user called summary TABLE
        row_fmt = '|{0:>5}|{1:>10.10}|'  # ID, TimeStamp filed
        col_count = len(dict(rows[0])) - 2  # minus ID, timestamp field
        one_col_fmt = '{%d:>26.26}|'

        if col_count >= 6:
            one_col_fmt = '{%d:>10.10}|'
        elif col_count >= 4:
            one_col_fmt = '{%d:>15.15}|'

        row_fmt += ''.join([one_col_fmt % (int(i) + 2)
                            for i in range(col_count)])
        u_line_fmt = '|{0:_^%d}|' % (16 + col_count + (int(one_col_fmt[-4:-2])
                                     * col_count))

        columns = list(dict(rows[0]).keys())
        print(colors['v'] + u_line_fmt.format(table_name))
        # print column line
        print(row_fmt.format('ID', *columns[1:]) + colors['e'])
        # print rows
        for i in range(0, len(rows)):
            # val = list(map(str, dict(rows[i]).values()))
            val = [str(v) for v in dict(rows[i]).values()]
            print(row_fmt.format(*val))


def args_to_sql(table, columns='*', condition=''):
    if columns is None:
        columns = '*'
    else:
        columns = ','.join(columns)

    if condition is not None:
        where = " WHERE"
        for w in condition:
            # ID to tablenameID (default primarykey.)
            if w.upper().startswith('ID'):
                w = table + w.replace('id', 'ID')  # if user used small case id

            # Wildcard use
            if '[' in w:
                column, wildcard = w[1:-1].split('=')
                w = column + ' LIKE' + "'%" + wildcard + "%'"

            # < or >
            if '_gt_' in w:
                w = w.replace('_gt_', '>')
            if '_ls_' in w:
                w = w.replace('_ls_', '<')

            # for now not support numeric value type
            if '=' in w:
                column, value = w.split('=')
                w = column + "='" + value + "'"

            where += ' ' + w
    else:
        where = ''

    return columns, where


def fetch_data(args, detail=True):
    if detail is False:
        table = args.table
        columns = '*'
        where = ''
    else:
        table = args.table[0]
        columns, where = args_to_sql(table, args.col, args.where)

    sql = "SELECT %s, %s, %s FROM %s" % (table + 'ID', 'TimeStamp',
                                         columns, table)
    sql += where

    if detail:
        SIZE = 5
    else:
        SIZE = 15

    cursor = Database()
    with cursor as c:
        c.execute(sql)
        while True:
            data = c.fetchmany(SIZE)
            if data == []:
                print(fmt['fail'].format('No data to read'))
                break

            print_data(table, data, detail)

            if len(data) < SIZE:
                print(fmt['ok'].format('Endofdata'))
                break

            msg = 'Do you want to read next %s rows? y/n\n-->' % SIZE
            answer = input(fmt['q'].format(msg)).lower().strip()
            if 'y' in answer:
                continue
            else:
                break


def create_table(table_name, contents_keys):
    columns = ''
    for k in contents_keys:
        if '[' in k:
            k, v = k[:-1].split('[')
            columns += '%s %s,' % (k, v.upper())
        else:
            columns += '%s TEXT,' % (k)

    sql = ('CREATE TABLE IF NOT EXISTS %s' '(%sID INTEGER '
           'PRIMARY KEY NOT NULL, TimeStamp TEXT,' % (table_name, table_name))
    sql += columns[:-1]
    sql += ');'

    return sql


def insert_memo(args):
    if args.template_dir:   # option -t, put template path
        template_path = config(full_path=False)['template_dir']
        memo_file = template_path + args.file[0]
    else:
        memo_file = args.file[0]

    table_name, contents = memo_to_dict(memo_file)

    cursor = Database()
    with cursor as c:
        # check if the table is exist
        c.execute('PRAGMA table_info(%s)' % (table_name))
        table_info = c.fetchone()
        if table_info is None:  # table does not exist
            msg = ('Table %s does not exist. '
                   'Do you want to create new table  (y/n) \n' '==>'
                   ) % (table_name)
            answer = input(fmt['q'].format(msg)).strip().lower()

            if 'y' in answer:
                create_query = create_table(table_name, contents.keys())
                c.execute(create_query)   # create new table
                msg = ('Table %s is created') % (table_name)
                print(fmt['ok'].format(msg))
            else:
                msg = ('To check exists table list -> -ls tables')
                sys.exit()

        # insert memo.
        values = []
        columns = 'TimeStamp,'
        query_2 = ''

        for k, v in contents.items():
            query_2 += '?,'
            if '[' in k:
                columns += k[:k.index('[')] + ','
            else:
                columns += k + ','

            if type(v) is dict or type(v) is list:
                json_v = json.dumps(v)
                values.append(json_v)
            else:
                values.append(v)

        query_1 = ("INSERT iNTO %s(%s) VALUES(datetime('now', 'localtime'),"
                   % (table_name, columns[:-1]))
        query = query_1 + query_2[:-1] + ')'

        c.execute(query, tuple(values))  # insert memo
        print(fmt['ok'].format('Record is inserted into database.'))


def delete(args):
    table = args.table[0]
    where = args.where
    where_sql = args_to_sql(table, condition=where)[1]

    if where_sql == '':  # when only table_name defined.
        msg = ('This will delete all the records in %s.\n'
               'Do you want to delete %s? y/n \n==>' % (table, table))
        answer = input(fmt['q'].format(msg)).lower().strip()

        if answer == 'y':
            sql = 'DROP TABLE %s' % table

            cursor = Database()
            with cursor as c:
                c.execute(sql)
            print(fmt['ok'].format('%s is deleted.' % table))
        else:
            print(fmt['ok'].format('The command was successfully cancelled.'))

    else:
        sql = 'DELETE FROM %s%s' % (table, where_sql)

        cursor = Database()
        with cursor as c:
            c.execute(sql)

        print(fmt['ok'].format('Records is deleted.'))


def update(args):
    where_sql = args_to_sql(args.table[0], condition=args.where)[1]
    new_value = args.new_value[0].split('=')
    try:
        set_sql = new_value[0] + "='" + new_value[1] + "'"
    except IndexError:
        msg = 'Fail to update record.'
        print(fmt['fail'].format(msg))
        # TODO check if sys.exit() is right method.
        sys.exit()

    if where_sql == '':
        msg = fmt['q'].format('This will update all records in'
                              'the table\nAre you sure? y/n\n')
        answer = input(msg).lower()
        if 'y' not in answer:
            print(fmt['ok'].format('The command was successfully cancelled.'))
            return

    sql = 'UPDATE %s SET %s %s' % (args.table[0], set_sql, where_sql)

    cursor = Database()
    with cursor as c:
        c.execute(sql)

    print(fmt['ok'].format('Record is updated'))


def shell(args):
    db_path = config()

    buffer = ''
    print(colors['y'] + "[*]Enter your SQL commands to execute in sqlite3." +
          colors['e'])
    print(colors['y'] + "[*]Enter a blank line to exit." + colors['e'])

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    while True:
        line = input(colors['b'] + 'sqlite>' + colors['e'])
        if line == "":
            break
        buffer += line
        if sqlite3.complete_statement(buffer):
            buffer = buffer.strip()
            try:
                c.execute(buffer)
                result = c.fetchall()
                if result is not None:
                    print(result)

                if buffer.lstrip().upper().startswith("SELECT"):
                    print(c.fetchall())
            except sqlite3.Error as Error:
                print(fmt['fail'].format('Error == %s' % Error))
                pass
        buffer = ""

    conn.commit()
    c.close()
    conn.close()


def summary_function_filter(args):
    if args.table is None:
        summary()
    else:
        fetch_data(args, detail=False)  # One table summary


def summary(only_table_name=False):
    db_name = config(full_path=False, only_db_name=True)[:-3]
    cursor = Database()
    with cursor as c:
        # sqlite_master returns (type, name, tbl_name, rootpage, sql)
        c.execute('SELECT * FROM sqlite_master')
        master = c.fetchall()

        if only_table_name:  # list table
            print(fmt['ls_title'].format('Tables'))
            for m in master:
                print(fmt['ls_content'].format(m['tbl_name']))
            return

        print(fmt['ov_title'].format(db_name))
        print(fmt['ov_row_0'].format('Table_name', 'Column', 'type', 'total'))

        for m in master:
            # get columns
            columns = m['sql'].split('(')[1][:-1].split(',')
            pk_col = columns[0].split(' ')[0]

            c.execute('select count(*) from %s' % m['tbl_name'])
            total = c.fetchall()
            print(fmt['ov_content'].format(m['tbl_name'], pk_col, 'PK',
                                           total[0]['count(*)']))

            for col in columns[1:]:
                column = col.strip().split(' ')  # [column_name, datatype]
                if len(column) == 1:  # If user didn't specify datatype.
                    column.append('.')
                print(fmt['ov_content'].format('. . .', column[0],
                                               column[1].upper(), ''))
            print(fmt['ov_content_u'].format('', '', '', ''))


def list_function(args):
    opt = args.list_opt.lower().strip()

    if opt == 'db':
        print(fmt['ls_title'].format('Databases'))
        path = config(full_path=False)['db_path']
        dbs = subprocess.getstatusoutput('ls %s' % path)[1].split('\n')
        for d in dbs:
            print(fmt['ls_content'].format(d))
        sys.exit()
    elif opt == 'table':
        return summary(only_table_name=True)
    else:
        msg = 'You can choose either db or table for list option'
        print(fmt['fail'].format(msg))


def template(args):
    table_name = args.table[0]

    sql = "SELECT sql FROM sqlite_master WHERE tbl_name='%s';" % table_name
    cursor = Database()
    with cursor as c:
        c.execute(sql)
        column_data = c.fetchall()

    try:
        columns = column_data[0][0][:-1].split(',')[2:]
        # columns[0] is autogenerate PK
        # columns[1] is autogenerate timestamp
    except IndexError:
        msg = 'Fail to write %s template. ' % table_name
        print(fmt['fail'].format(msg))

    template = '#tp:table\n%s\n\n' % table_name[0]
    for column in columns:
        name, datatype = column.strip().split(' ')
        if datatype.lower() == 'json':
            tpl_col = '#tp:' + name + '[' + 'JSON' + ']'
            tpl_col += '\n @key:'
        else:
            tpl_col = '#tp:' + name + '[' + datatype.upper() + ']'
        template += tpl_col + '\n\n'

    template_path = config(full_path=False)['template_dir']
    # If template_path is not set
    if template_path == '':
        set_configure(item='template')

    tpl_file = template_path + table_name[0] + '_tpl' + '.md'

    try:
        with open(tpl_file, 'w', encoding='utf_8') as tpl:
            tpl.write(''.join(template))

    except IOError as error:
        print(fmt['fail'].format('Fail to write %s template. ' % table_name))
        print(fmt['fail'].format(error))


def backup(args):
    config_data = config(full_path=False)
    path = args.path
    now = datetime.now()
    date = '{}-{}-{}-{}:{}'.format(now.year, now.month, now.day,
                                   now.hour, now.minute)

    if path is not None:
        if not path.endswith('/'):      # MacOs
            path += '/'
        backup = '{}{}_{}.db'.format(path, config_data['db_name'][:-3],
                                     date)
    else:
        backup = '{}{}_{}.db'.format(config_data['db_path'],
                                     config_data['db_name'][:-3],
                                     date)

    original_db = config_data['db_path'] + config_data['db_name']

    try:
        copyfile(original_db, backup)
    except IOError as error:
        msg = 'The creation of backup for the existing database failed.'
        print(fmt['fail'].format(msg))
        print(fmt['fail'].format(error))
        sys.exit()

    msg = 'The backup for the database is successfully created.'
    print(fmt['ok'].format(msg))


def memo_to_dict(memo_file):
    contents = {}
    # temp
    current_field = ''
    sub_field = 'default'
    sub_field_count = 0

    # open text file and put each line into the list.
    try:
        with open(memo_file, 'r') as f:
            memo = f.readlines()
    except FileNotFoundError as error:
        print(colors['r'] + str(error) + colors['e'])
        sys.exit()

    for line in memo:
        if line == '\n':
            continue
        line = line.replace('\n', '').strip()

        if '#tp:' in line:
            line = line.strip()
            field = line[4:]
            if 'json' in field.lower():
                root_field = field
                if root_field in contents:
                    contents[root_field].append({})
                    sub_field_count += 1
                else:
                    contents[root_field] = [{}]
                    current_field = root_field
                    sub_field_count = 0
            else:
                contents[field] = ''
                current_field = field

        # line without tag(@tp_) will be a value of contents.
        else:
            if contents == {}:
                continue
            if type(contents[current_field]) == list:
                if '@key:' in line:
                    sub_field = line[5:]
                    contents[current_field][sub_field_count][sub_field] = ''
                    continue
                try:
                    contents[current_field][sub_field_count][sub_field] += line
                except KeyError:
                    print('Please define JSON Key value as @key:[KEY_NAME]')
                    sys.exit()
            else:
                contents[current_field] += line

    # coontents dictionary to json file foramt.
    # json_test = json.dumps(contents, indent=4)
    # pymongo use bson or dict file.
    try:
        table_name = contents.pop('table')
    except KeyError:
        print(colors['fail'].format('Please define table name. /@tp_table'))

    return table_name, contents


w_help_msg = """Specify the record(s)
____________________where usage____________________
+Fetch the record with ID
    -w ID=3
+Fetch the record(s) with KEYWORD
    -w COLUMN=KEYOWRD
+Fetch the record(s) with WILDCARD
    -w [COLUMN=WILDCARD]
+Fetch the record(s) with greater or less than operator
    -w COLUMN_gt_VALUE or -w COLUMN_ls_VALUE
"""


def parser():
    # create the parser
    parser = argparse.ArgumentParser(
            description=u'\U0001F337',
            epilog='git : https://github.com/fiftypercent-mima/tulip',
            usage=""" %(prog)s COMMAND [OPTION]""",
            )
    subparsers = parser.add_subparsers(
            title='command',
            metavar='* for more information : tulip COMMAND -h *')

    # backup
    backup_parser = subparsers.add_parser(
            'backup', help=' Create a backup',
            usage='tulip backup [OPTION]\n Create a backup')
    backup_parser.add_argument(
            '-p', '--path', type=str, nargs='?', help='Location of backup')
    backup_parser.set_defaults(func=backup)

    # create
    new_parser = subparsers.add_parser(
            'create', help='Create a new database',
            usage='tulip create DATABASE_NAME\n Create a new database')
    new_parser.add_argument(
            'DB_NAME', type=str, nargs=1, help=argparse.SUPPRESS)
    new_parser.set_defaults(func=create_db)

    # delete
    del_parser = subparsers.add_parser(
            'delete', help='Delete one or more records',
            formatter_class=RawTextHelpFormatter,   # for help message
            usage=' tulip delete TABLE                : Drop the table\n'
            '\ttulip delete TABLE [-w CONDITION] '
            ': Delete the record(row) or records')
    del_parser.add_argument(
            'table', type=str, nargs=1, help=argparse.SUPPRESS)
    del_parser.add_argument(
            '-w', '--where', type=str, nargs='*',
            help=w_help_msg)
    del_parser.set_defaults(func=delete)

    # insert
    insert_parser = subparsers.add_parser(
            'insert', help='Insert record into database',
            usage='tulip insert TEMPLATE_FILE\n'
                  ' Insert record into database')
    insert_parser.add_argument(
            'file', type=str, nargs=1, help=argparse.SUPPRESS)
    insert_parser.add_argument(
            '-t', '--template_dir', action='store_true',
            help='template directory path'
            )
    insert_parser.set_defaults(func=insert_memo)

    # list
    list_parser = subparsers.add_parser(
            'list', help='List tables',
            usage='tulip list {table | db}\n'
                  ' List tables or databases  (*defaults=table)')
    list_parser.add_argument('list_opt', type=str, nargs='?', default='table',
                             help=argparse.SUPPRESS)
    list_parser.set_defaults(func=list_function)

    # summary
    summary_parser = subparsers.add_parser(
            'summary',  help='Display the summary of database or table',
            usage='tulip summary [TABLE]\n'
                  ' Display the summary of the database')
    summary_parser.add_argument(
            'table', type=str, nargs='?', help='Display the summary of table')
    summary_parser.set_defaults(func=summary_function_filter)

    # read
    read_parser = subparsers.add_parser(
            'read', help='Display one or more records',
            formatter_class=RawTextHelpFormatter,
            usage='tulip read TABLE [-c COLUMN] [-w CONDITION]\n'
                  ' Display the record(s)')
    read_parser.add_argument(
            'table', type=str, nargs=1, help=argparse.SUPPRESS)
    read_parser.add_argument(
            '-c', '--col', type=str, nargs='*',
            help='Specify the column(s) to display')
    read_parser.add_argument(
            '-w', '--where', type=str, nargs='*', help=w_help_msg)
    read_parser.set_defaults(func=fetch_data)

    # shell
    shell_parser = subparsers.add_parser(
            'shell', help='Open sqlite3 shell',
            usage='tulip shell\n Open sqlite3 shell')
    shell_parser.set_defaults(func=shell)

    # template
    tpl_parser = subparsers.add_parser(
            'template', help='Make table_name_tpl.md file',
            usage='tulip template TABLE\n'
                  ' Make table_name_tpl.md file')
    tpl_parser.add_argument('table', type=str, nargs=1, help=argparse.SUPPRESS)
    tpl_parser.set_defaults(func=template)

    # update
    up_parser = subparsers.add_parser(
            'update', help='Update record(s)',
            formatter_class=RawTextHelpFormatter,
            usage='tulip update TABLE COLUMN=VALUE [-w CONDITION]\n'
                  ' Update record(s)')
    up_parser.add_argument(
            'table', type=str, nargs=1, help=argparse.SUPPRESS)
    up_parser.add_argument(
            'new_value', type=str, nargs=1, help=argparse.SUPPRESS)
    up_parser.add_argument(
            '-w', '--where', type=str, nargs='*', help=w_help_msg)
    up_parser.set_defaults(func=update)

    return(parser)


def main():
    tulip_parser = parser()
    args = tulip_parser.parse_args()
    try:
        args.func(args)
    except AttributeError:      # tulip without command occurs this error
        tulip_parser.print_help()
        tulip_parser.exit()


if __name__ == '__main__':
    main()
