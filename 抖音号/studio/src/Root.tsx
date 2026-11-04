import {Composition, Still} from 'remotion';
import {Cover} from './videos/001/Cover';
import {Full} from './videos/001/Full';
import {Opening} from './videos/001/Opening';
import {CoverLook} from './videos/001/look/CoverLook';
import {FinalFilm} from './videos/001/look/FinalFilm';
import {LOOK_FRAMES, LookSample} from './videos/001/look/LookSample';
import cuesV4 from './videos/001/cues_v4.json';
import full from './videos/001/full.json';
import {CardSheet, ExprSheet, PoseSheet} from './videos/style_test/Sheets';
import {A1, A2, A3, A4, A5, AMini} from './videos/style_test/FlatShots';
import {B1, B2, B3, B4, B5, BMini} from './videos/style_test/InkShots';
import {COMPARE_H, COMPARE_W, CompareSheet, MiniStrip, PHONE_H, PHONE_W, PhoneSheet, Review} from './videos/style_test/Compare';
import {PoseSheet002} from './videos/002/PoseSheet';
import {GRAY_FRAMES, Gray002} from './videos/002/Gray002';
import {Cover002} from './videos/002/Cover002';
import {FILM_FRAMES, Film002} from './videos/002/film/Film002';
import {FilmSheet002} from './videos/002/film/FilmSheet';
import {GRAY003_FRAMES, Gray003} from './videos/003/Gray003';
import {FILM003_FRAMES, Film003} from './videos/003/Film003';
import {NOTICE8_FRAMES, Notice8} from './videos/003/Notice8';
import {NOTICE9_FRAMES, Notice9} from './videos/003/Notice9';
import {NOTICE10_FRAMES, Notice10} from './videos/003/Notice10';
import {Cover003} from './videos/003/Cover003';
import {Cover10} from './videos/003/Cover10';
import {Cover11} from './videos/003/Cover11';
import {NOTICE11_FRAMES, Notice11} from './videos/003/Notice11';

export const Root: React.FC = () => (
  <>
    {/* 笔记 001《等待》整条 */}
    <Composition id="Wait001" component={Full} durationInFrames={full.frames} fps={full.fps} width={1920} height={1080} />
    {/* 《等待》终版：暖光剪影画风的整条（10/28） */}
    <Composition id="Wait001Final" component={FinalFilm} durationInFrames={full.frames} fps={full.fps} width={1920} height={1080} />
    <Still id="Wait001FinalCover43" component={CoverLook} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
    <Still id="Wait001FinalCover34" component={CoverLook} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    {/* 观感样片：开头 0–12.2 秒，暖光房间和人（videos/001_等待/观感对照.md） */}
    <Composition id="Wait001Look" component={LookSample} durationInFrames={LOOK_FRAMES} fps={30} width={1920} height={1080} />
    {/* 封面：横版 4:3、竖版 3:4 */}
    <Still id="Wait001Cover43" component={Cover} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
    <Still id="Wait001Cover34" component={Cover} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    {/* 第四版开头样片（留作对照） */}
    <Composition id="Wait001Opening" component={Opening} durationInFrames={cuesV4.frames} fps={cuesV4.fps}
      width={1920} height={1080} />
    {/* 画风测试（videos/画风测试/说明.md）：姿势表、表情表 */}
    <Composition id="StylePosesA" component={PoseSheet} durationInFrames={30} fps={30} width={1600} height={1960} defaultProps={{kind: 'flat' as const}} />
    <Composition id="StylePosesB" component={PoseSheet} durationInFrames={30} fps={30} width={1600} height={1960} defaultProps={{kind: 'ink' as const}} />
    <Composition id="StyleFacesA" component={ExprSheet} durationInFrames={30} fps={30} width={1600} height={1330} defaultProps={{kind: 'flat' as const}} />
    <Composition id="StyleFacesB" component={ExprSheet} durationInFrames={30} fps={30} width={1600} height={1330} defaultProps={{kind: 'ink' as const}} />
    <Composition id="StyleCardsA" component={CardSheet} durationInFrames={30} fps={30} width={1800} height={1300} defaultProps={{kind: 'flat' as const}} />
    {/* 画风 A：五个牌桌镜头（静帧取第 20 帧）和 5 秒小动作片 */}
    <Composition id="StyleA1" component={A1} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleA2" component={A2} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleA3" component={A3} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleA4" component={A4} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleA5" component={A5} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleAMini" component={AMini} durationInFrames={150} fps={30} width={1080} height={1920} />
    {/* 画风 B：同样五个镜头和小动作片 */}
    <Composition id="StyleB1" component={B1} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleB2" component={B2} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleB3" component={B3} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleB4" component={B4} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleB5" component={B5} durationInFrames={90} fps={30} width={1080} height={1920} />
    <Composition id="StyleBMini" component={BMini} durationInFrames={150} fps={30} width={1080} height={1920} />
    {/* 对照：A、B 同一镜头左右并排；按手机实际大小缩小 */}
    <Composition id="StyleCompare" component={CompareSheet} durationInFrames={150} fps={30} width={COMPARE_W} height={COMPARE_H} />
    <Composition id="StyleComparePhone" component={PhoneSheet} durationInFrames={150} fps={30} width={PHONE_W} height={PHONE_H} />
    <Composition id="StyleMiniStripA" component={MiniStrip} durationInFrames={150} fps={30} width={3160} height={740} defaultProps={{kind: 'A' as const}} />
    <Composition id="StyleMiniStripB" component={MiniStrip} durationInFrames={150} fps={30} width={3160} height={740} defaultProps={{kind: 'B' as const}} />
    <Composition id="StyleReviewA" component={Review} durationInFrames={150} fps={30} width={3190} height={1000} defaultProps={{kind: 'A' as const}} />
    <Composition id="StyleReviewB" component={Review} durationInFrames={150} fps={30} width={3190} height={1000} defaultProps={{kind: 'B' as const}} />
    <Composition id="StyleCardsB" component={CardSheet} durationInFrames={30} fps={30} width={1800} height={1300} defaultProps={{kind: 'ink' as const}} />
    {/* 002《被坑多了，人会变狠吗？》横屏：补的新姿势一览 */}
    <Composition id="Harsh002Poses" component={PoseSheet002} durationInFrames={30} fps={30} width={2400} height={1500} />
    {/* 002 横屏灰框预演（锁节奏用，不是成片）：时间表 videos/002/timeline.json */}
    <Composition id="Harsh002Gray" component={Gray002} durationInFrames={GRAY_FRAMES} fps={30} width={1920} height={1080} />
    {/* 002 封面：竖版 3:4、横版 4:3（videos/002/Cover002.tsx） */}
    <Still id="Harsh002Cover34" component={Cover002} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    <Still id="Harsh002Cover43" component={Cover002} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
    {/* 002 横屏成片：画法换成正式的，时间和字幕仍读 videos/002/timeline.json（videos/002/film/Film002.tsx） */}
    <Composition id="Harsh002Film" component={Film002} durationInFrames={FILM_FRAMES} fps={30} width={1920} height={1080} defaultProps={{audio: true}} />
    <Composition id="Harsh002FilmSheet" component={FilmSheet002} durationInFrames={30} fps={30} width={2400} height={2100} />
    {/* 003《消息提醒》横屏灰框预演（锁节奏用，不是成片）：时间表 videos/003/timeline.ts */}
    <Composition id="Notice003Gray" component={Gray003} durationInFrames={GRAY003_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 成片：前 15 秒精修，后面先沿用灰框 v3 画面；时间、字幕同灰框（videos/003/Film003.tsx） */}
    <Composition id="Notice003Film" component={Film003} durationInFrames={FILM003_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 第八版成片（11/02）：时间表 videos/003/timeline8.ts，画面 videos/003/Notice8.tsx */}
    <Composition id="Notice003V8" component={Notice8} durationInFrames={NOTICE8_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 第九版成片（11/02 深夜）：时间表 videos/003/timeline9.ts，画面 videos/003/Notice9.tsx */}
    <Composition id="Notice003V9" component={Notice9} durationInFrames={NOTICE9_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 v10（第三版，不教学的观点片，11/04）：时间表 videos/003/timeline10.ts，画面 videos/003/Notice10.tsx */}
    <Composition id="Notice003V10" component={Notice10} durationInFrames={NOTICE10_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 v11（第四版：手机提醒，不是微信，11/04）：时间表 videos/003/timeline11.ts，画面 videos/003/Notice11.tsx */}
    <Composition id="Notice003V11" component={Notice11} durationInFrames={NOTICE11_FRAMES} fps={30} width={1920} height={1080} />
    {/* 003 封面：竖版 3:4、横版 4:3（videos/003/Cover003.tsx） */}
    <Still id="Notice003Cover34" component={Cover003} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    <Still id="Notice003Cover43" component={Cover003} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
    {/* 003 v10 封面 */}
    <Still id="Notice003Cover10Tall" component={Cover10} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    <Still id="Notice003Cover10Wide" component={Cover10} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
    {/* 003 v11 封面 */}
    <Still id="Notice003Cover11Tall" component={Cover11} width={1080} height={1440} defaultProps={{w: 1080, h: 1440}} />
    <Still id="Notice003Cover11Wide" component={Cover11} width={1440} height={1080} defaultProps={{w: 1440, h: 1080}} />
  </>
);
