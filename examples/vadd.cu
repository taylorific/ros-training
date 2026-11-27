#include <cstdio>
#include <cuda_runtime.h>

__global__ void add(const float *a, const float *b, float *c, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) c[i] = a[i] + b[i];
}

int main() {
  const int n = 1 << 24;                       // 16M floats
  float *a, *b, *c;
  cudaMallocManaged(&a, n * sizeof(float));    // unified memory: visible to CPU and GPU
  cudaMallocManaged(&b, n * sizeof(float));
  cudaMallocManaged(&c, n * sizeof(float));
  for (int i = 0; i < n; i++) { a[i] = 1.0f; b[i] = 2.0f; }

  add<<<(n + 255) / 256, 256>>>(a, b, c, n);   // 65,536 blocks x 256 threads
  cudaDeviceSynchronize();

  cudaDeviceProp p;
  cudaGetDeviceProperties(&p, 0);
  printf("%s: %d SMs, c[0]=%.1f c[n-1]=%.1f\n", p.name, p.multiProcessorCount, c[0], c[n - 1]);
  return 0;
}
