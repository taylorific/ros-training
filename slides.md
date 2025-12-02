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
