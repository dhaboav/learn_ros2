from setuptools import find_packages, setup

package_name = "turtlesim_controller"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dhaboav",
    maintainer_email="100108392+dhaboav@users.noreply.github.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            f"turtle_act_move_server = {package_name}.turtle_action_move_server:main",
            f"turtle_act_move_client = {package_name}.turtle_action_move_client:main",
            f"turtle_service = {package_name}.turtle_service:main",
            f"turtle_math = {package_name}.turtle_math:main",
        ],
    },
)
