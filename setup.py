from setuptools import setup, find_packages
from version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gate-controller',
    version=__version__,
    author='Grega Krajnc',
    author_email='grega.dev@srnjak.com',
    description='The Gate Controller Project, specifically designed for the '
                'Raspberry Pi.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/srnjak/gate-controller',
    packages=find_packages(),  # Automatically find packages
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Home Automation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
    install_requires=[
        'Flask',
        'PyYAML',
    ],
    extras_require={
        'RPi': ['RPi.GPIO'],
    },
    include_package_data=True,
    package_data={
        'gate_controller': ['config/*.yaml', 'static/*.yaml'],
    },
    entry_points={
        'console_scripts': [
            'gate-controller-server=gate_controller.server:main',
            'gate-controller=gate_controller.cli:cli',
        ],
    },
)
