# -*- coding: utf-8 -*-
"""Fable 开场白 (af39): 从 build/af39_remarks/*.txt 读台词, 生成操作列表。

文案文件每行 `场景键|性格键|台词`, 台词一个字不改, 构建时读入。
pick_ops 把 (场景, 键) 映射成编号 (从 1 开始, 0 表示没有), 生成
try_begin/else_try 嵌套: 先按 (场景, 键) 分支, 再按 idx 取模取句。
文件里出现 scenes/keys 之外的场景或键就 raise, 防止拼写错误悄悄丢句子。
"""
import io
import os

from header_operations import (
    try_begin, else_try, try_end, eq, store_mod, str_store_string,
)

_REMARKS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'af39_remarks')


def _load(filename):
    """读一个文案文件, 返回 {(scene, key): [台词, ...]} (保持文件顺序)。"""
    path = os.path.join(_REMARKS_DIR, filename)
    groups = {}
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            scene, key, text = line.split('|', 2)
            groups.setdefault((scene, key), []).append(text)
    return groups


def pick_ops(filename, scenes, keys, scene_var, key_var, idx_var, sreg, wrap=None):
    """生成按 (场景编号, 键编号) 选句的操作列表, 写进 sreg。

    scenes / keys 是有序列表, 编号从 1 开始 (0 表示没有)。
    idx_var 由调用方传进来, 是一个已经算好的非负整数局部变量。
    wrap: 可选, wrap(key, text) -> 显示用的整句 (匪帮用来加头目名前缀)。
    某个 (场景, 键) 组合在文件里没有台词就跳过, 不生成分支。
    文件里出现 scenes/keys 之外的场景或键, 直接 raise。
    """
    groups = _load(filename)
    for (scene, key) in groups:
        if scene not in scenes:
            raise ValueError('af39 %s: unknown scene %r' % (filename, scene))
        if key not in keys:
            raise ValueError('af39 %s: unknown key %r' % (filename, key))
    ops = [(try_begin,)]
    first = True
    for si, scene in enumerate(scenes, 1):
        for ki, key in enumerate(keys, 1):
            lines = groups.get((scene, key))
            if not lines:
                continue
            if not first:
                ops.append((else_try,))
            first = False
            ops.append((eq, scene_var, si))
            ops.append((eq, key_var, ki))
            ops.append((store_mod, ":af39_i", idx_var, len(lines)))
            ops.append((try_begin,))
            for n, text in enumerate(lines):
                if n:
                    ops.append((else_try,))
                ops.append((eq, ":af39_i", n))
                if wrap is not None:
                    text = wrap(key, text)
                ops.append((str_store_string, sreg, "@" + text))
            ops.append((try_end,))
    ops.append((try_end,))
    return ops
