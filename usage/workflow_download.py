from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1202344
JM648074
JM1202507
JM1117824
JM611836
JM1202200
JM641743
JM1202016
JM1201665
 JM1201923
JM1201600
JM1201857
JM1201858
JM1202203
 JM1202829
JM1201863
 JM1201856
 JM1201942
JM1201592
JM1201591
JM1202591
 JM1202093
 JM1202224
 JM1201595
JM1202680
JM1201599
JM1202576
 JM1202080
 JM1202079
JM1201595
 JM1202225
 JM1201596
JM1202580
 JM1202857
 JM1202202
 JM1202630
 JM1203039
 JM1201842
JM1201622
 JM1202238
JM1201951
JM1202338
JM1201689
JM1202337
JM1201989
 JM1202397
JM1201652
JM1202084
 JM1202767
 JM1202304
 JM1202085
 JM1201980
 JM1201963
 JM1202772
 JM373933
 JM372238
 JM361757
 JM295836
 JM295835
 JM295832
JM295828
 JM547912
JM1089399
JM1089400
 JM1118479
JM1201606
JM1202015
JM1202353
JM1201942
JM1202216
JM1202882
 JM1202850
JM1202863
JM1202204
 JM1202864
JM1201623
 JM1202990
 JM1202969
JM1202975
 JM1202983
JM1202981
JM1200510
 JM1199910
 JM1200284
JM1199148
JM1196608
 JM1198346
JM1186817
 JM1145801
 JM1144561
 JM1136877
 JM1137714
 JM1125198
JM1088740
 JM1062228
JM1060165
 JM1065113
 JM1054411
 JM1047399
 JM1044848
 JM631049
 JM623260
JM588453
JM583276
 JM575197
 JM577787
JM577373
 JM501220
JM545439
JM535538
 JM535601
JM524420
JM1164499
 JM1099429
JM1015390
 JM1182387
JM1047398
 JM614194
 JM588458
 JM588454
JM484047
JM273115
 JM265292
 JM1093874
 JM391297
 JM523547
 JM502182
 JM477548
JM473270
JM474755
 JM1181381
 JM1119843
JM1017559
 JM1047410
 JM631843
 JM206792
 JM1098170
JM1200381
 JM1190476
JM1127414
 JM1025760
 JM1058215
JM650274
JM640413
 JM640505
JM539919
JM508784
 JM518500
JM402943
 JM353558
 JM298117
 JM280104
 JM274473
 JM271182
 JM268637
 JM241075
JM241714
 JM222101
 JM468004
 JM468003
JM457849
JM457845
JM439144
JM432869
JM1202955
 JM1202982









'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
