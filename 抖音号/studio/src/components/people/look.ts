// 人的“长相”：颜色和发型。两种画风共用 hair（墨线小人只用 hair 决定头顶那几笔）。
export type Hair = 'short' | 'bob';
export type Look = {
  skin: string; skinShade: string;
  hair: string; hairHi: string;
  top: string; topShade: string;          // 上衣（主色、暗面）
  bottom: string; bottomShade: string;    // 裤子
  shoe: string; shoeShade: string; sole: string;
  blush: string; mouth: string; brow: string; eye: string;
  hairStyle: Hair;
  hood: boolean;                           // 连帽衫
  coat?: boolean;                          // 长外套（下摆盖到大腿）
};

// 主角“你”：灰蓝连帽衫，深色短发。这一个颜色固定下来当号的标志
export const ME: Look = {
  skin: '#F3CDAA', skinShade: '#DDA987',
  hair: '#2A2122', hairHi: '#3E3233',
  top: '#5F7EA3', topShade: '#4A6487',
  bottom: '#34313C', bottomShade: '#27242E',
  shoe: '#ECE5D8', shoeShade: '#CFC6B7', sole: '#B9AE9C',
  blush: '#F0958A', mouth: '#4A2626', brow: '#2A2122', eye: '#1D1719',
  hairStyle: 'short', hood: true,
};

// 另一个人：橄榄绿长外套，齐肩短发
export const OTHER: Look = {
  skin: '#EFC6A2', skinShade: '#D6A07E',
  hair: '#4A3328', hairHi: '#5E4236',
  top: '#7F8A5C', topShade: '#646E45',
  bottom: '#3B3633', bottomShade: '#2C2826',
  shoe: '#3A2E28', shoeShade: '#2A211C', sole: '#1E1814',
  blush: '#EE9387', mouth: '#4A2626', brow: '#3A2820', eye: '#1D1719',
  hairStyle: 'bob', hood: false, coat: true,
};
