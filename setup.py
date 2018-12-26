import setuptools

with open("README", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="war3structs",
  version="0.0.1-alpha",
  author="sides",
  author_email="sides@sides.tv",
  description="Python construct definitions for Warcraft III file formats",
  long_description=long_description,
  long_description_content_type="text/plain",
  url="https://github.com/warlockbrawl/war3structs",
  packages=setuptools.find_packages(),
  package_data={'': ['war3structs/storage/storm.dll', 'war3structs/storage/CascLib.dll']},
  include_package_data=True,
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows"
  ]
)
