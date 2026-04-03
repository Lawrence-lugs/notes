---
title: "Interesting Quantization Observations"
date: "2025-01-17"
toc: true
---
# Spreads, RMSE and SNR vs Bits

With playing around with code from [github.com/Lawrence-lugs/hwacc_design_garage](https://github.com/Lawrence-lugs/hwacc_design_garage)

```verilog
wDimX = 8
wDimY = 128
xBatches = 10
wBits = 8
xBits = 8
seed = 0
outBits = 8
# np.random.seed(seed)

wShape = (wDimX, wDimY)
xShape = (xBatches, wDimY)

w = np.random.uniform(-1, 1, wShape)
x = np.random.uniform(-1, 1, xShape)
wx = w @ x.T

# Calculate the output scale
wx_qtensor = quant.quantized_tensor(
    real_values=wx,
    precision=outBits,
    mode='maxmin'
)

# Set numpy printing to at most 3 significant digits
np.set_printoptions(precision=3)

# print('w\n',w)
# print('x\n',x)
# print('wx\n',wx)

# Quantize the weights and input
wQ = quant.quantized_tensor(
    real_values=w,
    precision=wBits,
    mode='maxmin'
)
xQ = quant.quantized_tensor(
    real_values=x,
    precision=xBits,
    mode='maxmin'
)
wQxQ_qvals_t = wQ.quantized_values @ xQ.quantized_values.T

out_scale = wx_qtensor.scale

wQxQ_t = quant.quantized_tensor(
    quantized_values=wQxQ_qvals_t,
    scale=out_scale,
    zero_point = 0
)

wQxQ = quant.scaling_quantized_matmul(
    wQ, xQ, outBits, internalPrecision=16, out_scale = out_scale
)

import matplotlib.pyplot as plt

plt.scatter(wx.flatten(), wQxQ.fake_quantized_values.flatten())

wx, wQxQ.fake_quantized_values, wQxQ.quantized_values
```

Changing wBits, xBits and outBits gives some interesting tradeoffs

![image.png](attachments/image.png)

![image.png](attachments/image%201.png)

![image.png](attachments/image%202.png)

![image.png](attachments/image%203.png)

![image.png](attachments/image%204.png)

![image.png](attachments/image%205.png)

![image.png](attachments/image%206.png)

![image.png](attachments/image%207.png)

There should be some mathematical expected SNR based on quantization that corresponds to these.

# Weight Quantization

weights need at least 2 bits to be viable in the ternary form

they don’t seem to quantize into -2 because it’s symmetric over the zero point

![image.png](attachments/image%208.png)

With 1-bit quantization, only zeros appear because the zero point is 0, yet there’s only 1 bit to represent everything.

### ADC Outputs and Encoding

```verilog
00 0000 0000
98 7654 3210
```