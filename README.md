# inisql
sql inspired query driven abstraction layer for managing ini files parsed using ConfigParser 

## usage:

Initialization:
> sql.inisql('file.ini', interpolation=None)

prepared statements:
| placeholder | type | description | example |
|-------------|------|-------------|---------|
| %s | string | accepts string only | SELECT * FROM section WHERE key=%s |
| %i | integer | accepts integers only | SELECT * FROM section WHERE key=%i |
| %f | float | accepts floats only | SELECT * FROM section WHERE key=%f |
| %b | boolean | accepts boolean only | SELECT * FROM section WHERE key=%b |
| ? | None/Any | accepts NoneType or any type | SELECT * FROM section WHERE key=? |

SELECT:
> sql.execute("SELECT * FROM section")
> 
> sql.execute("SELECT * FROM section WHERE key=value")
> 
> sql.execute("SELECT * FROM section WHERE key1=value1 AND key2=value2")
> 
> sql.execute("SELECT * FROM section WHERE %s=%i", ['key1', 1]) 
>
> sql.execute("SELECT key1,key2 FROM section")

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

errors:
> print(sql.error)

dictionary:
> print(sql)
