import psycopg2
import ujson


class Format_resp():
    def __init__(self, resp_text = None, data_type = 'JSON'):
        self.resp = resp_text
        self.data_type = data_type


    def do(self, resp = None, new_items = None, json_key = None):
        if self.data_type == 'JSON':
            #new items - if we need to add some specific data to the API response before writing it to the DB
            if resp is not None:
                try:
                    if json_key is None:
                        data = ujson.loads(resp)
                    else:
                        data = ujson.loads(resp)[json_key]
                    if new_items is None:
                        print('returning unchainged')
                        return data
                    else:
                        print('Appending new data to json items: ', new_items)
                        for data_item in data:
                            for key in new_items:
                                data_item[key] = new_items[key]
    #                print(data)
                    return data
                except Exception as ex:
                    print('Exception during processing JSON: {}'.format(ex))
            else:
                print('got none to JSON processing {}')
                return None
        else:
            pass


class Writer:
    def prepare_request(self, sql_part, json_part):
        print('not implemented')

class Db_writer(Writer):
    def __init__(self, connect_params, db_type = 'postgres'):
        self.db_type = db_type
        self.connect_params = connect_params
        if db_type == 'postgres':
            self.connect()
        else:
            pass

    def connect(self):
        if self.db_type == 'postgres':
            try:
                self.dbconn = psycopg2.connect(**self.connect_params)
                self.cur = self.dbconn.cursor()
                print('Connected to the PostgreSQL database')
            except Exception as e:
                print('Error connecting to DB: ', e)


    def prepare_request(self, sql_part, json):
        if self.db_type == 'postgres':
            for item in json:
                self.cur.execute(sql_part, item)
        else:
            print('other DB adapter not implemented')

    def commit(self):
        self.cur.execute('COMMIT;')

    def close(self):
        if self.db_type == 'postgres':
            self.cur.close()
            self.dbconn.close()

if __name__ == '__main__':
    pass
