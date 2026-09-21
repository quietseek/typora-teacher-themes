PALETTES = [
    dict(name='雾蓝', accent='#355f99', ink='#283548', muted='#5b687b', tint='#edf3fb', rule='#ccd9ea', canvas='#f4f7fb', selection='#d5e2f4', description='清晰理性，适合化学备课与知识梳理。'),
    dict(name='葡萄紫', accent='#74589a', ink='#372d46', muted='#6c617b', tint='#f3eff8', rule='#ddd3e8', canvas='#f8f6fb', selection='#e3d8ef', description='柔和沉静，适合长时间阅读与讲义。'),
    dict(name='暖棕', accent='#876047', ink='#44342a', muted='#786757', tint='#f7f0e8', rule='#e3d5c6', canvas='#faf7f2', selection='#ebddcc', description='温暖纸感，适合教案与教学反思。'),
    dict(name='胭脂', accent='#9b5069', ink='#442e36', muted='#7a626c', tint='#fbf0f3', rule='#ebd3dc', canvas='#fcf7f8', selection='#f1d6e0', description='重点鲜明，适合例题、讲评与复习材料。'),
    dict(name='石墨', accent='#505b69', ink='#303842', muted='#64707e', tint='#f0f3f6', rule='#d5dce4', canvas='#f6f7f9', selection='#dce3eb', description='简洁克制，适合作业、试题和正式文档。'),
]

def palette_css(palette):
    tokens = ['accent', 'ink', 'muted', 'tint', 'rule', 'canvas', 'selection']
    return ':root { ' + ' '.join(f'--qm-{key}: {palette[key]};' for key in tokens) + ' }'
