# :tulip: 
:tulip: Tulip is your personal database(SQLite) tool. :tulip:

## Highlights
* Store your journals, study notes, etc., in the databse and View, Manage them on the Terminal.
* Written in python

## Installation
For now tulip only runs on MacOs

### Requirements
-Python3
-pip3

### MacOS
    # Download the repository.
    $ git clone [address]
    
    # Installation
    pip3 install -e .

    # Uninstall
    pip3 uninstall tulip 

    # Create database
    $ tulip create DB_NAME

### Windows & Ubuntu
coming soon ...

## Usage
usage: tulip COMMAND [OPTION]

optional arguments:
  -h, --help            show this help message and exit

command:
  (for more information : tulip COMMAND -h)
    backup              Create a backup
    create              Create a new database
    delete              Delete one or more records
    insert              Insert record into database
    list                List tables
    summary             Display the summary of database or table
    read                Display one or more records
    shell               Open sqlite3 shell
    template            Make table_name_tpl.md file
    update              Update record(s)
-----------------------------------------------------------------
### Exemple of summary
$ tulip summary
![ex-summary](/images/tpl_ex_summary.jpg){: style="float:center"}

$ tulip summary [TABLE] 
![ex-summary-table](/images/tpl_ex_summary_table.jpg){: style="float:center"}

### Template Rules
-Define Table
    #tp:table
        Write table name here
-Define Column and Column's value
    #tp:column name 
        column's value
-Define Column Datatype
    #tp:column name[DATATYPE]
    if no datatype given, then datatype will be TEXT
-If Datatype is json
    #tp:ThirdColumnName[json]
        @key:json_key_name
            value

#### Template Exemple
    #tp:table
        TableName

    #tp:ColumnName
        When columns's data type is not defined
        default value is TEXT
     
    #tp:SecondColumnName[integer]
        50

    #tp:ThirdColumnName[json]
        @key:json_key_name
            value
        
        @key:second_json_key_name
            second_json_value

* read insrted exemple.md on tulip
    $ tulip read TableName
![tpp-ex-read](/images/tpl_ex_read.jpg){: style="float:center"}

* TableID(auto increment, PrimaryKey) and timestamp(YYYY-mm-DD HH:MM:ss) will be inserted by default. 
* You can use any filetype .txt, .md, etc., 

## Contributing
In case you spotted an error or think that an example is not to clear enough and should be further improved, please feel free to open an issue or pull request.

## Behind The Tulip 
If you've scrolled this for you might as well interesting about behind story of this program.
This is my first program I wrote to learn python. 
I fall in love with programming but yet I don't know how to make love with programming safely , beautifully. 
If you can give me any tip or advice about tulp code or general programming. 
You will be the rain in my deadly isolated and droughted programming land.
I wellcome any literally any programming adivce and I won't forget your help.

## License
[MIT](https://choosealicense.com/licenses/mit/)
