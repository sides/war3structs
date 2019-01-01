import setuptools

with open("README", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  install_requires=[
    'construct>=2.9',
    'lark-parser>=0.6'
  ],
  name="war3structs",
  version="0.1.2",
  author="sides",
  author_email="sides@sides.tv",
  description="Python construct definitions for Warcraft III file formats",
  long_description=long_description,
  long_description_content_type="text/plain",
  url="https://github.com/warlockbrawl/war3structs",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows"
  ]
)
