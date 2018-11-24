class QueryResult:
    def __init__(self, cursor, source, error=None):
        self.source = source
        if error:
            self.error = error
        else:
            if cursor:
                self.headings = [x[0] for x in cursor.description]
                self.rows = cursor.fetchall()
            else:
                self.headings = None
                self.rows = None


def wrap(fn):
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            return QueryResult(None, None, e)
        return result
    return wrapper
