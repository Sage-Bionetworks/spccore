import os
import setuptools

# figure out the version
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "spccore", "__version__.py")) as f:
    exec(f.read(), about)

setuptools.setup(
    # basic
    name='spccore',
    version=about["__version__"],
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),

    # requirements
    python_requires='>=3.5.*',
    install_requires=[
        'requests>=2.21.0',
        'keyring==12.0.2',
        'deprecated==1.2.4',
    ],
    extras_require={
        'boto3' : ["boto3"],
        ':sys_platform=="linux2" or sys_platform=="linux"': ['keyrings.alt==3.1'],
    },

    # test
    setup_requires=["pytest-runner"],
    tests_require=['pytest'],

    # metadata to display on PyPI
    description="Synapse Python Client Core Package",
    url='http://synapse.sagebase.org/',
    author='The Synapse Engineering Team',
    author_email='platform@sagebase.org',
    license='Apache',
    project_urls={
        "Source Code": "https://github.com/Sage-Bionetworks/spccore",
        "Bug Tracker": "https://github.com/Sage-Bionetworks/spccore/issues",
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'],
)
