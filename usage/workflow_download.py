from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1119997
JM1119536
JM1117252
JM1114807
JM1113861
JM1102211
JM1102213
JM1100771
JM1100557
JM1098164
JM1087325
JM1101095
JM1054399
JM1087889
JM1086625
JM1085081
JM1085408
JM1083591
JM1083590
JM1060375
JM1051458
JM1033514
JM1029520
JM1033519
JM1029119
JM1027089
JM586480
JM532319
JM246530
JM73230
JM502301
JM96580
JM180818
JM129903
JM420727
JM314044
JM81399
JM385378
JM331964
JM304473
JM288795
JM105177
JM86713
JM86596
JM86595
JM86326
JM74900
JM1016921
JM650293
JM649652
JM649654
JM648202
JM647789
JM646989
JM643128
JM89436
JM89433
JM15162
JM13787
JM641548
JM638685
JM638098
JM637736
JM637339
JM636688
JM634736
JM1126238
JM1125570
JM1125198
JM1124229
JM1120122
JM1117873
JM1096578
JM1110623
JM1093042
JM1092030
JM1092051
JM1088740
JM1081256
JM1062228
JM1060165
JM1044848
JM1047399
JM648195
JM627904
JM627905
JM623538
JM620805
JM616255
JM607084
JM596436
JM578238
JM568056
JM564569
JM562490
JM562188
JM561252
JM561251
JM1016834
JM558661
JM561159
JM545354
JM545711
JM544661
JM539601
JM541052
JM541528
JM541051
JM539382
JM539600
JM539864
JM1016903
JM539404
JM536268
JM536271
JM535521
JM535267
JM534050
JM532921
JM531972
JM529529
JM529537
JM525497
JM524099
JM514070
JM518053
JM521352
JM522292
JM517510
JM519144
JM516998
JM512209
JM509847
JM507124
JM505202
JM505047
JM499299
JM516638





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
