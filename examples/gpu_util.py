"""Show what nvidia-smi reports for workloads that do and don't keep the GPU busy."""
import subprocess, threading, time
import numpy as np
import torch

QUERY = "utilization.gpu,utilization.memory,power.draw,clocks.sm,pcie.link.gen.current,pcie.link.width.current"
samples, stop = [], threading.Event()

def sampler():
    while not stop.is_set():
        out = subprocess.run(["nvidia-smi", f"--query-gpu={QUERY}", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True).stdout.strip().split(", ")
        samples.append((time.time(), [float(x) for x in out]))
        time.sleep(0.25)

def phase(name, fn, seconds=6):
    torch.cuda.synchronize()
    t0 = time.time(); n = 0
    while time.time() - t0 < seconds:
        fn(); n += 1
    torch.cuda.synchronize()
    t1 = time.time()
    s = [v for t, v in samples if t0 + 1 <= t <= t1]          # skip the ramp-up second
    avg = np.mean(s, axis=0) if s else [0] * 6
    print(f"{name:42s} {n / (t1 - t0):9.1f} it/s | GPU {avg[0]:5.1f}%  mem {avg[1]:5.1f}%  "
          f"{avg[2]:6.1f} W  SM {avg[3]:6.0f} MHz  PCIe gen{avg[4]:.0f} x{avg[5]:.0f}")

dev = torch.device("cuda")
print(torch.__version__, torch.cuda.get_device_name(0))
threading.Thread(target=sampler, daemon=True).start()
time.sleep(2)
phase("idle", lambda: time.sleep(0.1))

a_small = torch.randn(256, 256, device=dev); b_small = torch.randn(256, 256, device=dev)
def small(): (a_small @ b_small); torch.cuda.synchronize()
phase("small matmul 256x256, sync each time", small)

a = torch.randn(8192, 8192, device=dev); b = torch.randn(8192, 8192, device=dev)
phase("large matmul 8192x8192 fp32", lambda: (a @ b))
ah, bh = a.half(), b.half()
phase("large matmul 8192x8192 fp16 (tensor cores)", lambda: (ah @ bh))

# Host -> device copies: pageable vs pinned memory
pageable = torch.randn(64, 1024, 1024)            # 256 MB
pinned = pageable.pin_memory()
for name, src in [("copy 256 MB host->GPU, pageable", pageable), ("copy 256 MB host->GPU, pinned", pinned)]:
    torch.cuda.synchronize(); t = time.time(); reps = 20
    for _ in range(reps): src.to(dev, non_blocking=True)
    torch.cuda.synchronize(); dt = time.time() - t
    print(f"{name:42s} {reps * 0.25 / dt:6.1f} GB/s")

# A camera-like pipeline: 640x480 frames through a small conv net
net = torch.nn.Sequential(*[torch.nn.Conv2d(3 if i == 0 else 32, 32, 3, padding=1) for i in range(6)]).to(dev).half().eval()
frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

def one_frame_cpu_preprocess():
    x = frame.astype(np.float32) / 255.0                 # normalize on the CPU
    x = torch.from_numpy(x).permute(2, 0, 1)[None]       # HWC -> NCHW
    with torch.no_grad(): net(x.to(dev).half())
    torch.cuda.synchronize()
phase("1 frame/call, CPU preprocessing (fps)", one_frame_cpu_preprocess)

batch_u8 = torch.from_numpy(np.stack([frame] * 16)).pin_memory()
def batch_gpu_preprocess():
    x = batch_u8.to(dev, non_blocking=True)               # copy raw bytes (4x smaller than float)
    x = x.permute(0, 3, 1, 2).half() / 255.0              # normalize on the GPU
    with torch.no_grad(): net(x)
phase("16 frames/call, GPU preprocessing (calls/s)", batch_gpu_preprocess)
stop.set()
