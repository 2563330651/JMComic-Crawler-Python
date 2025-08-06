from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
 JM1125570
 JM1123435
 JM1120679
 JM1195342
JM1189380
 JM1175736
JM1174351
 JM1174339
 JM1173268
JM1168499
 JM1124931
 JM1124852
 JM1096435
 JM1093337
 JM1092943
 JM1092070
 JM1091600
JM1087854
 JM1087823
 JM1088402
JM1075453
 JM1072207
JM1069754
 JM1069284
 JM1067724
 JM1066904
 JM1061008
JM1033963
JM1021076
 JM618618
 JM616258
 JM604781
 JM1194048
JM1190057
 JM1192412
 JM1192399
JM1191284
 JM644633
 JM542657
 JM306828
 JM475261
 JM323719
 JM642257
 JM1114798
 JM1078959
 JM1078893
 JM1078270
 JM1071456
 JM1072262
 JM1027653
JM1025496
 JM1021468
 JM1021117
JM1014468
JM1013173
 JM1014484
 JM1017290
 JM630364
 JM598473
 JM543574
 JM1113715
 JM1098792
JM1092956
JM1093940
JM1094403
 JM1092924
 JM1087871
 JM1077320
JM1078972
JM1076793
JM1063660
 JM1058883
 JM1058910
 JM1052122
 JM179445
 JM1202981
 JM1202983
 JM461970
 JM1015690
 JM401891
 JM361199
JM361982
 JM1202216
 JM1201506
 JM1201032
 JM1200978
 JM1201231
JM1200381
JM1200198
 JM1200151
JM1199757
 JM1196806
 JM1196425
JM1196430
JM1195762
JM1195859
 JM285224
 JM1195664
JM1195343
 JM302471
 JM219168
 JM1173751
 JM1141349
 JM1034654
 JM625790
JM404884
 JM1053385
 JM1182993
JM1174459
 JM1169679
JM1173677
 JM1176888
JM1160191
 JM1152145
 JM1152984
 JM1152982
 JM1133120
JM1141306
JM1100966
 JM1071320
JM639407
 JM1062571
 JM1062577
 JM1054172
 JM1038510
 JM1201423
 JM1068578
 JM1070326
 JM592047
 JM1034420
JM1033440
 JM1033181
JM1030112
 JM1029514
JM1028368
 JM1025545
 JM1025543
 JM1025317
 JM1020305
 JM1023165
 JM1023164
 JM649532
 JM612847
 JM646604
 JM1202206
 JM1202203
 JM1201616
JM1201505
 JM1201431
JM1201265
 JM1201215
 JM1201218
JM1201118
JM1201122
 JM286179
JM1150997
JM1113749
 JM256003
 JM1146472
 JM1046460
JM552447
JM519855
 JM336481
JM1199694
 JM1188813
 JM1202342
 JM1188812
 JM1137739
 JM1030127
 JM550415
 JM550884
JM448537
 JM401847
 JM304435
JM572336
 JM620830
 JM1201215










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
