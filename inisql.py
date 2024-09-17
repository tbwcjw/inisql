import configparser
import re


class inisql:
    def __init__(self, config_file, *args, **kwargs):
        self.config = configparser.ConfigParser(*args, **kwargs)                    #pass args, kwargs to config parser
        self.config.read(config_file)                                               #read input file
        self.config_file = config_file                                              #store input file
        self.last_query= str()
        self.result = dict()
        self.error = dict()

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}                             #output inisql to dictionary

    def execute(self, query, params=None):
        tokens = query.split()
        if len(tokens) == 0:
            self.error = ValueError("Empty query")                                  
            return False                                                            #execute will always return True/False
                                                                                    #results, config and info are stored seperately
        command = tokens[0].upper()                                                 #verb                 
        if params:
            query = self._replace_placeholders(query, params)
            tokens = query.split()

        verbs = {                                                                   #trying to implement as many SQL language operations
            'SELECT': self._select_query(tokens),
            'INSERT': self._insert_query(tokens),
            'UPDATE': self._update_query(tokens),
            'DELETE': self._delete_query(tokens),
            'DROP': self._drop_query(tokens),
        }
        
        if command not in verbs: 
            self.error = ValueError(f"Unsupported operation: {command}")            #requested operation not in verbs
            return False
        
        self.last_query = query
        return verbs[command]
    
    def _replace_placeholders(self, query, params):                                 #bind parameters placeholder types
        type_placeholders = {
            '%s': str,
            '%i': int,
            '%f': float,
            '%b': bool,
            '?' : None                                                              #can match any type
        }

        for placeholder, expected_type in type_placeholders.items():
            while placeholder in query:
                if not params:
                    raise ValueError(f"Not enough parameters providers for query placeholders")
                
                param = params.pop(0)                                               #iterate and pop each param(s) into param

                if placeholder != '?' and not isinstance(param, expected_type):     #no match placeholder/query
                    raise TypeError(f"Expected {expected_type.__name__} for placeholder '{placeholder}' but got {type(param).__name__}")
                
                if isinstance(param, bool):
                    param = 'TRUE' if param else 'FALSE'
                elif isinstance(param, float):
                    param = f"{param}"
                elif param is None:                         
                    param = "NULL"
                else:
                    param = str(param)

                query = query.replace(placeholder, param, 1)
        if params:                                                                  #iteration ended with remainder. error.
            raise ValueError("Too many parameters provided for query placeholders") 
        return query
    
    def _select_query(self, tokens):                                                #SELECT operation
        if tokens[2].upper() != 'FROM': 
            self.error = ValueError("Invalid SELECT syntax")
            return False
        
        keys = tokens[1].split(",") if tokens[1] != '*' else None                   #TODO: make this work with spaces (key, key)
        section = tokens[3]                                                         #currently only works without (key,key)

        if section not in self.config:
            self.error = ValueError(f"Section {section} not found")
            return False
        
        result = dict(self.config[section])

        if keys:
            result = {key: result[key] for key in keys if key in result}            #key if not key if key key if key not key key key not if in key key key
            missing_keys = [key for key in keys if key not in result]               #jesus christ what a fucking mess
            if missing_keys:
                self.error = ValueError(f"Keys not found {','.join(missing_keys)}") #keys not present in dictionary, error
                return False
        if 'WHERE' in tokens:
            where_clause = ' '.join(tokens[tokens.index('WHERE')+1:])
            conditions = self._parse_conditions(where_clause)
            result = self._apply_conditions(result,conditions)

        self.result = result
        return True
    
    def _parse_conditions(self, where_clause):                                      #iterate over conditions if exists
        conditions = where_clause.split('AND')
        parsed_conditions = []
        for condition in conditions:
            key, value = condition.split("=")
            parsed_conditions.append((key.strip(), value.strip()))
        return parsed_conditions

    def _apply_conditions(self, section_dict, conditions):                          #filter results using conditions
        filtered_result = {}
        for key, value in section_dict.items():
            match = all(section_dict.get(cond_key) == cond_value for cond_key, cond_value in conditions)
            if match:
                filtered_result[key] = value
        return filtered_result

    def _insert_query(self, tokens):                                                #INSERT operation
        if tokens[1].upper() != 'INTO':
            self.error = ValueError("Invalid INSERT syntax")
            return False
        
        section = tokens[2]
        key_values = ' '.join(tokens[3:]).strip("()").split(",")
        kv_pairs = [kv.strip().split("=") for kv in key_values]

        if section not in self.config:
            self.config.add_section(section)
        
        for key, value in kv_pairs:
            self.config[section][key.strip()] = value.strip()
        
        self._commit_changes()
        return True

    def _update_query(self, tokens):                                                #UPDATE operation
        if tokens[2].upper() != 'SET' or 'WHERE' not in tokens:
            self.error =  ValueError("Invalid UPDATE syntax")
            return False
        
        section = tokens[1]
        set_clause = ' '.join(tokens[3:tokens.index('WHERE')]).strip()
        where_clause = ' '.join(tokens[tokens.index('WHERE') + 1:]).strip()

        if section not in self.config:
            self.error = ValueError(f"Section {section} not found")
            return False
        
        set_key, set_value = set_clause.split("=")
        where_key, where_value = where_clause.split("=")

        if self.config[section].get(where_key.strip()) == where_value.strip():
            self.config[section][set_key.strip()] = set_value.strip()
            self._commit_changes()
            return True
        return False

    def _delete_query(self, tokens):                                                #DELETE operation
        if tokens[1].upper() != 'FROM' or 'WHERE' not in tokens:
            self.error = ValueError("Invalid DELETE syntax")
            return False
        
        section = tokens[2]
        where_clause = ' '.join(tokens[tokens.index('WHERE') + 1:]).strip()
        where_key, where_value = where_clause.split("=")

        if section not in self.config:
            self.error = ValueError(f"Section {section} not found")
            return False
        
        if self.config[section].get(where_key.strip()) == where_value.strip():
            del self.config[section][where_key.strip()]
            self._commit_changes()
            return True
        return False

    def _drop_query(self, tokens):                                                  #DROP operation
        if tokens[1].upper() == 'SECTION':
            section = tokens[2]
            if section not in self.config:
                self.error =  ValueError(f"Section {section} not found.")
                return False
            self.config.remove_section(section)
            self._commit_changes()
        if tokens[1].upper() == 'OPTION':
            section = tokens[4]
            option = tokens[2]
            if section not in self.config:
                self.error = ValueError(f"Section {section} not found")
                return False
            if option not in self.config[section]:
                raise ValueError(f"Option {option} not found in {section}")
            self.config.remove_option(section, option)
            self._commit_changes()
            return True
        return False
            
    def _commit_changes(self):                                                      #commit to file
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

sql = inisql('smb.conf', interpolation=None)

print(sql.execute("SELECT key,key FROM section"))
print(sql.to_dict())