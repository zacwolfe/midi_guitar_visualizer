import subprocess
import sys


if __name__ == '__main__':
    pname = '/Users/zacw/code/mma/mma.py'
    fname = '/Users/zacw/Documents/tmp/fella2zz.mma'
    oname = './mma/tmp'
    # result = subprocess.run([pname, '-f', '{}/tmp.mid'.format(oname), fname ], shell=True)
    try:
        result = subprocess.run("{} -f {} {}".format(pname, '{}/tmp.mid'.format(oname), fname), shell=True, check=True)
        print('result is {} and success {}'.format(result, result.returncode == 0))
    except subprocess.CalledProcessError as e:
        print("error with code {} and msg {}".format(e.returncode, e.output))
