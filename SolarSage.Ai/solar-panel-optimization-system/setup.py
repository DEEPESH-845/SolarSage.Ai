# setup.py
"""
Setup script for Advanced Solar Panel AI Cleaning System
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced Solar Panel AI Cleaning System with Quartz Integration"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="solar-panel-ai-cleaning",
    version="3.0.0",
    author="Advanced Solar AI Team",
    author_email="solar-ai@example.com",
    description="Advanced Solar Panel AI Cleaning System with Quartz Integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/solar-ai/solar-panel-cleaning",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "gpu": [
            "tensorflow-gpu>=2.8.0",
            "torch>=1.11.0+cu113",
        ],
        "hardware": [
            "RPi.GPIO>=0.7.1",
            "gpiozero>=1.6.0",
        ],
        "visualization": [
            "matplotlib>=3.4.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
            "dash>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "solar-ai=main:main",
            "solar-ai-monitor=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml", "*.json"],
    },
    zip_safe=False,
)