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

# ROS 2 networking: DDS and middleware

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
zoom: 0.8
---

# What is DDS?

DDS (Data Distribution Service) is an open standard for publish/subscribe messaging, used in robotics, defense, and industrial systems. ROS 2 is built on top of it.

- **No master**: unlike ROS 1's `roscore`, every process finds its peers itself (**discovery**)
- **Participants** join a **domain**, then advertise their publishers and subscribers
- **RTPS** is the wire protocol, so different DDS vendors can talk to each other
- **QoS** (quality of service) policies decide how data is delivered: reliable or best effort, kept for late joiners or not, how much history

What a ROS 2 node looks like on the network:

| ROS 2 | DDS |
|---|---|
| `ROS_DOMAIN_ID` | domain |
| process with nodes | participant |
| topic | topic (+ type) |
| publisher / subscription | data writer / data reader |
| QoS profile | QoS policies |

---
hideInToc: true
zoom: 0.8
---

# The middleware is swappable: RMW

```
your node (rclcpp / rclpy)
        │
       rcl
        │
       rmw  ◄── RMW_IMPLEMENTATION picks the implementation at runtime
   ┌────┴─────────────┬─────────────────┬─────────────────┐
 Fast DDS        Cyclone DDS          Zenoh         Connext DDS
```

Every one of these is **Tier 1** on Lyrical:

| RMW | Product | License | Notes |
|---|---|---|---|
| `rmw_fastrtps_cpp` | eProsima Fast DDS | Apache 2 | **Default**, always installed |
| `rmw_cyclonedds_cpp` | Eclipse Cyclone DDS | EPL 2.0 | `ros-lyrical-rmw-cyclonedds-cpp` |
| `rmw_zenoh_cpp` | Eclipse Zenoh | EPL 2.0 | Not DDS; `ros-lyrical-rmw-zenoh-cpp` |
| `rmw_connextdds` | RTI Connext DDS | Commercial / research | Connext installed separately; not on arm64 |

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp     # per shell, or in ~/.bashrc
ros2 run demo_nodes_cpp talker
```

---
hideInToc: true
---

# How DDS discovery works

1. Each participant **multicasts** "I'm here" to `239.255.0.1` on the domain's discovery port
2. Peers reply, then exchange their publishers and subscribers by **unicast**
3. Matching publisher/subscriber pairs (same topic, type, compatible QoS) start sending data

Ports are derived from the domain ID: `7400 + 250 × domain` for discovery multicast, then unicast ports just above it.

```bash
# what a Fast DDS talker opened, measured on the VM
ROS_DOMAIN_ID=0    0.0.0.0:7400  0.0.0.0:7414  0.0.0.0:7415  ...
ROS_DOMAIN_ID=42   0.0.0.0:17900 0.0.0.0:17910 0.0.0.0:17911 ...
```

Multicast is the weak spot: Wi-Fi access points, VPNs, cloud networks and Docker's bridge network often drop it.

---
hideInToc: true
---

# Check the network first

```bash
# machine A
ros2 multicast receive
# machine B
ros2 multicast send
```

```
Waiting for UDP multicast datagram...
Received from 10.63.45.217:38395: 'Hello World!'
```

If this fails, DDS discovery with default settings will fail too. Then:

```bash
ros2 doctor --report | grep -A3 middleware   # which RMW is active
ros2 topic list                              # do you see the other machine's topics?
ros2 topic info --verbose /chatter           # publishers, subscribers and their QoS
```

`ros2 topic list` uses a background daemon that caches the graph: after changing networking variables, run `ros2 daemon stop`.

---
hideInToc: true
---

# `ROS_DOMAIN_ID`: separate robots on one network

```bash
export ROS_DOMAIN_ID=42
```

Nodes only see nodes with the same domain ID, so teams and robots sharing a network don't cross-talk.

Tested between the VM (talker) and the host (listener):

| VM | Host | Result |
|---|---|---|
| domain 42 | domain 0 | nothing received |
| domain 42 | domain 42 | received |

- Pick **0 to 101**: higher IDs can collide with Linux's ephemeral ports (32768 to 60999); the maximum is 232
- It's isolation, not security: anyone on the network can join your domain

---
hideInToc: true
zoom: 0.78
---

# Limit discovery: range and static peers

```bash
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST   # SUBNET (default) | LOCALHOST | OFF | SYSTEM_DEFAULT
export ROS_STATIC_PEERS="10.63.45.81;robot2.local"
```

- `SUBNET`: discover anything reachable by multicast
- `LOCALHOST`: only this machine, plus any static peers
- `OFF`: discover nothing, not even on the same machine. Static peers are ignored too

Tested between the VM (publisher) and the host (subscriber):

| VM | Host | Result |
|---|---|---|
| default | `LOCALHOST` | nothing received |
| default | `LOCALHOST` + `ROS_STATIC_PEERS=10.63.45.81` | received |
| `OFF` | `OFF` + static peer | nothing received |
| `OFF` + static peer | `OFF` + static peer | nothing received |

`LOCALHOST` + static peers is the way to connect to specific machines without multicast. These variables work for the DDS middlewares, not Zenoh.

---
hideInToc: true
zoom: 0.85
---

# QoS must be compatible

```bash
ros2 topic pub -r 5 --qos-reliability best_effort /qos_demo std_msgs/msg/String "{data: hi}"
ros2 topic echo --qos-reliability reliable /qos_demo std_msgs/msg/String
```

```
[WARN] [_ros2cli_36300]: New publisher discovered on topic '/qos_demo', offering
       incompatible QoS. No messages will be received from it. Last incompatible policy: RELIABILITY
```

| Policy | Options | Rule |
|---|---|---|
| Reliability | `RELIABLE`, `BEST_EFFORT` | A reliable reader needs a reliable writer |
| Durability | `TRANSIENT_LOCAL`, `VOLATILE` | A transient-local reader needs a transient-local writer |
| History / depth | `KEEP_LAST(n)`, `KEEP_ALL` | Size of the queue |

- Sensors usually publish **best effort** (`SensorDataQoS`): subscribe with best effort too
- Maps and `/tf_static` use **transient local**, so late joiners still get the last message
- `ros2 topic info --verbose` shows each endpoint's QoS

---
hideInToc: true
zoom: 0.62
---

# Fast DDS, Cyclone DDS or Zenoh?

| | Fast DDS (default) | Cyclone DDS | Zenoh |
|---|---|---|---|
| Install | Always installed | One apt package | One apt package + run a router |
| Discovery | Multicast; optional **discovery server** | Multicast; unicast **peers** in XML | **Router** (TCP 7447); no multicast needed |
| Config | XML profiles, environment variables | One XML via `CYCLONEDDS_URI` | JSON5 config, `ZENOH_CONFIG_OVERRIDE` |
| Same-host transport | Shared memory by default | UDP by default; shared memory needs extra setup | Configurable |
| Talks to other DDS | Yes (RTPS) | Yes (RTPS) | No: Zenoh nodes only |
| Across Wi-Fi, NAT, internet | Hard (multicast); use discovery server | Hard; needs peers on both sides | Easiest: routers connect over TCP |
| Docker | Pitfall: shared memory across containers | Worked out of the box in our tests | Router per host |
| Discovery range variables | Supported | Supported | Not supported |

**Fast DDS**: nothing to install and the most features, but more surprises: the shared-memory trap in Docker and verbose XML.

**Cyclone DDS**: small and predictable, one readable config file; the most common alternative to the default. You must list unicast peers on every machine.

**Zenoh**: designed for networks DDS struggles with (Wi-Fi, fleets, cloud). Needs a router, and can't talk to DDS nodes.

Pick one per system and use it everywhere.

---
hideInToc: true
zoom: 0.82
---

# Mixing middlewares

Tested with the VM talker and host listener, each line for 10 s at 1 message/s:

| Talker (VM) | Listener (host) | Messages |
|---|---|---|
| Fast DDS | Fast DDS | 10 |
| Cyclone DDS | Cyclone DDS | 10 |
| Fast DDS | Cyclone DDS | 9 |
| Zenoh | Zenoh, no router | 0 |
| Zenoh | Fast DDS | 0 |
| Zenoh (router per host) | Zenoh | 10 |

- DDS vendors interoperate over RTPS, but QoS details and performance tuning differ: don't rely on mixing them
- Zenoh is a different protocol, so it never talks to DDS nodes directly (a `zenoh-bridge-ros2dds` can translate)
- Setting `RMW_IMPLEMENTATION` everywhere (launch files, systemd units, containers) avoids accidental mixes

---
hideInToc: true
zoom: 0.85
---

# Fast DDS example: discovery server

When multicast doesn't work (Wi-Fi, cloud, VPN), run one central server instead:

```bash
# on 10.63.45.217
fastdds discovery --server-id 0
```

```
#### Server started ####
  Running on:  UDPv4:[0.0.0.0]:11811
```

```bash
# on every machine that should join (VM talker, host listener, ...)
export ROS_DISCOVERY_SERVER=10.63.45.217:11811
ros2 run demo_nodes_cpp talker
```

- Our test: VM talker → host listener through the server: received
- Nodes without `ROS_DISCOVERY_SERVER` don't see nodes that use it
- `ros2` CLI tools: set the same variable; add `ROS_SUPER_CLIENT=true` if the graph looks incomplete. Use `--spin-time 5` with `--no-daemon`, discovery takes a moment
- Discovery traffic goes to one server instead of every participant, which also scales better

Same-host trick with containers: `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` disables shared memory (see Docker slide).

---
hideInToc: true
zoom: 0.78
---

# Cyclone DDS example: unicast only

```xml
<!-- ~/cyclonedds.xml on the VM; on the host: name="br0", peer 10.63.45.81 -->
<CycloneDDS xmlns="https://cdds.io/config">
  <Domain Id="any">
    <General>
      <Interfaces>
        <NetworkInterface name="enp1s0" />
      </Interfaces>
      <AllowMulticast>false</AllowMulticast>
    </General>
    <Discovery>
      <ParticipantIndex>auto</ParticipantIndex>
      <MaxAutoParticipantIndex>20</MaxAutoParticipantIndex>
      <Peers>
        <Peer address="10.63.45.217" />
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file://$HOME/cyclonedds.xml
```

- `NetworkInterface`: use this NIC only (stops DDS picking a Docker bridge or VPN interface)
- `ParticipantIndex auto` gives predictable ports so peers can find each other without multicast
- Tested: both machines configured → received. Only the VM configured → nothing received

---
hideInToc: true
zoom: 0.85
---

# Zenoh example: a router per host

```bash
sudo apt-get install ros-lyrical-rmw-zenoh-cpp
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
```

```bash
# host 10.63.45.217: router
ros2 run rmw_zenoh_cpp rmw_zenohd

# VM: router that connects to the host's router
ZENOH_CONFIG_OVERRIDE='connect/endpoints=["tcp/10.63.45.217:7447"]' \
  ros2 run rmw_zenoh_cpp rmw_zenohd
```

```bash
# nodes on each machine connect to their local router (tcp/localhost:7447) by default
ros2 run demo_nodes_cpp talker      # VM
ros2 run demo_nodes_cpp listener    # host
```

- Without a router, nodes don't discover each other at all, even on one machine
- Our test: router per host → 10 of 10 messages. Pointing the VM's **node** directly at the host's router connected over TCP but delivered nothing: let nodes use their local router
- Only TCP 7447 between routers: easy to open in a firewall, tunnel, or route across sites

---
hideInToc: true
zoom: 0.8
---

# ROS 2 in Docker: networking

| Setup | Result (Fast DDS default) |
|---|---|
| VM talker → container on the default **bridge** network | nothing received |
| Two containers, `--network host` | **nothing received** |
| Two containers, `--network host --ipc host` | received |
| Two containers, `--network host`, `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` | received |
| Two containers, `--network host`, Cyclone DDS | received |

- **Bridge network**: multicast doesn't cross Docker's NAT, and containers advertise private 172.17.x addresses. Use `--network host` for anything that talks to other machines
- **The shared-memory trap**: with host networking, Fast DDS sees "the same host" and switches to shared memory, but each container has its own `/dev/shm`. Discovery works, `ros2 topic list` looks fine, and no data arrives
- Fixes: `--ipc host`, `FASTDDS_BUILTIN_TRANSPORTS=UDPv4`, or Cyclone DDS
- Containers on one user-defined network (like `simnet` earlier) can discover each other, because multicast works inside one bridge

---
hideInToc: true
---

# Large messages and Wi-Fi

Images and point clouds are split into many IP fragments. Lose one fragment over Wi-Fi and the whole message waits in a kernel buffer that's 256 KB by default, which can stall a topic for up to 30 s.

```bash
# from the ROS 2 "DDS tuning" guide: starting points, tune for your system
sudo sysctl net.ipv4.ipfrag_time=3                     # default 30 s
sudo sysctl net.ipv4.ipfrag_high_thresh=134217728      # 128 MB
sudo sysctl net.core.rmem_max=8388608 net.core.rmem_default=8388608   # bigger receive buffers
```

- Make them permanent in `/etc/sysctl.d/60-ros.conf`
- Use **best effort** QoS for sensor streams
- Send compressed images (`/image/compressed`) or lower rates across machines
- Over the internet, stream video instead of raw messages (LiveKit, later)

---
hideInToc: true
zoom: 0.82
---

# Networking checklist

| Symptom | Check |
|---|---|
| Other machine's topics don't show up | Same `ROS_DOMAIN_ID`? Same `RMW_IMPLEMENTATION`? `ros2 multicast send/receive` works? Firewall? |
| Topics show up but no data | QoS mismatch (`ros2 topic info --verbose`)? Containers sharing shared memory? |
| Works on wired, fails on Wi-Fi | Multicast blocked: discovery server, static peers, or Zenoh. Fragment tuning for big messages |
| `ros2 topic list` is stale | `ros2 daemon stop` |
| Random cross-talk with other robots | Different domain IDs, or `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` |
| Container can't see the robot | `--network host` (not the default bridge) |

Set the networking variables in one place (a sourced env file, systemd `Environment=`, Docker `-e`) so every process on a robot agrees.

---
layout: section
---

# GPUs for ROS

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
zoom: 0.85
---

# What a GPU is good at

A CPU has a few fast cores for branching, sequential work. A GPU has thousands of simple cores that run the **same instruction on lots of data** at once.

| | CPU (host) | RTX 3060 Ti (our test GPU) |
|---|---|---|
| Cores | 6 to 16 | 38 SMs × 128 = 4,864 CUDA cores |
| Memory | System RAM, large | 8 GB VRAM, ~450 GB/s |
| Good at | Control flow, I/O, small tasks | Matrices, pixels, points, neural networks |

- Data has to be **copied** between system RAM and VRAM over PCIe, which is slow compared to either memory
- Work is launched as **kernels**: small functions run by thousands of threads
- GPUs also have fixed-function blocks: video encode/decode (NVENC/NVDEC, VA-API), ray tracing, tensor cores

The art of GPU programming is keeping data on the GPU and giving it enough work at once.

---
hideInToc: true
zoom: 0.72
---

# Why ROS uses GPUs

| Workload | Examples |
|---|---|
| Perception / AI inference | Object detection, segmentation, depth from stereo, VLA and LLM models |
| Point clouds | Voxel filtering, registration, ground removal on lidar data |
| Mapping and SLAM | Visual odometry, nvblox, dense reconstruction |
| Simulation | Gazebo sensor rendering, Isaac Sim (RTX only) |
| Video | Compress camera streams for recording or remote teleop (LiveKit) |

We already saw it in this course: Gazebo rendering on the GPU instead of the CPU

| Where | Rendering | `gz-sim-main` CPU |
|---|---|---|
| Docker on the host, no EGL vendor file | CPU (Mesa) | 164% |
| Docker on the host, NVIDIA EGL | GPU | 89% |
| Course VM, no GPU | CPU (`LIBGL_ALWAYS_SOFTWARE=1`) | 107% |
| Course VM, GPU passed through | GPU | 47% |

---
hideInToc: true
zoom: 0.8
---

# The GPU software stack

| Layer | NVIDIA | AMD | Intel | Apple |
|---|---|---|---|---|
| Kernel driver | `nvidia` (open or proprietary modules) | `amdgpu` (in Linux) | `i915` / `xe` (in Linux) | Built into macOS |
| Compute | **CUDA** | **ROCm / HIP** | oneAPI / SYCL, OpenVINO | **Metal** |
| AI libraries | cuDNN, TensorRT | MIOpen, MIGraphX | OpenVINO | Core ML, MPS |
| Graphics | OpenGL/Vulkan (NVIDIA driver) | OpenGL/Vulkan (Mesa) | OpenGL/Vulkan (Mesa) | Metal (OpenGL deprecated) |
| Video | NVENC / NVDEC | VA-API | VA-API, QSV | VideoToolbox |
| Monitoring | `nvidia-smi`, `nvtop` | `amd-smi`, `nvtop` | `intel_gpu_top`, `nvtop` | Activity Monitor, `ioreg` |

Portable options exist (OpenCL, Vulkan compute, ONNX Runtime and PyTorch with multiple backends), but most robotics GPU code is written for **CUDA**.

---
hideInToc: true
zoom: 0.85
---

# Why ROS looks NVIDIA-first

ROS itself is vendor-neutral. The **ecosystem** around it leans NVIDIA:

- **Jetson** (Orin, Thor) is the most common embedded computer with a serious GPU on robots, so code written for robots targets CUDA
- **Isaac ROS** (5.1, Lyrical): GPU-accelerated ROS packages for stereo, visual SLAM, nvblox, DNN inference. Runs only on NVIDIA: Jetson, or x86 with an Ampere+ GPU, Ubuntu 24.04, driver 595+
- **Isaac Sim** needs an NVIDIA RTX GPU
- **CUDA's head start**: PyTorch, TensorRT, OpenCV CUDA, PCL GPU, most research code
- Most ROS GPU tutorials, Docker images and Discourse answers assume `--gpus all`

The counterweight is moving into ROS itself:

- Lyrical's **`rosidl::Buffer` backends** let a message carry data in "vendor-specific memory domains such as GPU memory", so a GPU image can go between nodes without a copy to the CPU. The CUDA backend is community-maintained; other vendors can write backends
- Isaac ROS 5.0 dropped its own NVIDIA-only transport (NITROS) in favour of `rosidl::Buffer`
- Gazebo, RViz and Nav2 run on any GPU with OpenGL, or none

---
hideInToc: true
---

# AMD GPUs

- **Graphics** just works: the `amdgpu` kernel driver and Mesa are in Ubuntu, so Gazebo, RViz and Foxglove run well
- **Compute** is **ROCm**, with **HIP** as the CUDA-like API (`hipify` converts CUDA source)
- PyTorch has ROCm builds, and ONNX Runtime has ROCm/MIGraphX backends
- Check the support matrix before buying: ROCm 7.14 lists consumer cards like the RX 7900 XTX and RX 9070, but only on Ubuntu 24.04 and 22.04. Data center: Instinct MI300/MI350
- No Isaac ROS or Isaac Sim equivalent; fewer ROS packages with GPU code paths

```bash
# Docker: pass the compute and render devices (from the ROCm docs)
docker run -it --rm --device /dev/kfd --device /dev/dri <image>
amd-smi list          # monitoring; nvtop also supports AMD
```

Not tested here: our hardware is NVIDIA and Intel.

---
hideInToc: true
zoom: 0.8
---

# Apple silicon: Metal

- GPU and CPU share **unified memory**: no PCIe copies, and large models fit (our M4 iMac: 10 GPU cores, 32 GB shared)
- **Metal** is the API; PyTorch uses it through the `mps` device, and Core ML runs inference
- **No CUDA**: CUDA-only ROS packages don't build
- **ROS 2 on macOS** is Tier 3 on Intel Macs only; Apple silicon isn't listed, so you build from source on your own
- **Docker Desktop** runs an arm64 Linux VM with no GPU device: containers can't use Metal

```bash
$ docker run --rm ubuntu:24.04 sh -c "ls /dev/dri; uname -m"
ls: cannot access '/dev/dri': No such file or directory
aarch64
```

```bash
# GPU utilization on a Mac, no sudo needed
$ ioreg -r -d 1 -w 0 -c IOAccelerator | grep -oE '"Device Utilization %"=[0-9]+'
"Device Utilization %"=44
```

In practice a Mac is a great machine for Foxglove, simulation viewers and model work, with ROS itself running in a Linux VM or on the robot.

---
hideInToc: true
zoom: 0.9
---

# Install the NVIDIA driver on Ubuntu 26.04

```bash
$ sudo ubuntu-drivers devices
model    : GA104 [GeForce RTX 3060 Ti Lite Hash Rate]
driver   : nvidia-driver-595-open - distro non-free recommended

$ sudo ubuntu-drivers install nvidia:595-open      # 69 s in our VM
$ sudo reboot
$ nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
NVIDIA GeForce RTX 3060 Ti, 595.99.02, 8192 MiB
```

- `-open`: NVIDIA's open-source kernel modules, recommended for Turing (RTX 20) and newer
- `ubuntu-drivers` installs **Canonical-signed** modules (`linux-modules-nvidia-595-open-*`), so they load with **Secure Boot on** (tested in the VM)
- `-server` variants track data-center release branches
- The driver alone runs CUDA programs. To **build** CUDA code you need the toolkit:
  - `apt install nvidia-cuda-toolkit`: Ubuntu's package, CUDA **12.4**
  - NVIDIA's apt repo: current CUDA **13.5**, which lists Ubuntu 26.04 as supported

---
hideInToc: true
---

# First CUDA program

```cpp
__global__ void add(const float *a, const float *b, float *c, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;   // one thread per element
  if (i < n) c[i] = a[i] + b[i];
}

int main() {
  const int n = 1 << 24;
  float *a, *b, *c;
  cudaMallocManaged(&a, n * sizeof(float));        // visible to CPU and GPU
  ...
  add<<<(n + 255) / 256, 256>>>(a, b, c, n);       // 65,536 blocks of 256 threads
  cudaDeviceSynchronize();
}
```

```bash
$ nvcc -o vadd vadd.cu && ./vadd
NVIDIA GeForce RTX 3060 Ti: 38 SMs, c[0]=3.0 c[n-1]=3.0
```

Full source in `examples/vadd.cu`. The binary ran unchanged inside the VM with only the driver installed: `nvcc` links the CUDA runtime statically.

---
hideInToc: true
zoom: 0.88
---

# GPUs in Docker

```bash
# NVIDIA: needs the NVIDIA Container Toolkit on the host
docker run --rm --gpus all ubuntu:26.04 nvidia-smi -L
docker run --rm --device nvidia.com/gpu=all ubuntu:26.04 nvidia-smi -L     # CDI names
docker run --rm --gpus device=0 -e NVIDIA_DRIVER_CAPABILITIES=utility ubuntu:26.04 nvidia-smi

# Intel / AMD graphics and video: pass the render node
docker run --rm --device /dev/dri/renderD129 <image> vainfo
```

```
GPU 0: NVIDIA GeForce RTX 3060 Ti (UUID: GPU-0e57e4fa-3bd7-d89a-7b94-47893706b002)
```

- Without GPU flags the container has no `/dev/nvidia*` and no `nvidia-smi`
- `nvidia-ctk cdi list` shows the CDI names: `nvidia.com/gpu=0`, `=<UUID>`, `=all`
- `NVIDIA_DRIVER_CAPABILITIES` picks which driver libraries are mounted: `compute,utility` by default; add `graphics` for OpenGL/EGL (Gazebo), `video` for NVENC/NVDEC, or use `all`
- Capabilities don't go in `--gpus`: `--gpus "device=0,capabilities=utility"` fails with `unknown device`
- Render node numbers aren't fixed: on our host `renderD128` is NVIDIA and `renderD129` is Intel. Use `/dev/dri/by-path/pci-0000:00:02.0-render`
- Gazebo's EGL in a container also needs `10_nvidia.json` (see the simulation section)

---
hideInToc: true
zoom: 0.72
---

# GPUs in VMs: the options

| Approach | What the VM gets | CUDA in the VM? | Notes |
|---|---|---|---|
| None (default) | Virtual display only | No | Software rendering, as in our course VM |
| virtio-gpu with virgl/Venus | Accelerated OpenGL/Vulkan through the host | No | Host keeps the GPU; good for desktops and RViz |
| **PCI passthrough (VFIO)** | The whole physical GPU | **Yes** | Host loses the GPU while the VM runs |
| NVIDIA vGPU | A slice of a data-center GPU | Yes | Licensed, data-center GPUs only |
| SR-IOV | A hardware-partitioned slice | Yes | Some Intel iGPUs and AMD/NVIDIA data-center GPUs |

We tested no GPU and passthrough; the other rows are from vendor documentation.

Passthrough needs:

- IOMMU on (Intel VT-d / AMD-Vi), which our libvirt host setup already checks
- The GPU in an IOMMU group with nothing the host still needs
- Nothing on the host using the GPU (display manager, containers)

---
hideInToc: true
zoom: 0.85
---

# GPU passthrough: what happened on our host

```bash
$ virsh start ubuntu-server-2604
error: ... vfio 0000:01:00.0: group 2 is not viable
Please ensure all devices within the iommu_group are bound to their vfio bus driver.
```

```bash
$ for d in /sys/kernel/iommu_groups/2/devices/*; do lspci -nns ${d##*/}; done
00:01.0 PCI bridge: Intel ... PCIe Controller (x16)
00:01.2 PCI bridge: Intel ... PCIe Controller (x4)
01:00.0 VGA compatible controller: NVIDIA ... RTX 3060 Ti
01:00.1 Audio device: NVIDIA ... High Definition Audio Controller
02:00.0 Non-Volatile memory controller: Samsung ... SSD 970 EVO Plus
```

The CPU splits its 16 lanes between the GPU slot (x8) and an NVMe (x4) and can't isolate them, so **the SSD is in the GPU's group**. It worked once the unmounted SSD was also detached from the host:

```bash
sudo systemctl stop gdm                         # release the GPU on the host
virsh nodedev-detach pci_0000_02_00_0           # the SSD goes to vfio too (not given to the VM)
virsh attach-device ubuntu-server-2604 gpu-hostdev.xml --config   # 01:00.0 and 01:00.1, managed="yes"
virsh start ubuntu-server-2604
```

In the VM: `ubuntu-drivers install`, then `nvidia-smi`, CUDA and Gazebo all ran on the GPU (47% CPU vs 107%), and the Nav2 goal succeeded. Pick a board where the GPU slot has its own IOMMU group before planning on passthrough.

---
hideInToc: true
---

# Monitoring the GPU

```bash
nvidia-smi                                   # snapshot: processes, memory, power
nvidia-smi dmon -s pucm                      # one line per second
nvidia-smi pmon                              # per process (C = compute, G = graphics)
nvtop                                        # htop-style, NVIDIA + AMD + Intel; -s for JSON
sudo intel_gpu_top                           # Intel: per-engine Render/3D, Video, Blitter
nvidia-smi --query-gpu=utilization.gpu,power.draw,clocks.sm,pcie.link.width.current \
  --format=csv -l 1                          # pick fields, log every second
```

```
# gpu    pwr  gtemp  mtemp     sm    mem    enc    dec    jpg    ofa   mclk   pclk     fb
# Idx      W      C      C      %      %      %      %      %      %    MHz    MHz     MB
    0    196     66      -    100     30      0      0      0      0   6801   1650    699
```

- For fleets: export metrics to Prometheus (NVIDIA DCGM exporter) and graph them with the rest of the robot's telemetry
- On Jetson: `jtop` (jetson-stats)

---
hideInToc: true
zoom: 0.88
---

# "100% utilization" doesn't mean fully used

`utilization.gpu` is the "percent of time ... during which one or more kernels was executing", not how much of the GPU was busy. Measured with `examples/gpu_util.py` on the RTX 3060 Ti:

| Workload | Throughput | GPU util | Power |
|---|---|---|---|
| Idle | | 0% | 38 W |
| Tiny 256×256 matmul, sync after each | 34,480/s | **34.5%** | 59 W |
| Large 8192×8192 matmul, fp32 | 11.3/s | 100% | 197 W |
| Large 8192×8192 matmul, **fp16** (tensor cores) | **31.0/s** | 100% | 193 W |
| Camera net, 1 frame per call, CPU preprocessing | 175 fps | 61% | 160 W |
| Camera net, **16 frames** per call, GPU preprocessing | **512 fps** | 100% | 199 W |

- Tiny kernels look busy while doing almost nothing
- fp32 and fp16 both read 100%, but fp16 does **2.7×** the work
- Power draw is the better "is it working hard" signal: 197 W of a 200 W limit

---
hideInToc: true
zoom: 0.88
---

# Keeping the GPU busy

**Find the limit**

```bash
$ nvidia-smi --format=csv --query-gpu=clocks_event_reasons.active,\
clocks_event_reasons.sw_power_cap,power.draw,power.limit,clocks.sm,clocks.max.sm
0x0000000000000004, Active, 196.71 W, 200.00 W, 1665 MHz, 2130 MHz
```

Under load our GPU is **power capped**: 1,665 MHz of a possible 2,130 MHz. Thermal and power limits show up here, not in "utilization".

**Common fixes**

- **Batch**: process several frames or point clouds per call (2.9× fps above)
- **Preprocess on the GPU**: copy raw `uint8` bytes, convert and normalize on the GPU
- **Lower precision**: fp16 / int8 with tensor cores (TensorRT, `torch.autocast`)
- **Avoid copies**: keep data on the GPU between nodes (`rosidl::Buffer`, composition with intra-process communication)
- **Don't synchronize** after every small operation
- **Check the PCIe link**: ours runs Gen3 **x8** of x16 (≈6 GB/s host→GPU), because of the shared lanes on the passthrough slide
- **Profile**: Nsight Systems (`nsys profile`) shows the gaps where the GPU waits on the CPU

---
layout: section
---

# Simulation with Gazebo and Nav2

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
---

# Gazebo and ROS 2

Gazebo is the open source robot simulator from the same community as ROS: physics, sensors, and 3D rendering.

- Each ROS 2 release is paired with a Gazebo release: **Lyrical ↔ Gazebo Jetty (gz-sim 10)**
- `ros_gz` packages bridge Gazebo topics to ROS 2 topics and spawn robots from URDF
- Install Gazebo through ROS (`ros-lyrical-ros-gz`), not separately, so the versions match
- Gazebo is split in two:
  - **server** (`gz sim -s`): physics and sensor rendering, can run headless
  - **GUI client** (`gz sim -g`): 3D view that attaches to a running server

That split is what makes an on-demand GUI possible: the simulation runs headless all the time, and you attach a GUI only when someone wants to look.

---
hideInToc: true
---

# Nav2 in one slide

Nav2 is the ROS 2 navigation stack: give it a map and a goal pose, and it drives the robot there.

| Piece | Job |
|---|---|
| `map_server` + `amcl` | Load the map, localize the robot with the lidar |
| global / local costmaps | Obstacles from the map and live sensors |
| `planner_server` | Plan a path across the global costmap |
| `controller_server` | Follow the path, publish `cmd_vel` |
| `bt_navigator` | Behavior tree tying it together (`navigate_to_pose` action) |
| `lifecycle_manager` | Starts the nodes in order and aborts if one fails |

`nav2_bringup` ships complete simulations to learn on. We'll use the **TurtleBot 4** in the **Depot** world.

---
hideInToc: true
---

# Simulated sensors as ROS topics

The TurtleBot 4 simulation publishes the sensors a real robot has:

| Sensor | Topic | Type | Rate |
|---|---|---|---|
| Lidar | `/scan` | `sensor_msgs/LaserScan` | 10 Hz |
| IMU | `/imu` | `sensor_msgs/Imu` | 200 Hz |
| Wheel odometry | `/odom` (+ `odom → base_link` TF) | `nav_msgs/Odometry` | 83 Hz |
| RGB camera | `/rgbd_camera/image` | `sensor_msgs/Image` | 10 Hz |
| Depth camera | `/rgbd_camera/depth_image` | `sensor_msgs/Image` (32FC1) | 10 Hz |
| Camera intrinsics | `/rgbd_camera/camera_info` | `sensor_msgs/CameraInfo` | 10 Hz |
| Sim clock | `/clock` | `rosgraph_msgs/Clock` | |

Nodes run with `use_sim_time:=true` so they follow the simulator's clock, not the wall clock.

```bash
ros2 topic hz /scan
ros2 topic echo --once /rgbd_camera/depth_image --field encoding
```

---
hideInToc: true
---

# Architecture: headless sim, GUI on demand

```
             always running                         only while someone is looking
┌──────────────────────────────────────┐        ┌──────────────────────────────────┐
│ gz sim -s   (physics, sensors)       │◄──────►│ gz sim -g     (Gazebo 3D view)   │
│ ros_gz bridge                        │ gz +   │ rviz2         (map, costmaps)    │
│ Nav2 (amcl, planner, controller, ..) │ ROS 2  │ Xvnc :1 + openbox                │
└──────────────────────────────────────┘        │ websockify + noVNC  :6080        │
                                                └───────────────┬──────────────────┘
                                                                │ http + websocket
                                         browser ──► http://<host>:6080/vnc.html
```

- **Xvnc** (TigerVNC): an X server with no monitor that draws into memory and serves VNC
- **noVNC** + **websockify**: a VNC client in the browser, no install on the laptop
- `Xvnc -MaxDisconnectionTime 600` exits after 10 minutes with no viewer
- systemd starts the desktop on the **first browser connection**

---
hideInToc: true
---

# Install on the host (Ubuntu 26.04 + Lyrical)

```bash
sudo apt-get update
sudo apt-get install \
  ros-lyrical-navigation2 \
  ros-lyrical-nav2-bringup \
  ros-lyrical-nav2-minimal-tb4-sim \
  ros-lyrical-ros-gz \
  ros-lyrical-rviz2 \
  tigervnc-standalone-server tigervnc-tools \
  novnc websockify \
  openbox xterm
```

- `nav2-minimal-tb4-sim` brings the TurtleBot 4 model and the Depot world
- The Depot's 3D models download from Gazebo Fuel on first run (~100 MB, cached in `~/.gz/fuel`)
- About 7 GB of packages. Plan on 8 GB RAM and 4 CPUs for the VM
- Without a GPU, Gazebo renders the camera and GUI on the CPU (Mesa llvmpipe): ~1 CPU core for the sim

---
hideInToc: true
---

# Give Nav2 the robot's starting pose

Nav2 waits for an initial pose. With no RViz click in the first minute, bringup **aborts**:

```
[ERROR] [global_costmap]: Failed to activate global_costmap because transform
        from base_link to map did not become available before timeout
```

For a headless sim, put the pose in AMCL's parameters instead:

```bash
mkdir -p ~/sim
cp /opt/ros/lyrical/share/nav2_bringup/params/nav2_params.yaml ~/sim/
POSE="    set_initial_pose: true\n    initial_pose: {x: 7.1, y: 7.675, z: 0.0, yaw: 0.0}"
sed -i "/^amcl:/,/ros__parameters:/ s/ros__parameters:/&\n$POSE/" ~/sim/nav2_params.yaml
```

The robot spawns at Gazebo world `(-8, 0)`, but the map's origin is its bottom-left corner, so in the **map** frame the robot is at `(7.1, 7.675)`.

---
hideInToc: true
zoom: 0.9
---

# Run the simulation headless

```bash
source /opt/ros/lyrical/setup.bash
ros2 launch nav2_bringup tb4_simulation_launch.py \
  headless:=True use_rviz:=False \
  params_file:=$HOME/sim/nav2_params.yaml
```

```
[lifecycle_manager_nav2]: Managed nodes are active
```

In a VM, Gazebo can't use the virtual GPU (`eglInitialize failed for device EGL_EXT_device_drm`) and the sim never publishes odometry. Force Mesa's software renderer: `export LIBGL_ALWAYS_SOFTWARE=1` before launching.

Send the robot somewhere (map coordinates):

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 11.0, y: 8.5}, orientation: {w: 1.0}}}}"
```

```
Goal accepted with ID: 889cf0a0421c4f2e879e9ff6d2472529
Result:
    error_code: 0
Goal finished with status: SUCCEEDED
```

---
hideInToc: true
zoom: 0.75
---

# `gui.sh`: the browser desktop

The same script runs on the host and in the container:

```bash
#!/bin/bash
# Browser desktop that attaches to a running simulation, and exits
# by itself after IDLE_SECONDS with no VNC viewer connected.
set -e
source /opt/ros/lyrical/setup.bash
# Take the GUI apps down with the desktop when Xvnc exits. Use SIGKILL:
# the Gazebo GUI client ignores SIGTERM.
trap 'set +e; for p in $(pgrep -g $$); do [ "$p" = "$$" ] || kill -KILL "$p" 2>/dev/null; done' EXIT

mkdir -p ~/.vnc
echo "${VNC_PASSWORD:-rosrocks}" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

Xvnc :1 -geometry 1600x900 -depth 24 -localhost \
  -rfbauth ~/.vnc/passwd -MaxDisconnectionTime "${IDLE_SECONDS:-600}" &
XVNC_PID=$!
export DISPLAY=:1
sleep 2

openbox &
websockify --web /usr/share/novnc "${WEB_PORT:-6080}" localhost:5901 &

gz sim -g &
rviz2 -d /opt/ros/lyrical/share/nav2_bringup/rviz/nav2_default_view.rviz &

# Xvnc exits non-zero when the idle timeout fires: that is a normal stop
wait "$XVNC_PID" || true
```

- `-localhost` keeps raw VNC (5901) private; only websockify (6080) is reachable, and it asks for the VNC password
- The `trap` matters: the Gazebo GUI client ignores SIGTERM and would outlive the desktop

---
hideInToc: true
zoom: 0.8
---

# On the host: run the sim as a service

```ini
# /etc/systemd/system/sim.service
[Unit]
Description=Headless Gazebo + Nav2 TurtleBot 4 simulation
After=network-online.target

[Service]
User=ubuntu
Environment=GZ_PARTITION=sim LIBGL_ALWAYS_SOFTWARE=1
ExecStart=/bin/bash -c "source /opt/ros/lyrical/setup.bash && \
  exec ros2 launch nav2_bringup tb4_simulation_launch.py \
    headless:=True use_rviz:=False \
    params_file:=/home/ubuntu/sim/nav2_params.yaml"
Restart=on-failure
# ros2 launch shuts down cleanly on Ctrl+C (SIGINT); SIGTERM timed out after 90 s
KillSignal=SIGINT
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

```bash
install -m 755 gui.sh ~/sim/gui.sh
sudo systemctl enable --now sim.service
```

Run the sim **one** way: a leftover `ros2 launch` from a terminal starts a second set of Nav2 nodes with the same names, and bringup fails. Check with `ros2 node list | sort | uniq -d`.

---
hideInToc: true
zoom: 0.8
---

# On the host: start the desktop on the first browser connection

```ini
# /etc/systemd/system/sim-gui.socket
[Socket]
ListenStream=6080
[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/sim-gui.service: forwards each connection
[Unit]
BindsTo=sim-gui-desktop.service
After=sim-gui-desktop.service
[Service]
ExecStart=/usr/lib/systemd/systemd-socket-proxyd --exit-idle-time=5min 127.0.0.1:16080
```

```ini
# /etc/systemd/system/sim-gui-desktop.service: the desktop itself
[Unit]
StopWhenUnneeded=yes
[Service]
User=ubuntu
Environment=GZ_PARTITION=sim LIBGL_ALWAYS_SOFTWARE=1 WEB_PORT=16080 IDLE_SECONDS=600
ExecStart=/home/ubuntu/sim/gui.sh
TimeoutStopSec=15
ExecStartPost=/bin/sh -c "until curl -sf -o /dev/null http://127.0.0.1:16080/vnc.html; do sleep 1; done"
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now sim-gui.socket
# browse to http://<vm-ip>:6080/vnc.html (password: rosrocks)
```

---
hideInToc: true
---

# What you see in the browser

<img src="/sim-desktop.png" class="h-88 mx-auto" />

Gazebo GUI (left) and RViz with the Nav2 panel (right), attached to the headless sim in the course VM, mid-way to a goal.

---
hideInToc: true
---

# The same thing in Docker: the image

```dockerfile
FROM ros:lyrical-ros-base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-lyrical-navigation2 ros-lyrical-nav2-bringup \
      ros-lyrical-nav2-minimal-tb4-sim ros-lyrical-ros-gz ros-lyrical-rviz2 \
      tigervnc-standalone-server tigervnc-tools novnc websockify \
      openbox xterm \
    && rm -rf /var/lib/apt/lists/*

# Register NVIDIA's EGL library so Gazebo renders sensors on the GPU
RUN mkdir -p /usr/share/glvnd/egl_vendor.d && \
    printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}\n' \
      > /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# Gazebo only talks to peers in the same partition (default: hostname:user)
ENV GZ_PARTITION=sim

COPY gui.sh /usr/local/bin/gui.sh
```

```bash
docker build -t ros-sim:lyrical .
```

---
hideInToc: true
zoom: 0.9
---

# Run the simulation container

```bash
docker network create simnet
docker volume create gz-fuel

docker run -d --name sim --network simnet \
  --gpus all -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v gz-fuel:/root/.gz/fuel \
  -v $HOME/sim:/config:ro \
  ros-sim:lyrical bash -c "source /opt/ros/lyrical/setup.bash && \
    ros2 launch nav2_bringup tb4_simulation_launch.py \
      headless:=True use_rviz:=False params_file:=/config/nav2_params.yaml"
```

- `--gpus all` + `NVIDIA_DRIVER_CAPABILITIES=all`: GPU for sensor rendering (needs the NVIDIA Container Toolkit). Drop both on a machine without an NVIDIA GPU
- `gz-fuel` volume: models download once and are shared with the GUI container
- `simnet`: ROS 2 and Gazebo discovery both use multicast, which works inside one Docker network

```bash
$ nvidia-smi | grep gz-sim
|  0  N/A  N/A  1187865  G  .../libexec/gz/sim10/gz-sim-main  754MiB |
```

Without the EGL vendor file Gazebo silently falls back to the CPU: `gz-sim-main` used 164% CPU on Mesa vs 89% on the GPU.

---
hideInToc: true
---

# Attach a GUI container

```bash
docker run -d --rm --name sim-gui --network simnet \
  -p 127.0.0.1:6080:6080 \
  -v gz-fuel:/root/.gz/fuel \
  -e VNC_PASSWORD=rosrocks -e IDLE_SECONDS=600 \
  ros-sim:lyrical gui.sh
```

Open `http://localhost:6080/vnc.html` (through an SSH tunnel: `ssh -L 6080:localhost:6080 <host>`).

- The GUI joins the running sim: stopping it doesn't disturb the simulation or Nav2
- Same `GZ_PARTITION` (set in the image) so `gz sim -g` finds the server in the other container
- Same `gz-fuel` volume, or the 3D view stays empty: the GUI loads meshes from its own cache

---
hideInToc: true
zoom: 0.72
---

# In Docker: start the GUI container on the first connection

Same pattern as on the host, but the desktop unit runs a container:

```ini
# /etc/systemd/system/sim-gui.socket
[Socket]
ListenStream=127.0.0.1:6080
[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/sim-gui.service: forwards the connection
[Unit]
BindsTo=sim-gui-container.service
After=sim-gui-container.service
[Service]
ExecStart=/usr/lib/systemd/systemd-socket-proxyd --exit-idle-time=5min 127.0.0.1:16080
```

```ini
# /etc/systemd/system/sim-gui-container.service: the desktop itself
[Unit]
StopWhenUnneeded=yes
[Service]
ExecStartPre=-/usr/bin/docker rm -f sim-gui
ExecStart=/usr/bin/docker run --rm --name sim-gui --network simnet \
  -p 127.0.0.1:16080:6080 -v gz-fuel:/root/.gz/fuel ros-sim:lyrical gui.sh
ExecStartPost=/bin/sh -c "until curl -sf -o /dev/null http://127.0.0.1:16080/vnc.html; do sleep 1; done"
ExecStop=-/usr/bin/docker stop sim-gui
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now sim-gui.socket
```

---
hideInToc: true
---

# What happens on demand

```
$ docker ps | grep sim-gui                      # nothing running
$ curl -o /dev/null -w "%{http_code} %{time_total}s\n" http://127.0.0.1:6080/vnc.html
200 3.414155s                                   # first visitor starts the desktop
$ systemctl is-active sim-gui.socket sim-gui.service sim-gui-container.service
active active active

# ... no VNC viewer for IDLE_SECONDS: Xvnc exits, the container stops ...
VNCServerST: MaxDisconnectionTime reached, exiting
$ systemctl is-active sim-gui.socket sim-gui.service sim-gui-container.service
active inactive inactive                        # only the socket is left listening

$ curl -o /dev/null -w "%{http_code} %{time_total}s\n" http://127.0.0.1:6080/vnc.html
200 3.492851s                                   # next visitor starts it again
```

- `BindsTo=` (not `Requires=`) so the proxy stops when the container exits on its own
- The `-` in `ExecStop=-` ignores the error when the container already removed itself
- Use system units: a `systemctl --user` manager started before you joined the `docker` group can't reach the Docker socket

---
hideInToc: true
---

# Foxglove

A visualization and data platform for robotics. It runs **in your browser or a desktop app** and draws the robot's data locally, instead of streaming a remote desktop.

- **Live**: connect to a running robot or sim through `foxglove_bridge` (WebSocket, port 8765)
- **Recorded**: open MCAP files and ROS bags, scrub through time
- **Panels**: 3D (TF, point clouds, markers, URDF), Image, Plot, Map, Raw Messages, Log, Diagnostics, Topic Graph, Parameters, Service Call, Publish, Teleop and more
- **Layouts**: arrange panels once, share them with the team
- **Cloud** (paid tiers): upload recordings from devices, search and stream them

Apps: `app.foxglove.dev` in Chrome, or desktop for Linux (`.deb`), macOS and Windows. Foxglove's docs start with "Create a free Foxglove account".

---
hideInToc: true
zoom: 0.78
---

# Connect Foxglove to the simulation

```bash
sudo apt-get install ros-lyrical-foxglove-bridge
ros2 launch foxglove_bridge foxglove_bridge_launch.xml use_sim_time:=true
```

```
[foxglove_bridge]: Advertising new channel 112 for topic "/behavior_tree_log"
```

In Foxglove: **Open connection → Foxglove WebSocket → `ws://<host>:8765`**

What the bridge served from the TurtleBot 4 sim (112 topics advertised):

| Topic | Type | Rate | Size per message |
|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | 10 /s | 2.9 KB |
| `/rgbd_camera/image` | `sensor_msgs/msg/Image` | 10 /s | **230 KB** (raw 320×240 RGB) |
| `/odom` | `nav_msgs/msg/Odometry` | 83 /s | 0.7 KB |
| `/imu` | `sensor_msgs/msg/Imu` | 199 /s | 0.3 KB |

One small raw camera is already ~18 Mbit/s. Subscribe to `/rgbd_camera/image/compressed` instead, or throttle, over slow links.

---
hideInToc: true
zoom: 0.88
---

# Secure the bridge

`foxglove_bridge` has **no login**: anyone who can reach port 8765 can read every topic, publish, call services and set parameters.

```bash
ros2 launch foxglove_bridge foxglove_bridge_launch.xml \
  address:=127.0.0.1 \
  topic_whitelist:="['/scan', '/odom', '/tf', '/tf_static', '/map', '/rgbd_camera/.*']" \
  use_sim_time:=true
```

```bash
# from your laptop
ssh -L 8765:localhost:8765 <host>       # then connect to ws://localhost:8765
```

- `address:=127.0.0.1`: listen on localhost only (default `0.0.0.0`, every interface)
- `topic_whitelist`, `service_whitelist`, `param_whitelist`, `client_topic_whitelist`: regex lists, default `.*`
- `capabilities`: drop `clientPublish`, `services` or `parameters` for a read-only bridge
- `tls:=true` with `certfile`/`keyfile` for `wss://`
- `asset_uri_allowlist`: controls which files (meshes, URDF) clients can fetch

---
hideInToc: true
---

# Record and replay with MCAP

MCAP is the default bag format on Lyrical, and Foxglove opens it directly:

```bash
$ ros2 bag record -o run1 --topics /scan /imu /odom /tf /tf_static
$ ros2 bag info run1
Files:             0_run1_2026_11_27-13_38_31.mcap
Storage id:        mcap
Duration:          9.505273561s
Messages:          1997
```

- Drag the `.mcap` into Foxglove (or open it in the desktop app) to replay with every panel
- Message definitions are stored inside the file, so it opens without the ROS packages installed
- On Lyrical, pass topics with `--topics`; a bare `ros2 bag record /scan /imu` recorded nothing in our test

---
hideInToc: true
zoom: 0.9
---

# Foxglove: pros and cons

**Pros**

- Nothing to install on the robot except `foxglove_bridge` (MIT licensed)
- Renders on the viewer's machine: smooth 3D, no remote desktop, many viewers at once
- Same layouts for live data and recordings; strong plotting and message inspection
- Works with any ROS 2 distro the bridge supports, plus non-ROS data through the Foxglove SDK
- Free tier, and free Academic plan for `.edu`/`.ac` addresses

**Cons**

- The app is proprietary and expects an account; cloud features are paid (Pro $20/month + usage, Enterprise custom)
- Free tier limits: 3 users, 5 devices, 10 GB storage, 1 project
- Sends raw ROS messages: images and point clouds use a lot of bandwidth over the internet
- Bridge has no authentication: you must add network protection yourself
- Not a simulator GUI: can't click to move objects in Gazebo, and RViz plugins don't carry over

---
hideInToc: true
---

# Open source alternative: Lichtblick

Lichtblick is an open source (MPL-2.0) fork of Foxglove Studio, maintained since Foxglove's app became proprietary. Self-hosted, no Foxglove account.

```bash
docker run --rm -p 8080:8080 ghcr.io/lichtblick-suite/lichtblick:latest
# open http://localhost:8080
```

- Runs in the browser or as a desktop app; opens MCAP files and ROS bags
- Self-hosted: data never leaves your network
- Fewer features than current Foxglove, and no cloud data platform
- Connects live to `foxglove_bridge`: v2.5.2 includes the `foxglove.sdk.v1` protocol that current bridges require (older clients that only speak `foxglove.websocket.v1` get HTTP 400)

---
hideInToc: true
zoom: 0.9
---

# Choosing a remote view

| | noVNC desktop | Foxglove / Lichtblick | LiveKit |
|---|---|---|---|
| What travels | Pixels of a remote desktop | ROS messages | Encoded video + data |
| Runs the GUI | On the server | In the viewer's browser | Your own app |
| Gazebo GUI, RViz plugins | Yes | No | No |
| Plots, message inspection, bag replay | Through RViz/rqt | Yes, best at it | No |
| Many viewers | Each costs server CPU | Yes | Yes |
| Bandwidth over the internet | Moderate (VNC compression) | High for images/clouds | Low (adaptive video) |
| Access control | VNC password | None in the bridge | Tokens |

A common setup: the noVNC desktop for the simulator GUI, Foxglove for engineers digging into data, and LiveKit for operators driving with live video.

---
hideInToc: true
zoom: 0.7
---

# Lessons from getting this working

| Symptom | Cause | Fix |
|---|---|---|
| Nav2 bringup aborts after ~1 minute | No initial pose, so no `map → odom` TF | `set_initial_pose` in AMCL params |
| Goal fails with `error_code: 203` (start outside map) | Initial pose given in Gazebo world coordinates | Use **map** coordinates: `(7.1, 7.675)` in the Depot |
| Gazebo GUI shows an empty, gray world | GUI container has no copy of the Fuel models | Share `~/.gz/fuel` (the `gz-fuel` volume) |
| GUI client never sees the server | Different `GZ_PARTITION` (defaults to `hostname:user`) | Same `GZ_PARTITION` in every container |
| Sensors render on the CPU in Docker | No `10_nvidia.json` EGL vendor file in the image | Add it (see Dockerfile) |
| Socket-activated desktop never starts | User systemd can't use Docker | System units |
| In a VM: no odometry, `eglInitialize failed` | Gazebo tries the virtio GPU it can't open | `LIBGL_ALWAYS_SOFTWARE=1` |
| Bringup fails though nothing changed | A leftover launch runs duplicate Nav2 nodes | Run the sim one way (the service) |
| Desktop unit "failed" after idle | Gazebo GUI ignores SIGTERM; Xvnc exits non-zero | `trap` kills the group; `wait ... \|\| true` |

---
hideInToc: true
---

# NVIDIA Isaac Sim

A robot simulator built on NVIDIA Omniverse: RTX ray-traced rendering, PhysX physics, USD scenes.

- **Version**: 6.2.0, Apache 2.0 source on GitHub (`isaac-sim/IsaacSim`); Omniverse license terms are accepted on first run (`ACCEPT_EULA=Y`)
- **Minimum**: GeForce RTX 4080 with 16 GB VRAM, 32 GB RAM, 50 GB SSD, driver 595.58+, Ubuntu 24.04 (22.04 deprecated)
- **ROS 2**: built-in bridge with bundled **Humble** and **Jazzy** libraries; Lyrical is not listed
- **Sensors**: RTX camera (RGB, depth, segmentation, bounding boxes), RTX lidar and radar, IMU, contact sensors; odometry and TF publishers
- **Nav2**: tutorials with Nova Carter and iw.hub (`carter_navigation`)
- **Synthetic data**: Replicator for labeled training images
- **Remote GUI**: WebRTC livestream (desktop client or a Chromium browser), one viewer per instance

---
hideInToc: true
zoom: 0.88
---

# Isaac Sim in Docker

```bash
docker pull nvcr.io/nvidia/isaac-sim:6.2.0        # 31.9 GB

docker run --name isaac-sim --entrypoint bash -it --rm --gpus all \
  --network=host -e ACCEPT_EULA=Y -e PRIVACY_CONSENT=N \
  -v ~/docker/isaac-sim/cache/main:/isaac-sim/.cache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
  -v ~/docker/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
  -v ~/docker/isaac-sim/pkg:/isaac-sim/.local/share/ov/pkg:rw \
  -u 1234:1234 nvcr.io/nvidia/isaac-sim:6.2.0

./isaac-sim.compatibility_check.sh --/app/quitAfter=10 --no-window
./runheadless.sh -v     # livestream: TCP 49100 signaling, UDP 47998 media
```

- Create the `~/docker/isaac-sim/...` directories first and `chown -R 1234:1234` them; the caches make later starts much faster
- `--network=host` is required for livestreaming and lets ROS 2 discovery reach the host
- Livestream has no authentication or encryption: keep it on a trusted network or behind a VPN/tunnel

---
hideInToc: true
zoom: 0.72
---

# Isaac Sim on an RTX 3060 Ti (8 GB)

Below the official minimum, so we tried it:

```
|-- Driver version [supported]
|-- GPU 0 [supported]
|     |-- name: NVIDIA GeForce RTX 3060 Ti
|-- GPU 0: VRAM [not enough]
System checking result: FAILED
```

It still runs smaller scenes:

| Test | Result |
|---|---|
| `./runheadless.sh -v` | "Isaac Sim Full Streaming App is loaded" after ~4 min (first start compiles shaders); 1.2 GB VRAM |
| RTX lidar example in the warehouse, bundled Jazzy ROS 2 | `/scan` 8.3 Hz, `/point_cloud` 8.5 Hz (462,024 points), 2.95 GB VRAM |
| Reading those topics from a **Lyrical** container | Works: Jazzy (Isaac) ↔ Lyrical over DDS for standard messages |

```bash
export ROS_DISTRO=jazzy RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.core/jazzy/lib
./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
```

---
hideInToc: true
zoom: 0.7
---

# Gazebo vs Isaac Sim

| | Gazebo (Jetty) | Isaac Sim 6.2 |
|---|---|---|
| License | Apache 2.0 | Apache 2.0 source + Omniverse terms |
| Hardware | Any x86/ARM; runs on CPU, GPU optional | NVIDIA RTX only, 16 GB VRAM minimum |
| Install | apt packages; our Nav2 + Gazebo + VNC image is 7.7 GB | 31.9 GB container, x86_64 Linux (+ DGX Spark) |
| ROS 2 | Native, versioned with each ROS release (Lyrical) | Bridge with bundled Humble/Jazzy |
| Startup (our tests) | ~1 min to Nav2 active | ~4 min to app ready, ~6 min to a running scene, first start |
| Rendering | OGRE 2, good enough for most perception | RTX ray tracing, photoreal |
| Sensors | Camera, depth, lidar, IMU, odometry, contact | RTX camera, lidar and radar, segmentation, IMU, contact |
| Physics | DART, Bullet | PhysX (GPU), Newton |
| Scenes | SDF worlds, Fuel models | USD, NVIDIA asset library |
| Remote GUI | Any VNC/noVNC desktop, many viewers | WebRTC livestream, one viewer |
| Scale-out | Many headless sims per machine, CI-friendly | Few instances per GPU |
| Synthetic data | Basic | Replicator: labeled data at scale |

---
hideInToc: true
---

# Which simulator when?

**Gazebo** when you need:

- Navigation, control and integration testing with Nav2/MoveIt
- Many simulations at once: CI pipelines, every developer, classroom VMs
- Machines without NVIDIA GPUs (laptops, VMs, ARM)
- The newest ROS 2 release on day one

**Isaac Sim** when you need:

- Photoreal cameras or physically based lidar/radar for perception
- Synthetic, labeled training data for machine learning
- GPU physics at scale (manipulation, reinforcement learning with Isaac Lab)
- NVIDIA's Isaac ROS / Jetson ecosystem

Many teams use both: Gazebo for everyday development and CI, Isaac Sim for perception and data generation.

---
layout: section
---

# Recording and replay with ros2 bag

<br>
<br>
<Link to="toc" title="Table of Contents"/>

---
hideInToc: true
zoom: 0.75
---

# What a bag is for

A **bag** records messages from topics (and optionally services and actions) to disk, with timestamps, so you can play them back later exactly as they happened.

- **Debug** a failure that happened on the robot, at your desk
- **Develop offline**: run perception or SLAM on recorded sensor data, without the robot
- **Regression tests**: replay the same input after every change
- **Share data** with teammates, and collect training data

```
depot_run/
├── metadata.yaml                          # topics, types, QoS, counts, duration
└── 0_depot_run_2026_11_27-16_51_26.mcap   # the messages (MCAP format)
```

| Command | Does |
|---|---|
| `ros2 bag record` | Record topics to a new bag |
| `ros2 bag info` | Summary: duration, size, topics, counts |
| `ros2 bag play` | Publish the recorded messages again |
| `ros2 bag convert` | Filter topics, change storage or compression |
| `ros2 bag reindex` | Rebuild a lost `metadata.yaml` |

---
hideInToc: true
zoom: 0.8
---

# Record

While the TurtleBot 4 sim drove to a goal:

```bash
ros2 bag record -o depot_run --topics \
  /scan /odom /imu /tf /tf_static /rgbd_camera/image /rgbd_camera/camera_info /cmd_vel
# Ctrl+C to stop
```

```
$ ros2 bag info depot_run
Files:             0_depot_run_2026_11_27-16_51_26.mcap
Bag size:          295.4 MiB
Storage id:        mcap
ROS Distro:        lyrical
Duration:          125.111711767s
Messages:          52391
Topic information: Topic: /cmd_vel | Type: geometry_msgs/msg/TwistStamped | Count: 351
                   Topic: /imu | Type: sensor_msgs/msg/Imu | Count: 24748
                   Topic: /odom | Type: nav_msgs/msg/Odometry | Count: 10312
                   Topic: /rgbd_camera/camera_info | Type: sensor_msgs/msg/CameraInfo | Count: 1237
                   Topic: /rgbd_camera/image | Type: sensor_msgs/msg/Image | Count: 1238
                   Topic: /scan | Type: sensor_msgs/msg/LaserScan | Count: 1237
                   Topic: /tf | Type: tf2_msgs/msg/TFMessage | Count: 13267
                   Topic: /tf_static | Type: tf2_msgs/msg/TFMessage | Count: 1
```

2.4 MB/s, almost all of it the raw camera: 1,238 images × 230 KB. On Lyrical, MCAP is the default storage.

---
hideInToc: true
zoom: 0.9
---

# Choosing what to record

```bash
ros2 bag record --topics /scan /odom /tf /tf_static   # a list
ros2 bag record -a                                      # every topic
ros2 bag record -e "/rgbd_camera/.*|/scan"              # regex
ros2 bag record -a --exclude-topics /rgbd_camera/image  # everything but
ros2 bag record -a --exclude-regex ".*/compressed.*"
ros2 bag record --topics /scan --services /spawn        # also service calls
ros2 bag record --all-topics --all-services --all-actions
```

- Always record **`/tf` and `/tf_static`**, or nothing can be put in a common frame later
- Record **`camera_info`** with images, and **`/clock`** in simulation
- `-a` in a big system records hundreds of topics, including high-rate debug ones. Start from an explicit list
- `/tf_static` is published once: the recorder catches it because it's transient-local, so a late recorder still gets it
- Hidden topics (`/_...`) are skipped unless `--include-hidden-topics`

---
hideInToc: true
zoom: 0.78
---

# Size and compression

20 s of `/scan /odom /imu /tf /tf_static /rgbd_camera/image`:

| Recording | Size |
|---|---|
| `ros2 bag record ...` (MCAP, default) | 46 MB |
| `-s sqlite3` | 46 MB |
| `--storage-preset-profile zstd_fast` | 11 MB |
| `--storage-preset-profile zstd_small` | 1.8 MB |
| `--compression-mode file --compression-format zstd` | 0.5 MB (`.mcap.zstd`) |
| Same topics without the camera | 3.4 MB |

- The robot was standing still, so the simulated camera frames were nearly identical: **real camera footage compresses far less**
- `zstd_fast` is a good default: MCAP compresses each chunk, the bag stays readable and seekable
- File compression gives the smallest files, but each file must be decompressed before reading
- Biggest win: record `.../image/compressed`, or lower the camera rate, instead of raw images

---
hideInToc: true
zoom: 0.88
---

# Long recordings: split files and snapshots

```bash
# a new file every 10 s (or -b <bytes> for size)
$ ros2 bag record -o split_run -d 10 --topics /scan /odom /tf
$ ls split_run
0_split_run_...16_56_04.mcap  1_split_run_...16_56_14.mcap  2_split_run_...16_56_24.mcap  metadata.yaml
```

**Snapshot mode** keeps only the last N seconds in memory and writes them when asked, like a dashcam:

```bash
ros2 bag record -o snap_run --snapshot-mode --max-cache-duration 5 --topics /scan /odom
# ... later, when something interesting happens:
ros2 service call /rosbag2_recorder/snapshot rosbag2_interfaces/srv/Snapshot
```

```
rosbag2_interfaces.srv.Snapshot_Response(success=True)
Topic: /odom | Count: 408         # ~5 s at 83 Hz
Topic: /scan | Count: 49          # ~5 s at 10 Hz
```

The recorder also offers `/rosbag2_recorder/pause`, `resume`, `split_bagfile` and `stop` services: trigger them from your own nodes.

---
hideInToc: true
zoom: 0.88
---

# Play back

```bash
ros2 bag play depot_run                          # real time
ros2 bag play depot_run -r 2                     # 2x speed
ros2 bag play depot_run --clock                  # also publish /clock from the bag
ros2 bag play depot_run -l                       # loop
ros2 bag play depot_run --start-offset 120       # skip the first 120 s
ros2 bag play depot_run -p                       # start paused
ros2 bag play depot_run --topics /scan --remap /scan:=/scan_replay
```

Measured on the course VM (live sim stopped first):

| Command | Result |
|---|---|
| `play depot_run` | `/scan` at 10.4 Hz |
| `play depot_run -r 2 --clock` | `/scan` at 19.8 Hz, `/clock` at 40 Hz |
| `--topics /scan --remap /scan:=/scan_replay` | only `/scan_replay` appears |
| `--start-offset 120` (125 s bag) | finished in 5 s |

**Stop the live system first** (or remap): replayed and live `/tf`, `/scan` and `/odom` would mix.

---
hideInToc: true
zoom: 0.78
---

# Replay with simulated time

Nodes that process a bag must follow the **bag's** clock, not the wall clock:

```bash
ros2 bag play depot_run --clock
ros2 run my_pkg my_node --ros-args -p use_sim_time:=true
```

- Without `use_sim_time`, nodes compare old message stamps with the current wall clock: TF lookups and timeouts misbehave
- With `-r 2` and `--clock`, every node using sim time runs at 2x too
- Recorded QoS is replayed: the bag's metadata stores each publisher's QoS, and `/tf_static` is offered as `TRANSIENT_LOCAL` again, so a late subscriber still gets it:

```
$ ros2 topic info -v /tf_static
Node name: rosbag2_player
  Reliability: RELIABLE
  Durability: TRANSIENT_LOCAL
$ ros2 topic echo --once /tf_static | grep child_frame_id
  child_frame_id: base_footprint
  child_frame_id: bump_front_center
```

- If a subscriber needs different QoS, pass `--qos-profile-overrides-path overrides.yaml`

---
hideInToc: true
zoom: 0.9
---

# Convert, filter, repair

```yaml
# convert.yaml: keep two topics, write SQLite
output_bags:
  - uri: scan_odom_sqlite
    storage_id: sqlite3
    topics: [/scan, /odom]
```

```bash
$ ros2 bag convert -i depot_run -o convert.yaml
$ ros2 bag info scan_odom_sqlite
Files:             0_scan_odom_sqlite_2026_11_27-17_00_06.db3
Bag size:          14.3 MiB
Storage id:        sqlite3
Messages:          11549
```

Lost `metadata.yaml` (e.g. the robot lost power mid-recording)?

```bash
$ ros2 bag info reidx
Could not find metadata in bag directory reidx
$ ros2 bag reindex reidx
[INFO] [rosbag2_cpp]: Reindexing complete.
```

---
hideInToc: true
zoom: 0.8
---

# Read a bag from Python

```python
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

reader = rosbag2_py.SequentialReader()
reader.open(rosbag2_py.StorageOptions(uri="depot_run"), rosbag2_py.ConverterOptions("", ""))
reader.set_filter(rosbag2_py.StorageFilter(topics=["/odom", "/scan"]))
types = {t.name: get_message(t.type) for t in reader.get_all_topics_and_types()}

while reader.has_next():
    topic, data, recv_ns, send_ns = reader.read_next_ext()
    msg = deserialize_message(data, types[topic])
    ...  # sum odometry distance, find the closest scan range
```

```
$ time python3 read_bag.py depot_run
drove 6.80 m, 1237 scans, closest obstacle 1.61 m
real    0m1.167s
```

- No ROS graph needed: good for analysis, CI checks and dataset export
- Full script: `examples/read_bag.py`. `read_next()` still works but is deprecated on Lyrical
- To look instead of compute, open the `.mcap` in Foxglove (simulation section)

---
hideInToc: true
zoom: 0.9
---

# Record from a launch file

```python
# examples/record_launch.py
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='demo_nodes_cpp', executable='talker'),
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-o', 'talker_run',
                 '--storage-preset-profile', 'zstd_fast', '--topics', '/chatter'],
            output='screen',
        ),
    ])
```

```
[ros2-2] [rosbag2_recorder]: Recording stopped
[ERROR] [ros2-2]: process has died [pid 12988, exit code 2, cmd 'ros2 bag record ...']
```

The `ERROR` on Ctrl+C is cosmetic: the CLI exits with code 2 after stopping cleanly, and the bag is complete.

Stopping a recorder from a script: send **SIGINT** or **SIGTERM** to it in the foreground (`timeout -s INT 30 ros2 bag record ...`). A background job (`&`) in a script ignores SIGINT, so use SIGTERM there.

---
hideInToc: true
zoom: 0.76
---

# Bag checklist

| Do | Why |
|---|---|
| Record `/tf`, `/tf_static`, `camera_info` (and `/clock` in sim) | Nothing lines up without them |
| Name bags (`-o`) with robot, date and what happened | Hundreds of `rosbag2_2026_...` directories are useless |
| Use `--storage-preset-profile zstd_fast` | Smaller files, still seekable |
| Record compressed images, or fewer camera topics | Raw cameras dominate size and disk bandwidth |
| Split long runs (`-d` / `-b`) or use snapshot mode | One huge file is fragile and slow to copy |
| Check free disk space before long recordings | Raw sensors fill disks fast: 2.4 MB/s here is 8.6 GB/hour |
| Stop live nodes or remap before playing back | Replayed and live topics would mix |
| Replay with `--clock` and `use_sim_time:=true` | Old timestamps break TF and timeouts otherwise |
| Keep the message packages that were recorded | Custom types need their definitions to be read (MCAP stores them for tools like Foxglove) |

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
