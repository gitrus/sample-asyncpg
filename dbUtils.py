import asyncpg
import logging

class Table:
    """
    Utils for create table helpers from entity_dictionary.
    """
    def __init__(self, table_info: dict):
        self.name = table_info["table_name"]
        self.columns = [
            str(key) for key in table_info["column_map"]
        ]
        self.column_options = table_info["column_map"]
        self.id_column_name = table_info["id_column_name"]

    @staticmethod
    def __list_to_tuples(lst: list) -> str:
        return "({})".format(", ".join([str(elem) for elem in lst]))

    @staticmethod
    def __prepare_value(value):
        if isinstance(value, str):
            return "'{}'".format(value.replace('\\', '\\\\').replace("'", "''"))
        elif value is None:
            return "NULL"
        else:
            return value

    @staticmethod
    def __prepare_array(arr):
        return 'ARRAY[{}]'.format(', '.join([Table.__prepare_value(elem) for elem in arr]))

    def __entity_to_values(self, entity: dict, exclude_columns: list) -> str:
        escaped_list = []
        for column in self.columns:
            if column not in entity:
                escaped_list.append("NULL")
            elif column not in exclude_columns:
                escaped_list.append(
                    self.__prepare_array(entity[column]) if self.column_options[column]['is_array']
                    else self.__prepare_value(entity[column])
                )

        return self.__list_to_tuples(escaped_list)

    @staticmethod
    def __select_rules_to_conditions(select_rules):
        conditions = []
        for rule_name in select_rules:
            if rule_name == "date_range":
                conditions.append(
                    "{column_name} >= '{date_from}' AND {column_name} <= '{date_to}'".format(
                        column_name=select_rules[rule_name]["date_column_name"],
                        date_from=select_rules[rule_name]["range"][0],
                        date_to=select_rules[rule_name]["range"][1]
                    )
                )
            elif rule_name == "in":
                conditions.append(
                    "{column_name} IN {array}".format(
                        column_name=select_rules[rule_name]["column_name"],
                        array=Table.__list_to_tuples(select_rules[rule_name]["value_array"])
                    )
                )
            else:
                raise NotImplementedError(rule_name)

        return "" if (len(conditions) == 0) else "WHERE " + " AND ".join(conditions)

    def prepare_insert(self, data: list) -> str:
        if len(data) == 0:
            return ""

        template = "INSERT INTO {table_name} {column_names} VALUES {values} RETURNING {id_column_name}"
        values = [self.__entity_to_values(entity, []) for entity in data]

        insert = template.format(
            table_name=self.name,
            column_names=Table.__list_to_tuples(self.columns),
            values=', '.join(values),
            id_column_name=self.id_column_name
        )
        return insert

    async def insert(self, connection, data: list) -> list:
        if len(data) == 0:
            return []

        insert_query = self.prepare_insert(data=data)

        try:
            async with connection.transaction():
                insert_returning = await connection.fetch(insert_query)
        except asyncpg.exceptions.InFailedSQLTransactionError as error:
            logging.error("insert failed {}".format(error))
            return []

        return insert_returning
