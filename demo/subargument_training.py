import argparse

p = argparse.ArgumentParser(description='my script')
ps = p.add_subparsers(dest='command', help='commands')
p1 = ps.add_parser(name='command1', description='my command 1')
p1.add_argument('--flag1', type=str)
p2 = ps.add_parser(name='command2', description='my command 2')
a21 =p2.add_argument_group(title='model', description='model arguments')
a21.add_argument('--flag2', type=str)
a22 =p2.add_argument_group(title='training', description='training arguments')
a22.add_argument('--flag3', type=str)

#p.parse_args(['--help'])
p.parse_args(['command1','--help'])
#p.parse_args(['command2','--help'])
#args = p.parse_args(['command2','--flag2','data2'])
#args = p.parse_args(['command2','--flag2','data2'])
print(args)
