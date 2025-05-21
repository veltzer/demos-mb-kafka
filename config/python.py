config_requires = []
dev_requires = []
install_requires = [
    "confluent-kafka",
]
build_requires = [
    "pymakehelper",
    "pydmt",
    "pyclassifiers",
    "pypitools",
    "pycmdtools",
    "flake8",
    "pylint",
    "mypy",
]
test_requires = []
requires = config_requires + install_requires + build_requires + test_requires
