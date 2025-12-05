---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
hideInToc: true
title: ROS 2 Training
author: Mischa Taylor
info: |
  ## Slidev Starter Template
  Presentation slides for developers.
# apply unocss classes to the current slide
class: text-center
# https://sli.dev/features/drawing
drawings:
  persist: false
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
# open graph
# seoMeta:
#  ogImage: https://cover.sli.dev
themeConfig:
  paginationX: r
  paginationY: t
  paginationPagesDisabled: [1]
---

# ROS 2 Training

##### Mischa Taylor | 📧 <taylor@linux.com>

<div @click="$slidev.nav.next" class="mt-12 py-1" hover:bg="white op-10">
  Press Space for next page <carbon:arrow-right />
</div>

<div class="abs-br m-6 text-xl">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="slidev-icon-btn">
    <carbon:edit />
  </button>
  <a href="https://github.com/slidevjs/slidev" target="_blank" class="slidev-icon-btn">
    <carbon:logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
hideInToc: true
routeAlias: toc
---

# Table of Contents

<Toc columns="2"/>

---
layout: section
---

# Install and configure libvirt

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# Install QEMU/KVM on Ubuntu 24.04

Install QEMU/KVM and libvirtd

```bash
sudo apt-get update
sudo apt-get install qemu-kvm libvirt-daemon-system
sudo apt-get install virtinst
```

Make sure the current user is a member of the libvirt and kvm groups

```bash
$ sudo adduser $(id -un) libvirt
Adding user '<username>' to group 'libvirt' ...
$ sudo adduser $(id -un) kvm
Adding user '<username>' to group 'kvm' ...
```

Be sure to reboot!!!!

```bash
sudo reboot
```

---
hideInToc: true
---

# Validate config

```bash
$ virt-host-validate qemu
```

X86_64-based machines will likely display a warning about cgroup devices controller support not being enabled. This allows you to apply resource management to virtual machines. For more information refer to this doc. To add cgroup 'devices' controller support, edit /etc/default/grub and change the line that looks like GRUB_CMDLINE_LINUX_DEFAULT="quiet splash" to:

```bash
# GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash intel_iommu=on systemd.unified_cgroup_hierarchy=0"
```

```bash
# amd
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash amd_iommu=on iommu=pt systemd.unified_cgroup_hierarchy=0"
```

```bash
sudo update-grub
```

---
hideInToc: true
---

# Create a definition for the host network (1 of 2)

Create XML definition

```bash
cat <<EOF > /tmp/host-network.xml
<network>
  <name>host-network</name>
  <forward mode="bridge"/>
  <bridge name="br0" />
</network>
EOF
```

Configure

```bash
$ sudo virsh net-define /tmp/host-network.xml
$ sudo virsh net-start host-network
$ sudo virsh net-autostart host-network
```

---
hideInToc: true
---

# Create a definition for the host network (2 of 2)

Verify

```bash
$ virsh net-list --all
 Name           State    Autostart   Persistent
-------------------------------------------------
 default        active   yes         yes
 host-network   active   yes         yes
```

---
hideInToc: true
---

# macvtap

Create XML definition (optional)

```bash
cat <<EOF > /tmp/macvtap-network.xml
<network>
  <name>macvtap-network</name>
  <forward mode="bridge">
    <interface dev="eno1"/>
  </forward>
</network>
EOF
```

Configure

```bash
$ virsh net-define /tmp/macvtap-network.xml
$ virsh net-start macvtap-network
$ virsh net-autostart macvtap-network
```

---
hideInToc: true
---

Verify
```bash
$ virsh net-list
 Name              State    Autostart   Persistent
----------------------------------------------------
 default           active   yes         yes
 macvtap-network   active   yes         yes
```

---
hideInToc: true
---

# Image pool

```bash
$ virsh pool-define-as \
    --name default \
    --type dir \
    --target /var/lib/libvirt/images
$ virsh pool-build default
$ virsh pool-start default
$ virsh pool-autostart default
```

```bash
$ virsh pool-list --all
$ virsh vol-list --pool default --details
```

---
hideInToc: true
---

# cloud-init image pool

Note: There is a `--cloud-init` parameter for virt-install to auto-generate the
cloud-init ISO. However there's currently a bug in virt-install <= 4.1.0 that
makes it usuable. So we manage the lifecycle manually.
https://github.com/virt-manager/virt-manager/issues/178

```bash
$ virsh pool-define-as \
    --name boot-scratch \
    --type dir \
    --target /var/lib/libvirt/boot
$ virsh pool-build boot-scratch
$ virsh pool-start boot-scratch
$ virsh pool-autostart boot-scratch
```

```bash
$ virsh pool-list --all
$ virsh vol-list --pool boot-scratch --details
```

---
hideInToc: true
---

# ISO image pool

```bash
$ virsh pool-define-as \
    --name iso \
    --type dir \
    --target /var/lib/libvirt/iso
$ virsh pool-build iso
$ virsh pool-start iso
$ virsh pool-autostart iso
```

```bash
$ virsh pool-list --all
$ virsh vol-list --pool iso --details
```

---
layout: section
---

# Spin up your first VM

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# Verify host resources

```bash
$ virsh nodeinfo
CPU model:           x86_64
CPU(s):              12
CPU frequency:       3799 MHz
CPU socket(s):       1
Core(s) per socket:  6
Thread(s) per core:  2
NUMA cell(s):        1
Memory size:         65699300 KiB
```

```bash
$ df -h
Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              6.3G  2.4M  6.3G   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv  1.8T   16G  1.7T   1% /
tmpfs                               32G     0   32G   0% /dev/shm
tmpfs                              5.0M   12K  5.0M   1% /run/lock
efivarfs                           192K   69K  119K  37% /sys/firmware/efi/efivars
tmpfs                               32G     0   32G   0% /run/qemu
/dev/nvme2n1p2                     2.0G  103M  1.7G   6% /boot
/dev/nvme2n1p1                     1.1G  6.2M  1.1G   1% /boot/efi
```

---
hideInToc: true
---

# Create directory for config files (optional)

```bash
mkdir ubuntu-server-2404
cd ubuntu-server-2404
```

---
hideInToc: true
---

# Download cloud image template and resize

```bash
$ curl -LO \
    https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
$ qemu-img info noble-server-cloudimg-amd64.img
```

```bash
$ sudo qemu-img convert \
    -f qcow2 -O qcow2 \
    noble-server-cloudimg-amd64.img \
    /var/lib/libvirt/images/ubuntu-server-2404.qcow2
$ sudo qemu-img resize -f qcow2 \
    /var/lib/libvirt/images/ubuntu-server-2404.qcow2 \
    64G
```

<!--
```
curl -LO \
  https://crake-nexus.org.boxcutter.net/repository/ubuntu-cloud-images-proxy/noble/current/noble-server-cloudimg-amd64.img
```
-->

---
hideInToc: true
---

# Define login parameters for cloud-init ISO (1 of 2)

```bash
touch network-config

cat >meta-data <<EOF
instance-id: ubuntu-server-2404
local-hostname: ubuntu-server-2404
EOF
```

---
hideInToc: true
---

# Define login parameters for cloud-init ISO (2 of 2)

```bash
cat >user-data <<EOF
#cloud-config
hostname: ubuntu-server-2404
users:
  - name: autobot
    uid: 63112
    primary_group: users
    groups: users
    shell: /bin/bash
    plain_text_passwd: superseekret
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
chpasswd: { expire: False }
ssh_pwauth: True
package_update: False
package_upgrade: false
packages:
  - qemu-guest-agent
growpart:
  mode: auto
  devices: ['/']
power_state:
  mode: reboot
EOF
```

---
hideInToc: true
---

# Generate cloud-init ISO

```bash
sudo apt-get update
sudo apt-get install genisoimage
```

```bash
$ genisoimage \
    -input-charset utf-8 \
    -output ubuntu-server-2404-cloud-init.img \
    -volid cidata -rational-rock -joliet \
    user-data meta-data network-config

sudo cp ubuntu-server-2404-cloud-init.img \
  /var/lib/libvirt/boot/ubuntu-server-2404-cloud-init.iso
```

Alternative way with cloud-localds:

```bash
sudo apt-get update
sudo apt-get install cloud-image-utils
```

```bash
sudo cloud-localds \
  /var/lib/libvirt/boot/ubuntu-server-2404-cloud-init.iso \
  user-data meta-data \
  --verbose
```

---
hideInToc: true
---

# Spin up image and configure with cloud-init

```bash
virt-install \
  --connect qemu:///system \
  --name ubuntu-server-2404 \
  --boot uefi \
  --memory 8192 \
  --vcpus 2 \
  --os-variant ubuntu24.04 \
  --disk /var/lib/libvirt/images/ubuntu-server-2404.qcow2,bus=virtio \
  --disk /var/lib/libvirt/boot/ubuntu-server-2404-cloud-init.iso,device=cdrom \
  --network network=default,model=virtio \
  --graphics spice \
  --noautoconsole \
  --console pty,target_type=serial \
  --import \
  --debug
```

---
hideInToc: true
---

# Virtual machine console

```bash
# Command line console
virsh console ubuntu-server-2404

# Graphical console
virt-viewer ubuntu-server-2404
```

---
hideInToc: true
---

# Disable cloud-init and remove cloud-init ISO

In the guest:
```bash
# login with autobot user
$ cloud-init status --wait
status: done

# Disable cloud-init
$ sudo touch /etc/cloud/cloud-init.disabled

$ cloud-init status
status: disabled
$ sudo shutdown -h now
```

On the host
```bash
$ virsh domblklist ubuntu-server-2404
$ virsh change-media ubuntu-server-2404 sda --eject
$ sudo rm /var/lib/libvirt/boot/ubuntu-server-2404-cloud-init.iso
```


---
hideInToc: true
---

# Snapshots

```bash
$ virsh snapshot-create-as --domain ubuntu-server-2404 --name clean --description "Initial install"
$ virsh snapshot-list ubuntu-server-2404
$ virsh snapshot-revert ubuntu-server-2404 clean
$ virsh snapshot-delete ubuntu-server-2404 clean
```

# Cleanup

```bash
$ virsh shutdown ubuntu-server-2404
$ virsh undefine ubuntu-server-2404 --nvram --remove-all-storage
```

---
hideInToc: true
---

# Get IP of virtual machine

Preferred - use qemu-guest-agent

```bash
virsh start ubuntu-server-2404

virsh list --all
```

```
$ virsh domifaddr ubuntu-server-2404 --source agent
```

---
layout: section
---

# Install ROS 2 Jazzy on Ubuntu 24.04

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# Set locale to UTF-8

```bash
# Check for UTF-8
$ locale charmap
UTF-8

# Set locale to UTF-8 if not set
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

---
hideInToc: true
---

# Ensure that the Ubuntu Universe repository is enabled

```bash
apt-cache policy | grep universe
````

---
hideInToc: true
---

# Add the ros repository to apt sources

```bash
sudo apt-get update
sudo apt install ca-certificates curl
export ROS_APT_SOURCE_VERSION=$(
  curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
  | grep -F "tag_name" \
  | awk -F\" '{print $4}'
)

# Download the keyring package
. /etc/os-release
curl -L \
  -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/\
${ROS_APT_SOURCE_VERSION}/\
ros2-apt-source_${ROS_APT_SOURCE_VERSION}.${UBUNTU_CODENAME:-$VERSION_CODENAME}_all.deb"

# Install only if you want to point at the upstream repos
sudo dpkg -i /tmp/ros2-apt-source.deb
```

---
hideInToc: true
---

# If you have a custom mirror

```bash
# Look at the deb contents
dpkg-deb --contents /tmp/ros2-apt-source.deb
# Extract the key from the deb
mkdir -p /tmp/ros2-apt-source
dpkg-deb -x /tmp/ros2-apt-source.deb /tmp/ros2-apt-source
# Install the keyring
sudo install -m 644 \
  /tmp/ros2-apt-source/usr/share/keyrings/ros2-archive-keyring.gpg \
  /usr/share/keyrings/
# Point at a local mirror
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-archive-keyring.gpg] \
http://mirror.local/ros2 noble main" | \
sudo tee /etc/apt/sources.list.d/ros2.list

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-archive-keyring.gpg] \
http://crake-nexus.org.boxcutter.net/repository/ros-apt-proxy noble main" | \
sudo tee /etc/apt/sources.list.d/ros2.list
```

---
hideInToc: true
---

```bash
# Install development tools
sudo apt-get update
sudo apt-get install ros-dev-tools

# Packages are upgraded every month for ROS 2
sudo apt-get update
sudo apt-get upgrade
# Desktop install
sudo apt-get install ros-jazzy-desktop
# Bare bones
sudo apt-get install ros-jazzy-ros-base
```

---
hideInToc: true
---

# Uninstall

```bash
sudo apt-get remove ~nros-jazzy-*
sudo apt-get autoremove

# Remove the repository
sudo apt remove ros2-apt-source
sudo apt update
sudo apt autoremove
sudo apt upgrade # Consider upgrading for packages previously shadowed.
```

---
hideInToc: true
---

```bash
# Create user for ROS
sudo useradd --create-home --shell /bin/bash ros
echo "ros ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee "/etc/sudoers.d/dont-prompt-ros-for-sudo-password"
sudo su - ros
```

```bash
$ source /opt/ros/jazzy/setup.bash
$ which ros2
/opt/ros/jazzy/bin/ros2

$ ros2
```

```bash
grep -qxF 'source /opt/ros/jazzy/setup.bash' ~/.bashrc || \
  echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
```

---
hideInToc: true
---

# /opt/ros/jazzy/setup.bash explained

`source /opt/ros/jazzy/setup.bash` activates a ROS 2 environment for the current shell session. It's the same idea as activating a Python virtual environment, but for ROS.

The `setup.bash` script adds the ROS tools to your PATH:

```
$ echo $PATH
/opt/ros/jazzy/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
```

The script also defines environment variables like:

```
AMENT_PREFIX_PATH
COLCON_CURRENT_PREFIX
ROS_DISTRO
ROS_VERSION
LD_LIBRARY_PATH
PYTHONPATH
```

---
hideInToc: true
---

# Test ROS 2 Install

```bash
tmux
# Ctrl+B " - Split the window horizontally
# Ctrl+B o - Cycle panes
ros2 run demo_nodes_cpp talker
# Ctrl+B o - Cycle panes
ros2 run demo_nodes_cpp listener
# Ctrl+B c
```

```bash
tmux new-session -d -s ros "ros2 run demo_nodes_cpp talker" \; \
  split-window -v "ros2 run demo_nodes_cpp listener" \; \
  attach -t ros
```

---
layout: section
---

# Get started writing ROS code

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# ROS Package

A ROS package is a small standalone project.

A ROS package is a source-level project directory with metadata, declared with `package.xml`.  It is a folder, not a binary. It is the __source unit of compilation__.

A package is NOT:
- ❌ a .deb
- ❌ an .rpm
- ❌ a system package
- ❌ something you install with apt or dnf

---
hideInToc: true
---

# Workspace

A workspace is a __local build environment__. It is intended to be disposable. The workspace stores build artifacts and should never be committed to source control:

```
ros2_ws/
├── src/       # All packages (each has its own build system)
├── build/     # Per-package build directories. DO NOT commit (generated)
├── install/   # Final artifacts. DO NOT commit (generated)
└── log/       # Logs. DO NOT commit (generated)
```

---
hideInToc: true
---

# Colcon

Colcon is a command line tool used to build and test ROS packages. It sits above CMake and builds many packages together, optimizing parallelism.

Think of it like:
- make -> builds a single target
- cmake -> generates the build system for a single project
- colcon -> builds a whole tree of CMake, Python, and other package types together, handling ordering, isolation, environment setup and build metadata.

---
hideInToc: true
---

# Why ROS needs something like colcon

ROS workspaces typically contain dozens to hundreds of packages, each possibily depending on others. Some might use CMake, some plain Python, some other tools.

You need a build tool that:
- Figures out which packages depend on what
- Builds them in the correct order
- Isolates build/test/install outputs
- Generates environment scripts
- Works constently across languages
- Lets you re-build incrementally without breaking other packages

CMake alone doesn't do this, colcon does.

---
hideInToc: true
---

# Create a workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
colcon build

$ tree -d -L 1 ~/ros2_ws
/home/ros/ros2_ws
├── build
├── install
├── log
└── src
```

---
hideInToc: true
---

# Create a Python package

```bash
cd ~/ros2_ws/src
ros2 pkg create \
  hello_python_pkg \
  --build-type ament_python \
  --license Apache-2.0 \
  --dependencies rclpy
cd ~/ros2_ws
colcon build \
  --packages-select \
  hello_python_pkg

# with `source /opt/ros/jazzy/setup.bash`
# AMENT_PREFIX_PATH=/opt/ros/jazzy
ros2 pkg list | grep hello_python_pkg

source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_python_pkg:/opt/ros/jazzy
ros2 pkg list | grep hello_python_pkg
```

---
hideInToc: true
---

# Python package structure

- `package.xml` file containing meta information about the package
- `resource/<package_name>` required empty file that signals to ROS tooling that the package exists and should be indexed
- `setup.cfg` is required when a package has executables, so `ros2 run` can find them
- `setup.py` containing instructions for how to install the package
- `<package_name>` - a directory with the same name as your package, used by ROS 2 tools to find your package, contains `__init__.py`

```
/home/ros/ros2_ws/src/hello_python_pkg
├── LICENSE
├── hello_python_pkg
│   └── __init__.py
├── package.xml
├── resource
│   └── hello_python_pkg
├── setup.cfg
├── setup.py
└── test
    ├── test_copyright.py
    ├── test_flake8.py
    └── test_pep257.py
```

---
hideInToc: true
---

# Create a C++ package

```bash
cd ~/ros2_ws/src
ros2 pkg create \
  hello_cpp_pkg \
  --build-type ament_cmake \
  --license Apache-2.0 \
  --dependencies rclcpp
cd ~/ros2_ws
colcon build \
  --packages-select \
  hello_cpp_pkg

# with `source /opt/ros/jazzy/setup.bash`
# AMENT_PREFIX_PATH=/opt/ros/jazzy
ros2 pkg list | grep hello_cpp_pkg

source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_cpp_pkg:/opt/ros/jazzy
ros2 pkg list | grep hello_cpp_pkg
```

---
hideInToc: true
---

# C++ package structure

```
- `CMakeLists.txt` file that describes how to build the code within the package
- `include/<package_name>` directory containing the public headers for the package
- `package.xml` file containing meta information about the package
- `src` directory containing the source code for the package
```

```
/home/ros/ros2_ws/src/hello_cpp_pkg
├── CMakeLists.txt
├── LICENSE
├── include
│   └── hello_cpp_pkg
├── package.xml
└── src
```


---
hideInToc: true
---

# ROS Package naming

- Lowercase alphanumeric characters plus underscores (a–z, 0–9, _)
- Must start with a letter
- No capital letters, dashes (-), or spaces
- Should be short, descriptive, and unique within the workspace
- Name must match folder name, package.xml, and any resource marker (resource/<name>)
- Used as the canonical identifier for ros2 run, ros2 pkg, and dependency resolution

---
hideInToc: true
---

# Introducing ROS Nodes

• A **workspace** is a local directory __where you build and organize your ROS code__.
• A **package** is the unit of __organization and distribution__ inside a workspace.
- A **node** is the __executable program__ inside a package that actually does work in a ROS system.
- A node is where your code lives in ROS.
- A node is something like a ROS micro-service.

---
hideInToc: true
---

# Python hello world node

```python
cat >~/ros2_ws/src/hello_python_pkg/hello_python_pkg/hello_python_node.py <<EOF
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

def main(args=None):
    rclpy.init(args=args)
    node = Node('hello_node')
    node.get_logger().info('Hello, world!')
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
EOF
```
```bash
chmod +x ~/ros2_ws/src/hello_python_pkg/hello_python_pkg/hello_python_node.py
$ ls ~/ros2_ws/src/hello_python_pkg/hello_python_pkg
__init__.py  hello_node.py
```

---
hideInToc: true
---

# Entry point (setup.py)

```bash
cat >~/ros2_ws/src/hello_python_pkg/setup.py <<EOF
from setuptools import find_packages, setup

package_name = 'hello_python_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros',
    maintainer_email='ros@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hello_python_node = hello_python_pkg.hello_python_node:main',
        ],
    },
)
EOF
```

---
hideInToc: true
---

# Run a package specific Python executable

```
cd ~/ros2_ws
colcon build --packages-select hello_python_pkg
source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_cpp_pkg:/opt/ros/jazzy
$ ros2 run hello_python_pkg hello_python_node
[INFO] [1764903922.188898944] [hello_node]: Hello, world!
```

---
hideInToc: true
---

# C++ hello world node

```bash
cat >~/ros2_ws/src/hello_cpp_pkg/src/hello_cpp_node.cpp <<EOF
#include <rclcpp/rclcpp.hpp>

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("hello_cpp_node");

    RCLCPP_INFO(node->get_logger(), "Hello, world! ");

    rclcpp::shutdown();
    return 0;
}
EOF
```

---
hideInToc: true
---

# Add executable and install rule to CMakeLists.txt

```bash
cat >~/ros2_ws/src/hello_cpp_pkg/CMakeLists.txt <<'EOF'
cmake_minimum_required(VERSION 3.8)
project(hello_cpp_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(hello_cpp_node src/hello_cpp_node.cpp)
ament_target_dependencies(hello_cpp_node rclcpp)

install(TARGETS
  hello_cpp_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
EOF
```

---
hideInToc: true
---

# Run a package specific executable

```
cd ~/ros2_ws
colcon build --packages-select hello_cpp_pkg
source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_cpp_pkg:/opt/ros/jazzy
$ ros2 run hello_cpp_pkg hello_cpp_node
[INFO] [1764904714.200800158] [hello_cpp_node]: Hello, world!
```

---
hideInToc: true
---

# Relation between a workspace and source control

A ROS workspace is like a CMake build directory on steroids. You would never check in:

- `build/` from a CMake project
- `venv/` from a Python project
- `node_modules/` from a JavaScript project

Same idea.

The only “real” part of the workspace is the `src/` tree.

---
hideInToc: true
---

# What you should put in source control

Inside `src/`, each ROS package is just a normal project folder.

```
ros_ws/
  src/
    my_robot_description/
    my_robot_bringup/
    my_sensor_driver/
    slam_utils/
```

These go into source control as:
- Individual repos OR
- A single monorepo

---
hideInToc: true
---

# What NOT to put in source control

Add this to your `.gitignore` in the root of your workspace:

```
build/
install/
log/
.colcon/
```

Why?

- These contain paths that depend on your local system (`/home/taylor/.../ros_ws/`)
- They change on every build
- They break reproducibility
- They are very large and binary
- They cause meaningless merge conflicts

---
hideInToc: true
---

# Good source control workflow

## Option 1: One repo per package

```
src/
  my_pkg      # git clone https://github.com/.../my_pkg.git
  nav_utils   # git clone https://github.com/.../nav_utils.git
```

## Option 2: Monorepo

```
src/
  my_robot/
    package1/
    package2/
    package3/
```

Both are valid. Colcon works with either

---
hideInToc: true
---

# Workspace definition files

ROS Projects often include a directory like:

```
workspaces/
   desktop.yaml
   simulation.yaml
   full-stack.yaml
   dev.yaml
```

Inside each file is a `vcstool (vcs)` “repos file” - a YAML mapping of repositories to clone.

Example (very common pattern):

```
repositories:
  navigation2:
    type: git
    url: https://github.com/ros-planning/navigation2.git
    version: humble
  slam_toolbox:
    type: git
    url: https://github.com/SteveMacenski/slam_toolbox.git
    version: main
```

You’d use it like:

```
vcs import src < workspaces/full-stack.yaml
```

This populates the `src/` folder with all the required ROS packages.

---
hideInToc: true
---

# Why some ROS projects include multiple workspace YAML definitions

Many large ROS projects support multiple build configurations:
	•	minimal workspace (core libraries only)
	•	desktop workspace (URDF, RViz, perception, etc.)
	•	simulation workspace (Gazebo/Ignition/Isaac Sim plugins)
	•	full-stack workspace (drivers + SLAM + navigation)

Each one is defined by a separate `.yaml` or `.repos` file.

This lets a developer do:

```
vcs import src < workspaces/simulation.yaml
colcon build
```

or a different configuration later.

