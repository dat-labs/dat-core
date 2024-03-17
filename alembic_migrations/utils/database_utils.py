# database_utils.py

def create_trigger(table_name: str, column_name: str) -> str:
    return f'''
        CREATE TRIGGER trigger_{table_name}_{column_name}
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        EXECUTE FUNCTION function_{table_name}_{column_name}();
    '''

def create_trigger_function(table_name: str, column_name: str) -> str:
    return f'''
        CREATE OR REPLACE FUNCTION function_{table_name}_{column_name}()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.{column_name} = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    '''

def drop_trigger(table_name: str, column_name: str) -> str:
    return f'DROP TRIGGER IF EXISTS trigger_{table_name}_{column_name} ON {table_name}'

def drop_trigger_function(table_name: str, column_name: str) -> str:
    return f'DROP FUNCTION IF EXISTS function_{table_name}_{column_name}'
