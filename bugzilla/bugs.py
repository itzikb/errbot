import bugzilla
import csv
from errbot import BotPlugin, botcmd
import sys


class Bugzilla(BotPlugin):
    """Example 'Hello, world!' plugin for Errbot"""

    def __init__(self, bot, name=None):
        super(self.__class__, self).__init__(bot, name)
        self.URL = "bugzilla.redhat.com"
        self.users = {}
        with open("users.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                self.users[row[0]] = row[1]

    @botcmd
    def bzqa(self, msg, args):
        """Returns the number of bugs with the status defined
           as the first argument where the requester is the QA contact
           Example: !qa ON_QA
        """
        args = args.split()
        nick = str(msg.nick)

        if len(args) < 1:
            response = self.usage('bzqa')
            return response
        else:
            status = args[0]

        if status not in ['ON_QA', 'NEW', 'ON_DEV']:
            response = "Unrecognized status %s" % status

        elif nick in self.users:
            bzapi = bugzilla.Bugzilla(self.URL)
            query = bzapi.build_query(qa_contact=self.users[nick],
                                      status=status)
            bugs = bzapi.query(query)
            response = ("%s: You have %d bugs with status %s which you are "
                        "the QA Contact" % (nick, len(bugs), status))
        else:
            response = ("%s: You are not registred to bugs query."
                        "Please use !bzregister <email> to register" % nick)

        return response

    @botcmd
    def bzregister(self, msg, args):
        """ Register a nick name with an email used in Bugzilla
            Example: !bzregister user@example.com
        """
        args = args.split()
        nick = str(msg.nick)

        if len(args) < 1:
            response = self.usage('bzregister')
            return response
        else:
            email = args[0]
        row = [nick, email]

        with open("users.csv", 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        self.users[nick] = email
        response = "%s: Registration successful!" % nick
        return response

    def usage(self, command):
        usage_dict = {'bzqa': 'Usage: !bzqa <status>',
                      'bzregister': 'Usage: !bzregister <email>'}
        return usage_dict.get(command)
