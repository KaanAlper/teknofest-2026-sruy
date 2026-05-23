# CargoBot - TEKNOFEST 2026 SRUY simulasyon imaji
# ROS 2 Humble + Gazebo Classic + Nav2 + slam_toolbox
FROM osrf/ros:humble-desktop-full

SHELL ["/bin/bash", "-c"]

# Bagimliliklar
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-nav2-simple-commander \
    ros-humble-nav2-regulated-pure-pursuit-controller \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-teleop-twist-keyboard \
    ros-humble-xacro \
    ros-humble-cv-bridge \
    python3-opencv python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws
COPY src /ws/src

# Derle
RUN source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install

# Otomatik source
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /ws/install/setup.bash" >> /root/.bashrc

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "cargobot_bringup", "simulation.launch.py", "slam:=true"]
