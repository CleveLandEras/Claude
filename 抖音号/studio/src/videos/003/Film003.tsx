// 003《消息提醒》成片（Notice003Film）：和灰框同一套时间、动作（Gray003.tsx 的 NoticeBody），
// 前 15 秒用成片画法（暗房间、暖灯、真手机、成片小人），15 秒以后先沿用 v3 灰框画面；字幕带、字幕、“AI 生成”标全片用第二条成片的样式。不加声音。
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ModeCtx} from './mode';
import {GRAY003_FRAMES, NoticeBody} from './Gray003';
import {FPS} from './timeline';

export const FILM003_FRAMES = GRAY003_FRAMES;
export const FILM_UNTIL = 15;   // 精修到这一秒

export const Film003: React.FC = () => {
  const fr = useCurrentFrame();
  return (
    <ModeCtx.Provider value={{film: fr < FILM_UNTIL * FPS, text: true}}>
      <NoticeBody />
    </ModeCtx.Provider>
  );
};
