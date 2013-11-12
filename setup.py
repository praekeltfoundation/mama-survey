from setuptools import setup, find_packages

setup(
    name='mama-survey',
    version='dev',
    description='Simple Survey Django Application for askMAMA',
    long_description = open('README.md', 'r').read() + \
            open('AUTHORS.md', 'r').read() + open('CHANGELOG.md', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/mama-survey',
    packages = find_packages(),
    dependency_links = [
    ],
    install_requires = [
        'django==1.4.5',
        'django-snippetscream==0.0.7',
        'south==0.8.2',
        'photon==0.0.5',
        'jmbo==0.5.5',
        'jmbo-post'
    ],
    tests_require=[
        'django-setuptest==0.1.4',
        'mock',
    ],
    test_suite="setuptest.setuptest.SetupTestSuite",
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
