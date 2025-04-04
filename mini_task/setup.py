from setuptools import setup
import os
from glob import glob
package_name = 'mini_task'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
   	(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
   	(os.path.join('share', package_name, 'model'), glob('model/*')),
   	(os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='awaleed152',
    maintainer_email='ahmad.abouelainein@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'CommandPublisher = mini_task.CommandPublisher:main',
            'P2PController = mini_task.P2PController:main',
        ],
    },
)
