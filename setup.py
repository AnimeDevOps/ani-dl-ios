from setuptools import setup, find_packages


setup(name='anidl',
      version='0.0.1',
      description='CLI Tool/Client Library for anime1.com',
      url='https://github.com/AnimeDevOps/ani-dl',
      author='AnimeDevOps',
      author_email='iwantplati@gmail.com',
      packages=find_packages(),
      install_requires=[
            'requests'
      ],
      include_package_data=True,
      zip_safe=False,
      long_description='long_description',
      long_description_content_type="text/markdown",
      classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
      ],
      scripts=['cli/ani']
      )
