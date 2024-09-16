# inisql
sql inspired query driven abstraction layer for managing ini files parsed using ConfigParser 

## usage:

Initialization:
> inisql('file.ini', interpolation=None)

SELECT:
> sql.execute("SELECT * FROM global")
> 
> sql.execute("SELECT * FROM global WHERE key=value")
> 
> sql.execute("SELECT * FROM global WHERE key1=value1 AND key2=value2")
> sql.execute("SELECT * FROM global WHERE ?=?", ['key1', 'value1']) << Note: bound parameter implementation is basic. does not verify types.

INSERT:
> sql.execute("INSERT INTO section (key=value)")

UPDATE:
> sql.execute("UPDATE section SET key=newValue WHERE key=value")

DELETE:
> sql.execute("DELETE FROM section WHERE key=value")

DROP (section):
> sql.execute("DROP SECTION section")

DROP (option):
> sql.execute("DROP OPTION option FROM section")

result:
> print(sql.result)
