from setuptools import setup, find_packages

setup(
    name="bargal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "astropy~=6.1.7",
        "click~=8.2.0",
        "numpy~=2.0.0",
        "opencv_python~=4.11.0.86",
        "pandas~=2.2.3",
        "Pillow~=11.2.1",
        "Requests~=2.32.3",
        "setuptools~=70.0.0",
        "joblib~=1.2.0",
        "scikit_learn~=1.6.1",
        "tabulate~=0.9.0"
    ],
    entry_points={
        "console_scripts": [
            "bargal-imgdown=bargal.commands.download_image:main",
            "bargal-datasetdown=bargal.commands.download_dataset:main",
            "bargal-preprocess=bargal.commands.preprocess:main",
            "bargal-classify=bargal.commands.classify:main",
        ],
    },
    author="ludanortmun",
    description="A tool for barred galaxy detection and analysis",
    python_requires=">=3.7",
    include_package_data=True,
)
