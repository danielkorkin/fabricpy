#!/usr/bin/env python3
"""Setup script for fabricpy package."""

from setuptools import setup, find_packages
import os
import re


def read_file(filename):
    """Read file contents."""
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_version():
    """Get version from fabricpy/__version__.py or environment variable."""
    # First try to get version from environment (for CI/CD)
    version = os.environ.get('PACKAGE_VERSION')
    if version:
        return version.lstrip('v')  # Remove 'v' prefix if present
    
    # Fallback to version file
    try:
        version_file = read_file('fabricpy/__version__.py')
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
        if version_match:
            return version_match.group(1)
    except Exception:
        pass
    
    # Final fallback
    return "0.0.0"


def read_requirements(filename):
    """Read requirements from file."""
    try:
        return [line.strip() for line in read_file(filename).splitlines() 
                if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []


# Get version and basic info
VERSION = get_version()

# Read the README file for long description
long_description = read_file('README.md')

# Read development requirements
dev_requirements = read_requirements('requirements-dev.txt')

setup(
    name='fabricpy',
    version=VERSION,
    author='Daniel Korkin',
    author_email='danielkorkin@example.com',
    description='A lightweight helper library for writing Fabric mods in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/danielkorkin/fabricpy',
    project_urls={
        'Documentation': 'https://fabricpy.readthedocs.io/',
        'Source': 'https://github.com/danielkorkin/fabricpy',
        'Tracker': 'https://github.com/danielkorkin/fabricpy/issues',
        'Coverage': 'https://app.codecov.io/gh/danielkorkin/fabricpy',
        'Discussions': 'https://github.com/danielkorkin/fabricpy/discussions',
    },
    packages=find_packages(exclude=['tests*', 'docs*', 'temp*']),
    package_data={
        'fabricpy': [
            '*.md',
            '*.txt',
        ],
    },
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        # No runtime dependencies - fabricpy uses only Python standard library
    ],
    extras_require={
        'dev': dev_requirements,
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme',
        ],
        'test': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'coverage>=6.0',
            'pytest-mock>=3.10.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Java',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Framework :: Fabric',
    ],
    keywords=[
        'minecraft',
        'fabric',
        'mod',
        'modding',
        'game-development',
        'java-generation',
        'minecraft-forge',
        'minecraft-fabric',
        'mod-development',
        'code-generator',
        'python-to-java',
    ],
    entry_points={
        'console_scripts': [
            # Add command-line scripts here if needed in the future
            # 'fabricpy=fabricpy.cli:main',
        ],
    },
    zip_safe=False,
    license='MIT',
    platforms=['any'],
    
    # Metadata for PyPI
    maintainer='Daniel Korkin',
    maintainer_email='daniel.d.korkin@gmail.com',
    
    # Additional metadata
    download_url=f'https://github.com/danielkorkin/fabricpy/archive/v{VERSION}.tar.gz',
    
    # For development
    cmdclass={},
    
    # Package discovery
    package_dir={'': '.'},
)
