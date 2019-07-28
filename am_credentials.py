class AutometaUser(object):
    """docstring for AutometaUser."""

    def __init__(self, username, password, security_token):
        super(AutometaUser, self).__init__()
        self.username = username
        self.password = password
        self.security_token = security_token

    def create(self, params, data):
        # TODO: Add job to workqueue master for slurm or CHTC...
        """method to start new autometa analysis"""
        print("posting project to workqueue master")
        print(params)

    def query(self, query):
        # TODO: query database for user to get available processed and pending jobs
        """Get user's projects pending/processed in db."""
        result = psql.query(query)
        return result


class exceptions(object):
    """docstring for exceptions."""

    def __init__(self, arg):
        super(exceptions, self).__init__()
        self.arg = arg

class project(object):
    """docstring for project."""

    def __init__(self, arg):
        super(project, self).__init__()
        self.arg = arg

class ClassName(object):
    """docstring for ."""

    def __init__(self, arg):
        super(, self).__init__()
        self.arg = arg

def main():
    print('hit main in am_credentials')

if __name__ == '__main__':
    main()
