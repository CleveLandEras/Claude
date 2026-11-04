// 003 画法开关：同一套时间和动作，灰框（Notice003Gray）和成片（Notice003Film）共用。
// film：这一帧用成片画法画场景（人、手机、光）；text：字幕带、字幕、“AI 生成”标用成片样式（第二条成片那套）。
import React from 'react';

export type Mode = {film: boolean; text: boolean};
export const ModeCtx = React.createContext<Mode>({film: false, text: false});
export const useMode = () => React.useContext(ModeCtx);
