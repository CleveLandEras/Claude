// 用过的样式记录，不是每条都要套的固定规格：画面和节奏要从每条的内容里长出来，先读 剪辑认知.md。
// 第三版《等待》只用了这里的字体（F.serif），其余是它自己从“心跳线”这个母题里来的。
//
// 第二版用的（U / S，照 Orbit 做的界面风，号主说格式不适配）：纯黑底；只用一种蓝（靛蓝到青）做点阵和光；毛玻璃卡片带细亮边；
// 光都是模糊过的；现代无衬线，用字重做对比（前半句细、后半句粗）；每场只放一个控件、演示一个动作；
// 字在原地变；换场是卡片缩成药丸再展开，由红点（正在等的你）带过去；每一帧都有东西在动，缓动带一点弹性。
// 不要（avoid）：霓虹线条；紫色渐变；所有东西都淡入淡出；硬切；一屏好几个焦点；卡通；高饱和。

export const U = {
  bg: '#000000',
  ink: '#F4F6FB',
  soft: 'rgba(214, 220, 236, 0.72)',
  mute: 'rgba(190, 198, 220, 0.42)',
  faint: 'rgba(190, 198, 220, 0.16)',
  indigo: [92, 86, 255] as const,
  cyan: [64, 200, 255] as const,
  readout: '#A9D2FF',
  red: '#FF4B3E',
};

export const S = {
  sans: '"SF Pro Display", system-ui, -apple-system, "PingFang SC", sans-serif',
};

// 点阵的颜色：t=0 靛蓝，t=1 青
export const blue = (t: number) => {
  const k = Math.max(0, Math.min(1, t));
  return U.indigo.map((v, i) => Math.round(v + (U.cyan[i] - v) * k)) as [number, number, number];
};

// 第一版（编辑排版风，没被采用）用的，留着让 Opening_v1 还能编译
export const C = {
  bg: '#06070A',
  pool: '#141925',
  ink: '#ECE6D8',
  dim: 'rgba(236, 230, 216, 0.55)',
  faint: 'rgba(236, 230, 216, 0.22)',
  hair: 'rgba(236, 230, 216, 0.14)',
  gold: '#C9A35E',
  goldHi: '#E6CC90',
  spark: '#EEF5FF',
};

export const F = {
  serif: '"Songti SC", "Noto Serif SC", serif',
  latin: 'Baskerville, "Libre Baskerville", serif',
  mono: 'Menlo, monospace',
};

// 版心：左边距 180，字不全居中
export const L = 180;

// 小号英文标注：小型大写，字距拉开
export const smallCaps = (size = 15): React.CSSProperties => ({
  fontFamily: F.latin,
  fontSize: size,
  letterSpacing: '0.32em',
  textTransform: 'uppercase',
  color: C.dim,
});
