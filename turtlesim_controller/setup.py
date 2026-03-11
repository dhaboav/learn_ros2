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
            f"test_node = {package_name}.my_first_node:main",
            f"draw_circle = {package_name}.draw_circle:main",
            f"pose_subs = {package_name}.pose_subs:main",
            f"turtle_controller = {package_name}.turtle_controller:main",
            f"test_drive = {package_name}.test_drive:main",
            f"action_server = {package_name}.count_until_server:main",
            f"action_client = {package_name}.count_until_client:main",
        ],
    },
)
