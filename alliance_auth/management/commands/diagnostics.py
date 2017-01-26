from django.core.management.base import BaseCommand, CommandError

def check_version():
    import subprocess
    try:
        version = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\n')[0].split()[-1]
        if version == 'master':
            return('On development branch. Not guaranteed to work.')
    except (IndexError, AttributeError, OSError):
        return('Unable to determine codebase version.')


def check_requirements():
    import subprocess

    p = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE).communicate()[0]
    packages = [package.decode('utf-8').split('==')[0] for package in p.split()]
    packages_parsed = [p.lower() for p in packages]

    p2 = subprocess.Popen(['cat', 'requirements.txt'], stdout=subprocess.PIPE).communicate()[0]
    required = [package for package in p2.decode('utf-8').split('\n') if not package.startswith('#')]
    required_parsed = []
    for r in required:
        if r.startswith('git+'):
            r = r.split('/')[-1].split('.')[0]
        if '=' in r:
            r = r.split('=')[0]
        if '<' in r:
            r = r.split('<')[0]
        if '>' in r:
            r = r.split('>')[0]
        if r:
            required_parsed.append(r.lower())
    missing_packages = [r for r in required_parsed if r not in packages_parsed]
    if missing_packages:
        return('Missing required packages: %s\nHave you installed requirements?' % missing_packages)
    


class Command(BaseCommand):
    help = 'Runs through a series of tests to determine why auth is not working.'

    requires_system_checks = False
    can_import_settings = False
    leave_locale_alone = True

    TESTS = {
        'version': check_version,
        'requirements': check_requirements,
    }

    def add_arguments(self, parser):
        parser.add_argument('test_name', nargs='*', type=str)

    def handle(self, *args, **kwargs):
        errors = {}
        if 'test_name' in kwargs:
            for test_name in kwargs['test_name']:
                if test_name in self.TESTS:
                    status = self.TESTS[test_name]()
                    if status:
                        errors[test_name] = status
                else:
                    raise CommandError("unrecognized test '%s'" % test_name)
        else:
            for name, test in self.TESTS.items():
                status = test()
                if status:
                    errors[name] = status
        if errors:
            for name, message in errors.items():
                print('Failed %s test: %s' % (name, message))
        else:
            print('No issues identified.')
