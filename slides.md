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

# Install QEMU/KVM on Ubuntu 26.04

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

`virt-install --cloud-init` generates a temporary cloud-init ISO in
`/var/lib/libvirt/boot`, attaches it for the first boot, then ejects and
deletes it automatically.

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
mkdir ubuntu-server-2604
cd ubuntu-server-2604
```

---
hideInToc: true
---

# Download cloud image template and resize

```bash
$ curl -LO \
    https://cloud-images.ubuntu.com/resolute/current/resolute-server-cloudimg-amd64.img
$ qemu-img info resolute-server-cloudimg-amd64.img
```

```bash
$ sudo qemu-img convert \
    -f qcow2 -O qcow2 \
    resolute-server-cloudimg-amd64.img \
    /var/lib/libvirt/images/ubuntu-server-2604.qcow2
$ sudo qemu-img resize -f qcow2 \
    /var/lib/libvirt/images/ubuntu-server-2604.qcow2 \
    64G
```

<!--
```
curl -LO \
  https://crake-nexus.org.boxcutter.net/repository/ubuntu-cloud-images-proxy/resolute/current/resolute-server-cloudimg-amd64.img
```
-->

---
hideInToc: true
---

# Define login parameters for cloud-init (1 of 2)

```bash
cat >meta-data <<EOF
instance-id: ubuntu-server-2604
local-hostname: ubuntu-server-2604
EOF
```

---
hideInToc: true
---

# Define login parameters for cloud-init (2 of 2)

```bash
cat >user-data <<EOF
#cloud-config
hostname: ubuntu-server-2604
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

# Spin up image and configure with cloud-init

`--cloud-init` builds the cloud-init ISO from `user-data` and `meta-data` for you.

```bash
virt-install \
  --connect qemu:///system \
  --name ubuntu-server-2604 \
  --boot uefi \
  --memory 8192 \
  --vcpus 2 \
  --os-variant ubuntu-lts-latest \
  --disk /var/lib/libvirt/images/ubuntu-server-2604.qcow2,bus=virtio \
  --cloud-init user-data=user-data,meta-data=meta-data \
  --network network=default,model=virtio \
  --graphics spice \
  --noautoconsole \
  --console pty,target_type=serial \
  --import
```

`ubuntu26.04` isn't in the osinfo database yet, so use `ubuntu-lts-latest`
(see `virt-install --osinfo list | grep ubuntu`).

---
hideInToc: true
---

# Virtual machine console

```bash
# Command line console
virsh console ubuntu-server-2604

# Graphical console
virt-viewer ubuntu-server-2604
```

---
hideInToc: true
---

# First boot

cloud-init runs on the first boot, installs `qemu-guest-agent`, then reboots.
virt-install treats that first boot as the install, so the VM powers off
instead of restarting. virt-install also ejects and deletes the generated
cloud-init ISO.

```bash
$ virsh domstate ubuntu-server-2604
shut off
$ virsh domblklist ubuntu-server-2604
 Target   Source
------------------------------------------------------------
 vda      /var/lib/libvirt/images/ubuntu-server-2604.qcow2
 sda      -

$ virsh start ubuntu-server-2604
```

In the guest, cloud-init disables itself because its data source is gone:

```bash
$ cloud-init status
status: disabled
```


---
hideInToc: true
---

# Snapshots

```bash
$ virsh snapshot-create-as --domain ubuntu-server-2604 --name clean --description "Initial install"
$ virsh snapshot-list ubuntu-server-2604
$ virsh snapshot-revert ubuntu-server-2604 clean
$ virsh snapshot-delete ubuntu-server-2604 clean
```

# Cleanup

```bash
$ virsh shutdown ubuntu-server-2604
$ virsh undefine ubuntu-server-2604 --nvram --remove-all-storage
```

---
hideInToc: true
---

# Get IP of virtual machine

Preferred - use qemu-guest-agent

```bash
virsh start ubuntu-server-2604

virsh list --all
```

```
$ virsh domifaddr ubuntu-server-2604 --source agent
```

---
layout: section
---

# Install ROS 2 Lyrical on Ubuntu 26.04

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
```

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
http://mirror.local/ros2 resolute main" | \
sudo tee /etc/apt/sources.list.d/ros2.list

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros2-archive-keyring.gpg] \
http://crake-nexus.org.boxcutter.net/repository/ros-apt-proxy resolute main" | \
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
sudo apt-get install ros-lyrical-desktop
# Bare bones
sudo apt-get install ros-lyrical-ros-base
```

---
hideInToc: true
---

# Uninstall

```bash
sudo apt-get remove ~nros-lyrical-*
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
$ source /opt/ros/lyrical/setup.bash
$ which ros2
/opt/ros/lyrical/bin/ros2

$ ros2
```

```bash
grep -qxF 'source /opt/ros/lyrical/setup.bash' ~/.bashrc || \
  echo 'source /opt/ros/lyrical/setup.bash' >> ~/.bashrc
```

---
hideInToc: true
---

# /opt/ros/lyrical/setup.bash explained

`source /opt/ros/lyrical/setup.bash` activates a ROS 2 environment for the current shell session. It's the same idea as activating a Python virtual environment, but for ROS.

The `setup.bash` script adds the ROS tools to your PATH:

```bash
$ echo $PATH
/opt/ros/lyrical/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
```

The script also defines environment variables like:

```bash
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

# with `source /opt/ros/lyrical/setup.bash`
# AMENT_PREFIX_PATH=/opt/ros/lyrical
ros2 pkg list | grep hello_python_pkg

source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_python_pkg:/opt/ros/lyrical
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
- `<package_name>/py.typed` - marker file declaring the package ships type hints (checked by the generated `test_mypy.py`)

```
/home/ros/ros2_ws/src/hello_python_pkg
├── LICENSE
├── hello_python_pkg
│   ├── __init__.py
│   └── py.typed
├── package.xml
├── resource
│   └── hello_python_pkg
├── setup.cfg
├── setup.py
└── test
    ├── test_copyright.py
    ├── test_flake8.py
    ├── test_mypy.py
    ├── test_pep257.py
    └── test_xmllint.py
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

# with `source /opt/ros/lyrical/setup.bash`
# AMENT_PREFIX_PATH=/opt/ros/lyrical
ros2 pkg list | grep hello_cpp_pkg

source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_cpp_pkg:/opt/ros/lyrical
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
- Name must match folder name, package.xml, and any resource marker (resource/&lt;name&gt;)
- Used as the canonical identifier for ros2 run, ros2 pkg, and dependency resolution

---
hideInToc: true
---

# Introducing ROS Nodes

- A **workspace** is a local directory __where you build and organize your ROS code__.
- A **package** is the unit of __organization and distribution__ inside a workspace.
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
__init__.py  hello_python_node.py  py.typed
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
    package_data={'': ['py.typed']},
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

```bash
cd ~/ros2_ws
colcon build --packages-select hello_python_pkg
source ~/ros2_ws/install/setup.bash
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_python_pkg:/opt/ros/lyrical
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
cmake_minimum_required(VERSION 3.20)
project(hello_cpp_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(hello_cpp_node src/hello_cpp_node.cpp)
target_link_libraries(hello_cpp_node PUBLIC rclcpp::rclcpp)

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
# AMENT_PREFIX_PATH=/home/ros/ros2_ws/install/hello_cpp_pkg:/opt/ros/lyrical
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
    url: https://github.com/ros-navigation/navigation2.git
    version: lyrical
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
	-	minimal workspace (core libraries only)
	-	desktop workspace (URDF, RViz, perception, etc.)
	-	simulation workspace (Gazebo/Ignition/Isaac Sim plugins)
	-	full-stack workspace (drivers + SLAM + navigation)

Each one is defined by a separate `.yaml` or `.repos` file.

This lets a developer do:

```
vcs import src < workspaces/simulation.yaml
colcon build
```

or a different configuration later.

---
hideInToc: true
---

# Delivering your ROS code to robots in production

There are three primary approaches to packaging and delivery your robotics software.

1. Traditional ROS 2
2. Docker/Container-based
3. Nix-based

Each have their pros and cons. There is no one-best fit solution. You'll have to choose which works best for your particular situation.

---
layout: section
---

# Remote access to ROS with LiveKit

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# What is LiveKit?

LiveKit is an open source (Apache 2.0) real-time media server built on WebRTC. You can self-host it or use the hosted LiveKit Cloud.

- A **room** is a session that **participants** join
- Participants publish and subscribe to **tracks**: video, audio, and data
- The server is an SFU (Selective Forwarding Unit): it routes tracks between participants without decoding them
- WebRTC handles NAT traversal, encryption, congestion control and adaptive bitrate
- SDKs exist for browsers, mobile, Python, Rust, Go, and C++

Access is controlled with **tokens**: short-lived JWTs that grant one identity access to one room.

---
hideInToc: true
---

# Why LiveKit?

WebRTC is built into every browser, but a real-time video product needs much more than the WebRTC API:

- **Signaling**: a server to set up connections between participants
- **NAT traversal**: STUN/TURN servers so peers behind firewalls can connect
- **Scaling**: peer-to-peer breaks down past a few participants; an SFU forwards each stream once per subscriber
- **Quality**: simulcast and adaptive bitrate for slow or changing networks
- **Auth, SDKs, recording, monitoring**

LiveKit packages all of this:

- Open source (Apache 2.0): self-host the same server LiveKit Cloud runs
- SDKs for web, iOS, Android, Flutter, Unity, Rust, C++, Python, Go, Node.js and more
- One model (rooms, participants, tracks) for people, AI agents, phones and robots

---
hideInToc: true
zoom: 0.9
---

# The LiveKit ecosystem

| Component | What it does |
|---|---|
| **Server** | The SFU: routes audio, video and data between participants in rooms |
| **Agents** | Python/Node.js AI participants: speech-to-text → LLM → text-to-speech |
| **Egress** | Record to MP4/HLS, or livestream to YouTube/Twitch over RTMP |
| **Ingress** | Bring RTMP, WHIP, SRT or files into a room (e.g. OBS Studio) |
| **SIP** | Connects phone calls to rooms, inbound and outbound |
| **Cloud** | Hosted, globally distributed LiveKit |
| **CLI (`lk`)** | Create tokens, manage rooms, publish test media, scaffold agents |

Server, Egress, Ingress, SIP and Agents are all open source.

---
hideInToc: true
---

# What people build with LiveKit

- **Voice AI**: OpenAI built ChatGPT's Advanced Voice mode on LiveKit Cloud
- **Video AI and security**: Verkada streams security cameras for 30,000+ organizations
- **Robotics**: Skydio uses it for remote observation and teleoperation of drones
- **Call centers**: AI agents answering phone calls over SIP, handing off to humans
- **Telehealth**: video visits between patients and clinicians
- **Real-time translation**: an agent listens to one language and speaks another
- **Livestreaming and meetings**: conferencing apps, recorded with Egress, broadcast over RTMP
- **Games**: voice chat and AI-driven non-player characters

<!--
Customer examples are from livekit.com and the Agents docs as of Nov 2026.
-->

---
hideInToc: true
---

# Install the LiveKit server and CLI

```bash
# LiveKit server, installed to /usr/local/bin/livekit-server
curl -sSL https://get.livekit.io | bash

# LiveKit CLI, installed to /usr/local/bin/lk
curl -sSL https://get.livekit.io/cli | bash
```

```bash
$ livekit-server --version
livekit-server version 1.13.11
$ lk --version
lk version 2.20.1
```

Skip the server if you use LiveKit Cloud. You still need `lk` to create tokens.

---
hideInToc: true
---

# Run a development server

```bash
livekit-server --dev --enable_participant_data_blob
```

- `--dev` uses the fixed credentials `devkey` / `secret`
- `--enable_participant_data_blob` is required by ROS Portal to share message schemas
- Listens on `ws://127.0.0.1:7880`. Media uses 7881/TCP and 7882/UDP
- Add `--bind 0.0.0.0` to reach it from other machines

```
INFO  livekit  starting in development mode
INFO  livekit  no keys provided, using placeholder keys {"API Key": "devkey", "API Secret": "secret"}
INFO  livekit  starting LiveKit server {"portHttp": 7880, "rtc.portTCP": 7881, "rtc.portUDP": {"Start":7882,"End":0}}
```

Never use `--dev` on a server reachable from the internet.

---
hideInToc: true
---

# Try LiveKit without ROS

With the dev server running, publish a looping demo video from the CLI:

```bash
export LIVEKIT_URL=ws://127.0.0.1:7880
lk room join --identity bot_user --publish-demo --dev test_room
```

In another terminal, inspect the room and send a message to everyone in it:

```bash
$ lk room list --dev
│ RoomID          │ Name      │ Participants │ Publishers │
│ RM_GG4GzXGeWXuF │ test_room │ 1            │ 1          │

$ lk room participants list --dev test_room
bot_user (ACTIVE)	 tracks: 1

$ lk room send-data --dev --room test_room "hello from lk"
successfully sent data to room test_room
```

---
hideInToc: true
zoom: 0.68
---

# A Python participant

Save as `~/livekit/viewer.py`:

```python
import asyncio, os
from livekit import rtc        # pip install livekit

async def count_frames(stream):
    n = 0
    async for event in stream:
        n += 1
        if n % 300 == 0:
            print(f"{n} frames, {event.frame.width}x{event.frame.height}")

async def main():
    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track(track, publication, participant):
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            print(f"video '{publication.name}' from {participant.identity}")
            asyncio.ensure_future(count_frames(rtc.VideoStream(track)))

    @room.on("data_received")
    def on_data(packet):
        print(f"data: {packet.data.decode()}")

    await room.connect(os.environ["LIVEKIT_URL"], os.environ["LIVEKIT_TOKEN"])
    print(f"connected to '{room.name}' as {room.local_participant.identity}")
    await asyncio.sleep(60)
    await room.disconnect()

asyncio.run(main())
```

---
hideInToc: true
---

# Run the Python participant

```bash
sudo apt-get install python3-venv
python3 -m venv ~/livekit/venv
~/livekit/venv/bin/pip install livekit

export LIVEKIT_URL=ws://127.0.0.1:7880
export LIVEKIT_TOKEN=$(lk token create --join --room test_room \
  --identity python_viewer --valid-for 1h --token-only --yes --dev)
~/livekit/venv/bin/python ~/livekit/viewer.py
```

```
connected to 'test_room' as python_viewer
video 'demo' from bot_user
300 frames, 1280x720
600 frames, 1280x720
data: hello from lk
900 frames, 1280x720
```

Each frame is a decoded `rtc.VideoFrame`: the starting point for computer vision, recording, or an AI agent that watches a camera.

---
hideInToc: true
---

# Why use LiveKit with ROS?

ROS 2 uses DDS, which was designed for a single local network:

- Discovery uses multicast, which doesn't cross routers, NAT, or the internet
- Exposing DDS on a public network is a security risk
- DDS has no notion of adapting video quality to a slow link

LiveKit gives you a secure, low-latency path out of the robot's network:

- **Teleoperation**: stream cameras to an operator, send `cmd_vel` back
- **Remote monitoring**: watch telemetry from anywhere, including a browser
- **Robot-to-cloud**: run inference or recording on another machine

---
hideInToc: true
zoom: 0.9
---

# Other ways to reach a robot

| Approach | Good for | Limits |
|---|---|---|
| DDS over a VPN | Same ROS tools everywhere | Discovery traffic is chatty over a VPN; no adaptive video; every node is reachable |
| rosbridge / foxglove_bridge | Visualization and debugging in a browser | Single WebSocket (TCP) connection that needs an open port or tunnel; images sent as messages, not video codecs |
| Zenoh (`rmw_zenoh`) | Routing ROS traffic across networks | Data only: no WebRTC video stack or browser/mobile media clients |
| LiveKit + ROS Portal | Teleoperation, live video, many remote viewers | Extra infrastructure (a LiveKit server or Cloud); early-access ROS integration |

These combine well: for example Foxglove for engineers debugging, LiveKit for operators driving with live video.

---
hideInToc: true
---

# LiveKit Portal for ROS

[`livekit/ros-portal`](https://github.com/livekit/ros-portal) is a ROS 2 node that connects a ROS graph to a LiveKit room.

| ROS | LiveKit |
|---|---|
| Topics (any message type) | Data tracks |
| `sensor_msgs/Image` topics | Video tracks |
| Remote video tracks | `sensor_msgs/CompressedImage` (JPEG) |
| Services | RPC calls to a named participant |
| `ros2 topic list`, `ros2 service call`, ... | Remote CLI services under `/ros_portal/` |

Supports Humble, Jazzy, Kilted, and Lyrical on amd64 and arm64.

Early access: configuration may change between releases.

---
hideInToc: true
---

# How the pieces fit together

Two ROS graphs on different `ROS_DOMAIN_ID`s share no DDS traffic. The LiveKit room is their only connection.

```
 Robot (ROS_DOMAIN_ID=42)              Operator (ROS_DOMAIN_ID=100)
┌──────────────────────────┐          ┌──────────────────────────┐
│ turtlesim_node           │          │ ros2 topic pub cmd_vel   │
│ cam2image (/image)       │          │ ros2 topic echo pose     │
│          │               │          │          │               │
│   ros_portal_node        │          │   ros_portal_node        │
│   identity: turtle_sim   │          │   identity: controller   │
└──────────┬───────────────┘          └──────────┬───────────────┘
           │        ┌────────────────────┐       │
           └───────►│  livekit-server    │◄──────┘
                    │  room: turtle_room │
                    └────────────────────┘
```

In production the robot and operator are on different networks and the server is in the cloud.

---
hideInToc: true
---

# Install ROS Portal

The `.deb` packages are published on GitHub Releases (not in the ROS apt repo yet):

```bash
# Portal is built against current ROS packages: upgrade first
sudo apt-get update && sudo apt-get upgrade
export PORTAL_VERSION=$(
  curl -s https://api.github.com/repos/livekit/ros-portal/releases/latest \
  | grep -F "tag_name" \
  | awk -F\" '{print $4}'
)
curl -LO "https://github.com/livekit/ros-portal/releases/download/\
${PORTAL_VERSION}/\
ros-${ROS_DISTRO}-livekit-portal_${PORTAL_VERSION#v}-1_$(dpkg --print-architecture).deb"
sudo apt install ./ros-${ROS_DISTRO}-livekit-portal_*.deb
```

Installs to `/opt/livekit/ros/<distro>`, an overlay on top of `/opt/ros/<distro>`:

```bash
$ source /opt/livekit/ros/lyrical/setup.bash
$ ros2 pkg prefix ros_portal
/opt/livekit/ros/lyrical/ros_portal
```

<!--
If ros_portal_node dies with "symbol lookup error ... undefined symbol",
the ROS packages are older than the ones the .deb was built against: run
apt-get upgrade. As of Nov 2026 (v0.3.0) the livekit/ros-portal:lyrical
Docker image has this problem, so use the .deb on Lyrical.
-->

---
hideInToc: true
---

# Create tokens

Each ROS Portal joins the room with its own identity:

```bash
export LIVEKIT_URL=ws://127.0.0.1:7880

lk token create \
  --join \
  --room turtle_room \
  --identity turtle_sim \
  --allow-update-metadata \
  --valid-for 24h \
  --token-only \
  --yes \
  --dev
```

- `--dev` signs the token with the dev server's `devkey` / `secret`
- For LiveKit Cloud, drop `--dev`, set `LIVEKIT_URL=wss://<project>.livekit.cloud`, and export `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`
- ROS Portal reads only `LIVEKIT_URL` and `LIVEKIT_TOKEN`
- In production, use `LIVEKIT_TOKEN_ENDPOINT` to fetch tokens from your own backend

---
hideInToc: true
---

# Configure the robot side

`direction` is from the point of view of the ROS graph: `out` sends to LiveKit, `in` receives from LiveKit. Topic patterns are regular expressions.

```bash
mkdir -p ~/livekit
cat >~/livekit/turtle_sim.yaml <<'EOF'
ros_portal:
  version: "0.0.1"
  topics:
    # Velocity commands from the operator (LiveKit -> ROS)
    - topic: "/turtle.*/cmd_vel"
      direction: "in"
    # Pose telemetry to the operator (ROS -> LiveKit)
    - topic: "/turtle.*/pose"
      direction: "out"
    # sensor_msgs/Image topics are sent as video tracks
    - topic: "/image"
      direction: "out"
EOF
```

Without `config_path`, ROS Portal forwards every topic in both directions.

---
hideInToc: true
---

# Configure the operator side

The mirror image of the robot config, plus a service route:

```bash
cat >~/livekit/controller.yaml <<'EOF'
ros_portal:
  version: "0.0.1"
  topics:
    - topic: "/turtle.*/cmd_vel"
      direction: "out"
    - topic: "/turtle.*/pose"
      direction: "in"
    # Video track names must match exactly (no regex)
    - topic: "/image"
      direction: "in"
  services:
    # Creates a local service that forwards calls to turtle_sim
    - service: "/turtle1/teleport_absolute"
      direction: "out"
      participant: "turtle_sim"
      msg_type: "turtlesim_msgs/srv/TeleportAbsolute"
EOF
```

In Lyrical, turtlesim's interfaces live in the `turtlesim_msgs` package.

---
hideInToc: true
---

# Start the robot side

Each block in its own terminal (or tmux pane):

```bash
sudo apt-get install ros-lyrical-turtlesim ros-lyrical-image-tools
export ROS_DOMAIN_ID=42
ros2 run turtlesim turtlesim_node   # add `-platform offscreen` if headless
```

```bash
export ROS_DOMAIN_ID=42
ros2 run image_tools cam2image --ros-args -p burger_mode:=true
```

```bash
export ROS_DOMAIN_ID=42
source /opt/livekit/ros/lyrical/setup.bash
export LIVEKIT_URL=ws://127.0.0.1:7880
export LIVEKIT_TOKEN=$(lk token create --join --room turtle_room \
  --identity turtle_sim --allow-update-metadata --valid-for 24h \
  --token-only --yes --dev)
ros2 launch ros_portal ros_portal.launch.py \
  config_path:=$HOME/livekit/turtle_sim.yaml
```

---
hideInToc: true
---

# Start the operator side

```bash
export ROS_DOMAIN_ID=100
source /opt/livekit/ros/lyrical/setup.bash
export LIVEKIT_URL=ws://127.0.0.1:7880
export LIVEKIT_TOKEN=$(lk token create --join --room turtle_room \
  --identity controller --allow-update-metadata --valid-for 24h \
  --token-only --yes --dev)
ros2 launch ros_portal ros_portal.launch.py \
  config_path:=$HOME/livekit/controller.yaml
```

The robot's topics now appear in the operator's graph:

```bash
# [INFO] [ros_portal.connection]: Connected to LiveKit room 'turtle_room' ...
$ export ROS_DOMAIN_ID=100
$ ros2 topic list
/diagnostics
/image
/parameter_events
/rosout
/turtle1/pose
```

---
hideInToc: true
---

# Drive the turtle over LiveKit

From the operator domain, use the normal ROS tools:

```bash
export ROS_DOMAIN_ID=100

# Watch the pose coming from the robot
ros2 topic echo /turtle1/pose

# Drive in a circle
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 1.8}}"

# Call the robot's service through the configured route
ros2 service call /turtle1/teleport_absolute \
  turtlesim_msgs/srv/TeleportAbsolute "{x: 5.0, y: 5.0, theta: 0.0}"
```

Or with the keyboard:

```bash
sudo apt-get install ros-lyrical-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

---
hideInToc: true
---

# Run ros2 commands on the remote robot

ROS Portal exposes services that run `ros2` commands on another participant's graph, with no config needed:

```bash
export ROS_DOMAIN_ID=100
ros2 service call /ros_portal/ros2_topic_list \
  ros_portal_msgs/srv/Ros2TopicList \
  "{participant_id: turtle_sim, show_types: true}"

ros2 service call /ros_portal/ros2_service_call \
  ros_portal_msgs/srv/Ros2ServiceCall \
  "{participant_id: turtle_sim, service: /spawn, msg_type: turtlesim_msgs/srv/Spawn,
    payload: '{x: 2.0, y: 2.0, theta: 0.0, name: turtle2}'}"
```

```
output='/image [sensor_msgs/msg/Image]\n/turtle1/cmd_vel [geometry_msgs/msg/Twist]\n...'
output='name: turtle2'
```

Also available: `ros2_service_list`, `ros2_interface_show`, `ros2_topic_pub`.

---
hideInToc: true
---

# Video

The robot's `sensor_msgs/Image` topic is sent as a WebRTC video track and arrives on the operator as a JPEG `sensor_msgs/CompressedImage`:

```bash
$ export ROS_DOMAIN_ID=100
$ ros2 topic info /image
Type: sensor_msgs/msg/CompressedImage
Publisher count: 1

$ ros2 topic hz /image
average rate: 10.401
```

- Outbound images must be `rgb8`, `bgr8`, `rgba8`, `bgra8`, or `mono8`, or a JPEG `CompressedImage`
- The track resolution is fixed by the first frame
- The operator's portal pauses the track when nothing subscribes to `/image`
- `video_sources` in the config can stream a camera straight from a GStreamer pipeline (e.g. `v4l2src`) without going through ROS

---
hideInToc: true
---

# Going to production

- **Server**: LiveKit Cloud, or self-host with real API keys, TLS (`wss://`), and open media ports
- **Tokens**: point robots at a token endpoint (`LIVEKIT_TOKEN_ENDPOINT`) instead of long-lived tokens
- **Bandwidth**: forward only what you need. Use `direction`, and `max_rate_hz` to throttle high-rate topics
- **Static data**: mark `/tf_static` with `latched: true` so late joiners still get it
- **Composition**: `ros_portal_composable.launch.py` loads the portal into a component container for zero-copy with camera drivers
- **Docker**: `livekit/ros-portal:<distro>` images exist; run with `--network host` so DDS can see the robot's graph. As of v0.3.0 the `lyrical` image is built on outdated ROS packages and the node fails to start, so use the `.deb` on Lyrical
