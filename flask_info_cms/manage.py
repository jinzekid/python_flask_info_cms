#!/Users/jasonlu/.virtualenvs/pyven3_6/bin/python
from app import app


app.run(debug=True)


"""
def make_shell_context():
    return dict(app=app, db=mongo)

manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.run()
if __name__ == '__main__':
    manager.run()
"""
