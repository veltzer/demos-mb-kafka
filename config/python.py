""" python deps for this project """

install_requires: list[str] = [
    "confluent-kafka",
]
build_requires: list[str] = [
    "pydmt",
    "pymakehelper",
    "pyclassifiers",
    "pycmdtools",
    "pylint",
    "mypy",
]
requires = install_requires + build_requires
