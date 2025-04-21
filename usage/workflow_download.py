from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1128716
JM1076804
JM481546
JM78390
JM1047399
JM630345
JM614194
JM588458
JM588455
JM441635
JM573186
JM546722
JM340547
JM304197
JM486709
JM484047
JM303315
JM484046
JM446035
JM441611
JM419260
JM340562
JM281497
JM265292
JM273115
JM273114
JM1131983
JM1132644
JM332609
JM1095527
JM1132604
JM1128716
JM1120109
JM1120618
JM1119855
JM1124521
JM1120110
JM1121586
JM1131337
JM1128213
JM1130635
JM1119997
JM1123398
JM1125812
JM1119889
JM1126269
JM1120595
JM1122532
JM1127144
JM1121143
JM1122278
JM1128214
JM1120146
JM1120022
JM1126328
JM1124589
JM1121588
JM1124522
JM1127392
JM1124868
JM1128115
JM1128776
JM1123390
JM1130071
JM1120679
JM1125776
JM1124859
JM1124270
JM1126193
JM1122251
JM1132399
JM1132015
JM391555
JM1110922
JM1093900
JM309623
JM143092
JM1067736
JM499628
JM424074
JM422255
JM426162
JM604673
JM1038982
JM101577
JM415254
JM414201
JM405553
JM1132007
JM1131685
JM1130517
JM1129220
JM598997
JM1122282
JM1123444
JM1115968
JM1113271
JM1099613
JM1099438
JM1095374
JM1095381
JM1092992
JM1092915
JM1091278
JM1086680
JM1084400
JM1083620
JM1076004
JM1071978
JM1068567
JM1066515
JM1063982
JM1058686
JM1054389
JM1049898
JM1049311
JM1045651
JM1045612
JM1040796
JM1040832
JM1035109
JM1035118
JM1036719
JM1033963
JM1033255
JM1032498
JM1028168
JM1023962
JM1022591
JM1019848
JM1018591
JM1018059
JM1013245
JM1013834
JM332711
JM349621
JM340806
JM487310
JM463262
JM282811
JM496414
JM256005
JM630405
JM388876
JM447571
JM481972
JM409857
JM409642
JM1063983
JM514165
JM647403
JM544188







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
