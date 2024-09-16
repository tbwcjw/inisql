import configparser
import re


class inisqlparser:
    def __init__(self, config_file, *args, **kwargs):
        self.config = configparser.ConfigParser(*args, **kwargs)
        self.config.read(config_file)
        self.config_file = config_file

    def execute(self, query):
        tokens = query.split()
        if len(tokens) == 0:
            raise ValueError("Empty query")
        
        command = tokens[0].upper() #query type

        verbs = {
            'SELECT': self._select_query(tokens),
            'INSERT': self._select_query(tokens),
            'UPDATE': self._select_query(tokens),
            'DELETE': self._select_query(tokens),
            'DROP': self._select_query(tokens),
        }
        
        if command not in verbs: 
            raise ValueError(f"Unsupported operation: {command}")
        return verbs[command]
    
    def _select_query(self, tokens):
        if tokens[1] != '*' or tokens[2].upper() != 'FROM':
            raise ValueError("Invalid SELECT syntax")
        
        section = tokens[3]
        if section not in self.config:
            raise ValueError(f"Section {section} not found")
        
        return dict(self.config[section])
    
    def _insert_query(self, tokens):
        if tokens[1].upper() != 'INTO':
            raise ValueError("Invalid INSERT syntax")
        
        section = tokens[2]
        key_values = ' '.join(tokens[3:]).strip("()").split(",")
        kv_pairs = [kv.strip().split("=") for kv in key_values]

        if section not in self.config:
            self.config.add_section(section)
        
        for key, value in kv_pairs:
            self.config[section][key.strip()] = value.strip()
        
        self._commit_changes()

    def _update_query(self, tokens):
        if tokens[2].upper() != 'SET' or 'WHERE' not in tokens:
            raise ValueError("Invalid UPDATE syntax")
        
        section = tokens[1]
        set_clause = ' '.join(tokens[3:tokens.index('WHERE')]).strip()
        where_clause = ' '.join(tokens[tokens.index('WHERE') + 1:]).strip()

        if section not in self.config:
            raise ValueError(f"Section {section} not found")
        
        set_key, set_value = set_clause.split("=")
        where_key, where_value = where_clause.split("=")

        if self.config[section].get(where_key.strip()) == where_value.strip():
            self.config[section][set_key.strip()] = set_value.strip()
            self._commit_changes()
            #todo: handle race condition WHERE is not met

    def _delete_query(self, tokens):
        if tokens[1].upper() != 'FROM' or 'WHERE' not in tokens:
            raise ValueError("Invalid DELETE syntax")
        
        section = tokens[2]
        where_clause = ' '.join(tokens[tokens.index('WHERE') + 1:]).strip()
        where_key, where_value = where_clause.split("=")

        if section not in self.config:
            raise ValueError(f"Section {section} not found")
        
        if self.config[section].get(where_key.strip()) == where_value.strip():
            del self.config[section][where_key.strip()]
            self._commit_changes()

    def _drop_query(self, tokens):
        if tokens[1].upper() == 'SECTION':
            section = tokens[2]
            if section not in self.config:
                raise ValueError(f"Section {section} not found.")
            self.config.remove_section(section)
            self._commit_changes()
        if tokens[1].upper() == 'OPTION':
            section = tokens[4]
            option = tokens[2]
            if section not in self.config:
                raise ValueError(f"Section {section} not found")
            if option not in self.config[section]:
                raise ValueError(f"Option {option} not found in {section}")
            self.config.remove_option(section, option)
            self._commit_changes()
            
    def _commit_changes(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    
sql = inisqlparser('smb.conf', interpolation=None)

#print(sql.execute("SELECT * FROM global"))
#print(sql.execute("INSERT INTO user (key=value)"))
#print(sql.execute("UPDATE user SET key=newValue WHERE key=value"))
#print(sql.execute("DELETE FROM user WHERE key=newValue"))
#print(sql.execute("DROP SECTION user"))