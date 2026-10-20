# 设计概要配图的裁图定义（an_推送后台_设计概要.py --crop 读这里）
# 每张图：pg＝原型页 id；box＝要框进来的元素 [(CSS 选择器, 文字片段或 None), …]，取外接框；
#   pads＝上右下左留边（CSS 像素，留边涂白，编号放在留边里）；until＝下沿截到某元素底边；clipx＝只取左侧这么宽；css＝截这一页时追加的样式。
# marks＝编号 [(编号, 选择器, 文字片段, 放哪边)]：r 右侧、l 左侧、t 上方、b 下方、tr 右上角、in 元素内右端。
# 选择器都在该页 section 内找：.win 原型窗口，.stc .ui 右栏或「其他状态」里的小画面。
T = (50, 6, 6, 6)        # 编号在上方的表格：上边多留
L = (6, 6, 6, 44)        # 编号在左侧
CROPS = {
    # 模块 1 新建推送（原型页 3）
    'm1_steps': dict(pg='p3', box=[('.win .steps', None)], marks=[(1, '.win .steps', None, 'r')]),
    'm1_obj':   dict(pg='p3', box=[('.win .sec', '发送对象')],
                     marks=[(2, '.win .sec .f', '发送对象', 'r'), (3, '.win .sec .f', '排除群组', 'r'), (4, '.win .estb .ft', None, 'r')]),
    'm1_conf':  dict(pg='p3', box=[('.win .fl', '预计'), ('.win .fun', None)], marks=[(5, '.win .fun', None, 'r')]),
    'm1_test':  dict(pg='p3', box=[('.win .f', '测试发送')], marks=[(6, '.win .f', '测试发送', 'r')]),
    # 模块 2 按行为推送（原型页 4 新建、页 5 修改运行中）
    'm2_form':  dict(pg='p4', box=[('.win .sec', '发送对象'), ('.win .sec', '触发行为')], pads=(6, 44, 6, 44),
                     marks=[(1, '.win .f', '触发的玩家', 'l'), (2, '.win .ddf', None, 'tr'), (3, '.win .f', '提醒次数', 'r'), (4, '.win .estb', None, 'r')]),
    'm2_ver':   dict(pg='p5', box=[('.win .hdr', None), ('.win .banner', None)], marks=[(5, '.win .banner', None, 'r')]),
    # 模块 3 短信、Facebook、LINE 与快显（原型页 6、7、10）
    'm8_sms':   dict(pg='p6', box=[('.win .f.tp', None), ('.win .f', '链接'), ('.win .hint', '短链')],
                     marks=[(1, '.win .f.tp', None, 'r'), (2, '.win .f', '链接', 'r')]),
    'm8_fb':    dict(pg='p7', box=[('.win .f', '按钮'), ('.win .hint', '追踪')], marks=[(3, '.win .f', '按钮', 'r')]),
    'm8_fbto':  dict(pg='p7', box=[('.win .estb', None)], marks=[(4, '.win .estb', None, 'r')]),
    'm8_qx':    dict(pg='p10', box=[('.win .sec', '发送时间')], pads=(40, 6, 6, 6), css='section#p10 .win .estb{visibility:hidden}',
                     marks=[(5, '.win .sec .sh .seg', None, 't')]),
    # 模块 4 弹窗：规则与对象（原型页 8 列表、页 9 编辑）
    'm7_tab':   dict(pg='p8', box=[('.win table', '弹窗排序')], until=('.win table tr', '活动类·回流'), pads=T,
                     marks=[(1, '.win table th', '弹窗排序', 't'), (2, '.win table th', '今日', 't')]),
    'm7_edit':  dict(pg='p9', box=[('.win .nc', '对象')], marks=[(3, '.win .ef', '排除群组', 'r')]),
    'm7_ovl':   dict(pg='p9', box=[('.stc .ui .rel', '上架规则重叠')], marks=[(4, '.stc .ui .rel', '上架规则重叠', 'r')]),
    # 模块 5 弹窗：保存与下架（原型页 9 保存确认与测试预览、页 8 下架提示）
    'm7_save':  dict(pg='p9', box=[('.stc .dlg', '保存「')], marks=[(1, '.stc .dlg', '保存「', 'r')]),
    'm7_bar':   dict(pg='p9', box=[('.win span', '保存前弹出确认框'), ('.win .ebtn.b', '保存')], pads=(36, 6, 6, 6), marks=[(2, '.win .ebtn', '测试预览', 't')]),
    'm7_off':   dict(pg='p8', box=[('.stc .ui', '下架')], marks=[(3, '.stc .ui', '下架', 'r')]),
    # 模块 6 频率上限与勿扰（原型页 11；单条例外取自页 3 右栏）
    'm3_tab':   dict(pg='p11', box=[('.win table.tb', '推播')], pads=T,
                     marks=[(1, '.win table.tb th', '每人每天上限', 't'), (2, '.win table.tb th', '计 1 次', 't'), (3, '.win table.tb th', '截断顺序', 't')]),
    'm3_exc':   dict(pg='p3', box=[('.stc .ui', '仍计入')], marks=[(4, '.stc .ui', '仍计入', 'r')]),
    # 模块 7 勿扰时段（原型页 11）
    'm3_dnd':   dict(pg='p11', box=[('.win .sec', '勿扰时段')], marks=[(1, '.win .sec', '勿扰时段', 'tr')]),
    'm3_night': dict(pg='p11', box=[('.stc .ui', '一位玩家的夜间推送')], marks=[(2, '.stc .ui', '一位玩家的夜间推送', 'r')]),
    'm3_save':  dict(pg='p11', box=[('.stc .ui', '确认保存以下修改')], marks=[(3, '.stc .ui', '确认保存以下修改', 'r')]),
    # 模块 7 失败与重试（原型页 1 待处理、页 13 失败明细、页 2 停止确认）
    'm4_todo':  dict(pg='p1', box=[('.win .sec', '待处理')], marks=[(4, '.win .sec .sh', '待处理', 'in')]),
    'm4_fail':  dict(pg='p13', box=[('.win .pd-cd', '服务商未受理')], pads=(6, 44, 6, 44),
                     marks=[(1, '.win .pd-cl', '推送服务超时', 'l'), (2, '.win .pd-cl', '当场拒绝', 'r'), (3, '.win .pd-cf', '重试失败部分', 'r')]),
    'm4_stop':  dict(pg='p2', box=[('.stc .ui', '停止「')], marks=[(5, '.stc .ui', '停止「', 'tr')]),
    # 模块 8 数据看板（原型页 12）
    'm5_board': dict(pg='p12', box=[('.win .f', '人群'), ('.win .pd-tabs', None), ('.win .sec', '游戏外推送 · 从发送算起')], pads=(6, 6, 6, 44),
                     marks=[(1, '.win .pd-bt', '游戏外推送', 'l'), (2, '.win .pd-bt', '游戏内推送', 'l'), (3, '.win .pd-lg', None, 'l'),
                            (4, '.win .pd-bt', '游戏外推送', 'r'), (5, '.win .f', '人群', 'l')]),
    # 模块 9 玩家查询（原型页 14）
    'm6_can':   dict(pg='p14', box=[('.win table', '能否收到')], pads=T,
                     marks=[(1, '.win table th', '能否收到', 't'), (2, '.win table th', '今日已收', 't')]),
    'm6_rec':   dict(pg='p14', box=[('.win table', '结果')], pads=T, marks=[(3, '.win table th', '结果', 't')]),
    # 模块 10 操作纪录与权限（原型页 15；只读角色取自页 2）
    'm6_log':   dict(pg='p15', box=[('.win table', '操作人')], until=('.win table tr', '10/09 16:12'), pads=T,
                     marks=[(1, '.win table th', '改动内容', 't')]),
    'm6_ro':    dict(pg='p2', box=[('.stc .ui', '只读角色')], marks=[(2, '.stc .ui', '只读角色', 'tr')]),
    # 模块 11 迁移与切换（原型页 16）
    'm9_sw':    dict(pg='p16', box=[('.win .rel.key', '由哪里发')], until=('.win .ef.rel', '选定推播'), marks=[(1, '.win .ef.rel', '选定推播', 'r')]),
}
